#!/usr/bin/env python

import sys
import logging
import time
import os

from mock import MagicMock

from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from app.lib.mock import set_mock_data
from app.lib.route import get_routes
from app.config import config


log = logging.getLogger(__name__)


class BaseTest(AsyncHTTPTestCase):
    """ Base class for all functional tests """

    def wait_until_active(self, t=30):
        if 'mock_data' in config:
            return
        else:
            time.sleep(t)

    def setUp(self):
        super(BaseTest, self).setUp()
        self.test_token = "{0}".format(config['test_token'])

    def get_method(self, url):
        return self.fetch(
            url,
            method="GET",
            headers={
                "Content-Type": "application/json",
                "X-Auth-Token": self.test_token
            }
        )

    def fetch(self, path, **kwargs):
        response = AsyncHTTPTestCase.fetch(self, path, **kwargs)
        if response.body is not None:
            response.value = response.body.decode('utf-8')
        return response

    def get_app(self):
        # setup the application
        log.info("Starting the application")
        routes = get_routes(os.path.dirname(__file__), "app")

        app = Application(routes)

        return app

    @classmethod
    def setUpClass(cls):
        # call the superclass version of this
        super(BaseTest, cls).setUpClass()
        config.load_file('ops/config.yaml')
        if("-m" in sys.argv or "--mock" in sys.argv):
            set_mock_data()


class AsyncMagicMock(MagicMock):
    """ This is for using MagicMock with gen.Task in Tornado """

    def __call__(self, *args, **kwargs):
        """
            Handle this MagicMock as a normal MagicMock unless an Async
                (gen.Task) calls it asking for a callback to happen
        """
        # Call the super class and get the results, pickup after this
        # pylint: disable=E1003
        results = super(MagicMock, self).__call__(*args, **kwargs)

        # gen.Task call
        if "callback" in kwargs:
            kwargs["callback"](results)
        # Standard call
        else:
            return results
