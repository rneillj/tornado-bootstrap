#!/usr/bin/env python

import logging
import os
import re

import tornado.web

from app.lib.autoload import autoload
from pkg_resources import resource_filename


log = logging.getLogger(__name__)


class route(object):
    """
    Decorates RequestHandlers, and builds up a list of
    routable handlers
    """

    _routes = []

    def __init__(self, uri, name=None, module=None):
        self._uri = re.sub(r'{[a-z_]*}', u'([\w_\-]+)', uri) + '/?'
        self.name = name or uri
        self.module = module

    def __call__(self, _handler):
        log.info("Using {0} for {1}".format(_handler.__name__, self._uri))
        r = tornado.web.url(self._uri, _handler, name=self.name)
        r.module = self.module
        self._routes.append(r)
        return _handler

    @classmethod
    def _get_routes(cls):
        """ Return a list of routes so tornado can listen for them """
        return cls._routes


def get_routes(root, handler_path):
    """ Set up all the routes, both the Javascript and API routes """

    autoload(resource_filename(handler_path, "handlers"))
    routes = route._get_routes()

    routes.append((r'/v1/docs/?', tornado.web.RedirectHandler,
                  {'url': '/v1/docs/index.html'}))
    routes.append((r'/v1/docs/(.*)', tornado.web.StaticFileHandler,
                  {'path': "docs"}))

    return routes
