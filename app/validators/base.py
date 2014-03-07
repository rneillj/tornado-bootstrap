#!/usr/bin/env python
""" Base Validator """

import logging

from tornado import gen
from tornado.web import HTTPError

from app.logic.base import BaseLogic


log = logging.getLogger(__name__)


class BaseValidator(object):
    """
    Methods that will validate data being passed to a resource
    should be implemented here. Also, any custom error messages
    are generally included in these methods to allow for more
    effective debugging.
    """
