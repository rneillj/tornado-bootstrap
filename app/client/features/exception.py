#!/usr/bin/env python

import json

from tornado import gen
from tornado.web import HTTPError

from app.client.features.base import BaseFeature


class ExceptionFeature(BaseFeature):

    @gen.engine
    def __call__(self, request, callback):
        response = yield gen.Task(self.next_feature, request)
        if response.code == 500:
            raise HTTPError(503, "Service Unavailable")
        elif response.code > 299 and response.code != 500:
            parsed_response = yield gen.Task(
                self.__parse_response,
                response.body
            )
            raise HTTPError(response.code, parsed_response)

        callback(response)

    @gen.engine
    def __parse_response(self, response, callback):
        try:
            data = json.loads(response)
            if 'error' in data and 'message' in data['error']:
                response = data['error']['message']
            if 'error' in data and isinstance(data['error'], (str, unicode)):
                response = data['error']
        except:
            pass

        callback(response)
