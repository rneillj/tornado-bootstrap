#!/usr/bin/env python

import json

from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest

from app.config import config
from app.lib.timer import timer


class ComposureClient(object):

    def __init__(self, *args):
        self.features = args

        self.headers = {}

    def get(self, endpoint, callback):
        self.call("GET", endpoint, None, callback)

    def put(self, endpoint, body, callback):
        self.call("PUT", endpoint, body, callback)

    def post(self, endpoint, body, callback):
        self.call("POST", endpoint, body, callback)

    def delete(self, endpoint, callback):
        self.call("DELETE", endpoint, None, callback)

    @gen.engine
    def call(self, method, endpoint, body, callback):
        request = self.setup_request(method, endpoint, body)

        onion = self.make_call
        for feature in self.features:

            if(isinstance(feature, tuple)):
                actual_feature = feature[0]
                kwargs = {}
                for arg in feature:
                    if isinstance(arg, tuple):
                        kwargs[arg[0]] = arg[1]
                onion = actual_feature(self, onion, **kwargs)
            else:
                onion = feature(self, onion)

        response = yield gen.Task(onion, request)

        callback(response)

    @gen.engine
    def make_call(self, request, callback):
        message = "{0} {1} ".format(request.method, request.url)
        with timer(message + "took {0:0.2f} ms"):
            response = yield gen.Task(AsyncHTTPClient(max_clients=1000).fetch,
                                      request)
        body = response.body
        if response.body is not None:
            body = response.body.decode('utf-8')
        callback(CustomResponse(response.code, body))

    def setup_request(self, method, endpoint, body):
        request_options = {
            "url": endpoint,
            "method": method,
            "headers": self.headers,
            "request_timeout": 60,
            "validate_cert": False
        }

        if body is not None and body != "":
            request_options["body"] = json.dumps(body)
        request = HTTPRequest(**request_options)

        return request


class CustomResponse(object):

    def __init__(self, code, body):
        self._code = code
        self._body = body

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = value

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = value
