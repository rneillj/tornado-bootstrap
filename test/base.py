#!/usr/bin/env python

import logging
import time
import os

from mock import MagicMock
from mock import patch

from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from app.lib.route import get_routes
from app.config import config


log = logging.getLogger(__name__)


class BaseTest(AsyncHTTPTestCase):
    """ Base class for all functional tests """

    def wait_until_active(self, t=30):
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


class AsyncPatch(object):
    """ Context managed patch setup and teardown. """

    def __init__(self, patch_data):
        self.patch_data = patch_data
        self.patch_objects = self.create_patches()

    def __enter__(self):
        """
        Starts all patched objects using 'with' context management.
        Does not return anything for 'as' keyword.
        """
        for patch in self.patch_objects:
            patch.start()

    def __exit__(self, *args):
        """
        Stops all patched objects using 'with' context management.
        No error checking or stack trace evaluation occurs at the
        moment.
        """
        for patch in self.patch_objects:
            patch.stop()

    def create_patches(self):
        """
        Patches methods from classes for mock client calls.
        Accepts a list of dictionaries that include the
        following keys:

            class - Class object to be mocked.

            method - Method name as a string.

            mock_params - Keyword arguments to be passed
                          to AsyncMagicMock.
        """
        patches = []
        for d in self.patch_data:
            patches.append(
                patch.object(
                    d['class'],
                    d['method'],
                    new=AsyncMagicMock(**d.get('mock_params', {}))
                )
            )
        return patches


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
