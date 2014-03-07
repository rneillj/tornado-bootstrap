#!/usr/bin/env python
""" This is the base class from which all services should extend. """

import logging

from tornado import gen

from app.config import config


log = logging.getLogger(__name__)


class BaseService(object):
    """
    This class exists to provide a base class for all services. It is
    an aggregation layer that the handler calls which makes calls out
    to other objects, such as validators or resources. The base class
    should only include methods that should exist in the scope of all
    services.
    """
