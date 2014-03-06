#!/usr/bin/env python
""" This is the base class from which all services should extend """

import logging

from tornado import gen

from app.config import config
from app.dao.devices import DeviceDAO


log = logging.getLogger(__name__)


class BaseService(object):

    @staticmethod
    def _get_dao():
        """
        This abstract method needs to be implemented in every
        inheriting Serivce to pass back the specific DAO
        """
        raise NotImplementedError(
            "This abstract method needs to be implemented in every"
            "inheriting Serivce to pass back the specific DAO")

    @staticmethod
    @gen.engine
    def _get_response_kwargs(devices, response, callback):
        """
        Fetching linked device details for the given parent device.
        """
        for k, v in devices.iteritems():
            tasks = []

            for child in response.get(k, []):
                id = child['id'] if isinstance(child, dict) else int(child)
                tasks.append(gen.Task(DeviceDAO.get, id))

            responses = yield tasks

            for r in responses:
                devices[k].append(r)
        callback(devices)

    """
    This method exists entirely to allow us to bridge the gap between
    current DS API and the future DS API.

    When the future version is back, we remove the if config* checks
    entirely.
    """
    @staticmethod
    @gen.engine
    def inject_account_details(service, response, account_number, callback):
        if not config['feature_toggle']['future_api']:
            for k, v in enumerate(response):
                response[k]['account_name'] = response[k]['accountName']
        else:
            accounts = yield gen.Task(service.get, account_number)
            accounts = accounts.get('accounts', {})

            for k, v in enumerate(response):
                i = str(v['customer_number'])
                response[k]['account_name'] = accounts.get(i, '')

        callback(response)

    @staticmethod
    @gen.engine
    def prepare_child_list(service, device_id, children, c_type, callback):
        device = yield gen.Task(service.get, device_id)
        device = device.popitem()[1]  # returns a tuple of (key, values)
        if c_type in device:
            existing = [c['id'] for c in device[c_type]]
            children = list(set(children + existing))

        callback(children)

    @classmethod
    @gen.engine
    def get_parents(
        cls,
        device_id,
        children_attribute,
        filter_to_device_types,
        callback
    ):
        """ Grab the parents """

        dao = cls._get_dao()

        response = yield gen.Task(
            dao.get_parents, device_id, children_attribute)

        if filter_to_device_types:
            response = [
                device for device in response
                if device["device_type"] in filter_to_device_types
            ]

        callback({"devices": response})
