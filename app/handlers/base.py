#!/usr/bin/env python
""" This is the base class from which all handlers should extend """

import logging
import json

from tornado import gen
from tornado.web import HTTPError
from tornado.web import RequestHandler

from app.config import config


log = logging.getLogger(__name__)


class BaseHandler(RequestHandler):
    """
    This handles all of the setup of our requests.

    self.params: This is set to a dictionary representation of the parsed
                 json body received.
    """

    @gen.coroutine
    def prepare(self):
        """ Ensure the request is well formed json. """
        self.params = self.parse_request()

    def parse_request(self):
        content_type = self.request.headers.get(
            "Content-Type", 'application/json')

        if self.request.body in [None, b"", ""]:
            return

        if content_type.startswith("application/json"):
            try:
                return json.loads(self.request.body.decode('utf-8'))
            except Exception:
                raise HTTPError(400, "Bad Request. Could not parse JSON")
        else:
            # Content type is something other than application/json
            raise HTTPError(415, "Unsupported Media Type")

        return {}

    def write_error(self, status_code, **kwargs):
        if 'exc_info' in kwargs:
            exception = kwargs['exc_info'][1]
            if 'log_message' in dir(exception):
                if exception.log_message:
                    msg = exception.log_message
                else:
                    msg = str(exception)
            else:
                msg = repr(exception)
            self.write({"msg": msg})
            self.finish()
        else:
            super(BaseHandler, self).write_error(status_code, **kwargs)

    def write(self, chunk):
        """ Make sure we only write json and ensure content-type is correct """
        if isinstance(chunk, dict):
            chunk = json.dumps(chunk)
            self.set_header("Content-Type", "application/json; charset=UTF-8")

        super(BaseHandler, self).write(chunk)


def no_auth(func):
    func.no_auth = True
    return func
