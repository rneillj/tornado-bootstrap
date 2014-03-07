#!/usr/bin/env python
""" This is the base class from which all resources should extend. """

import logging

from tornado import gen

from app.client.base import ComposureClient
from app.client.exception import ExceptionFeature
from app.client.json_parsing import JsonFeature

from app.config import config


log = logging.getLogger(__name__)


class BaseResource(object):

    @staticmethod
    def init_client(*features):
        """
        This method initializes a client to make an outgoing call to
        a resource. It takes a list of features as an argument, maps
        each feature to its class, and instantiates a client with
        those features.
        """

        feature_mapping = {
            'exception': ExceptionFeature,
            'json': JsonFeature
        }

        features = [feature_mapping.get(key) for key in args
                    if feature_mapping.get(key)]

        return ComposureClient(*features)

    @staticmethod
    @gen.coroutine
    def list(self):
        """
        This method makes a call to get a list of the specified resources.
        It calls an abstract method of the same name.
        """
        response = yield gen.Task(self._list)
        return response

    @staticmethod
    @gen.coroutine
    def get(self):
        """
        This method makes a call to get the details of a specified resource.
        It calls an abstract method of the same name.
        """
        response = yield gen.Task(self._get)
        return response

    @staticmethod
    @gen.coroutine
    def put(self, resource, data):
        """
        This method makes a call to update the details of a specified resource.
        It calls an abstract method of the same name.
        """
        response = yield gen.Task(self._put, obj, data)
        return response

    @staticmethod
    @gen.coroutine
    def post(self, resource, data):
        """
        This method makes a call to create or append to a specified resource.
        It calls an abstract method of the same name.
        """
        response = yield gen.Task(self._post, obj, data)
        return response

    @staticmethod
    @gen.coroutine
    def delete(self, resource):
        """
        This method makes a call to delete a specified resource.
        It calls an abstract method of the same name.
        """
        response = yield gen.Task(self._delete, obj)
        return response

    @staticmethod
    @gen.coroutine
    def _list(self):
        raise NotImplementedError("This method is an abstract method to be "
                                  "implemented in an inheriting class.")

    @staticmethod
    @gen.coroutine
    def _get(self):
        raise NotImplementedError("This method is an abstract method to be "
                                  "implemented in an inheriting class.")
    @staticmethod
    @gen.coroutine
    def _put(self, resource, data):
        raise NotImplementedError("This method is an abstract method to be "
                                  "implemented in an inheriting class.")
    @staticmethod
    @gen.coroutine
    def _post(self, resource, data):
        raise NotImplementedError("This method is an abstract method to be "
                                  "implemented in an inheriting class.")
    @staticmethod
    @gen.coroutine
    def _delete(self, resource):
        raise NotImplementedError("This method is an abstract method to be "
                                  "implemented in an inheriting class.")
