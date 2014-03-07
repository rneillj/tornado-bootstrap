#!/usr/bin/env python
""" This is the base class from which all logic classes should extend. """

import logging


log = logging.getLogger(__name__)


class BaseLogic(object):
        """
        This class should include any basic logic that may be specific to
        a resource, but not specific to any other classes to be implemented.
        For example, a method that checks if something is true or false.
        """
        pass
