#!/usr/bin/env python
""" This is where we will house docs, healthchecks and other misc pieces """

import logging

from app.handlers.base import BaseHandler, no_auth
from app.lib.swagger import api_docs, list_modules
from app.lib.route import route


log = logging.getLogger(__name__)


@route(r'/v1/healthcheck')
@no_auth
class HealthCheckHandler(BaseHandler):

    def get(self):
        """
        This is a dummy health check.
        This should always return a 200 OK, as it doesn't doesn't
        do anything except write out a string.
        """
        self.write("I am alive. Thanks for checking.")


@route(r'/v1/docs/index')
@no_auth
class DocumentationHandler(BaseHandler):

    def get(self):
        #
        #     This provides a json view of our documentation.
        #
        #     Its used by swagger: https://github.com/wordnik/swagger-ui. This
        #     only provides a service list, which swagger uses to fetch all of
        #     the details. See /api/docs/index/{route} for the specifics
        #
        #
        self.add_header('Access-Control-Allow-Origin', '*')
        self.write({
            "apiVersion": "1.0",
            "swaggerVersion": "1.2",
            "apis": list_modules(route._get_routes()),

        })


@route(r'/v1/docs/index/{route}')
@no_auth
class DocumentationHandler(BaseHandler):
    def get(self, module):
        #
        #     This provides all of the docs for a given module
        #
        if(module == "everything_else"):
            module = None
        self.add_header('Access-Control-Allow-Origin', '*')
        self.write(api_docs(route._get_routes(), module))
