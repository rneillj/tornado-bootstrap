#!/usr/bin/env python
""" This is the base class from which all resources should extend """

import logging

from tornado import gen

from app.client.base import ComposureClient
from app.client.exception import ExceptionFeature
from app.client.json_parsing import JsonFeature

from app.config import config


log = logging.getLogger(__name__)


@gen.engine
def repeat(func, url, body, limit=50, offset=0, callback=None):
    data = []
    base_url = url

    count = 0
    while(limit >= 50):
        if func.func_name == 'post' and count != 0:
            offset = offset + limit  # next page
            url = base_url + '?offset={0}'.format(offset)

        count = count + 1
        result = yield gen.Task(func, url, body)  # always wrapped in a list
        result = result.body
        limit = len(result.get('results', []))  # results we got back

        data.extend(result.get('results', []))
        if not config['feature_toggle']['future_api']:
            break

    callback({"results": data})


class BaseResource(object):

    endpoint = config['device_service']['endpoint']
    if config['feature_toggle']['future_api'] is True:
        endpoint = config['device_service']['future_endpoint']
    client_features = ['exception', 'json', 'auth']

    @staticmethod
    def get_client(*args):
        feature_mapping = {
            'exception': ExceptionFeature,
            'json': JsonFeature
        }

        features = [feature_mapping.get(key) for key in args
                    if feature_mapping.get(key)]

        return ComposureClient(*features)

    @staticmethod
    def get_body(account_number):
        """
        This abstract method needs to be implemented in every
        inheriting DAO to pass a body to the list call in this
        class.
        """
        raise NotImplementedError("This is an abstract method. It must be "
                                  "implemented as a concrete method in an "
                                  "inheriting class.")

    @staticmethod
    def get_parent_body(device_id, children_attribute):
        """ General body for searching for a device's parent """
        body = {
            children_attribute: {"$in": [device_id]}
        }

        return body

    @classmethod
    @gen.engine
    def list(cls, account_number, callback):
        client = BaseResource.get_client(*BaseResource.client_features)
        url = "%s/search" % (BaseResource.endpoint)
        if account_number and isinstance(account_number, int):
            account_number = str(account_number)
        response = yield gen.Task(
            repeat,
            client.post,
            url,
            cls.get_body(account_number)
        )
        callback(response['results'])

    @staticmethod
    @gen.engine
    def get(device_id, callback):
        client = BaseResource.get_client(*BaseResource.client_features)
        url = "%s/devices/%s" % (BaseResource.endpoint, device_id)
        response = yield gen.Task(client.get, url)
        callback(response.body['device'])

    @classmethod
    @gen.engine
    def get_parents(cls, device_id, children_attribute, callback):
        """
            children_attribute is the Parent's child attribute,
            for example "vms" on hypervisors
        """
        client = BaseResource.get_client(*BaseResource.client_features)
        url = "%s/search" % (BaseResource.endpoint)

        response = yield gen.Task(
            repeat,
            client.post,
            url,
            cls.get_parent_body(device_id, children_attribute)
        )

        callback(response['results'])
