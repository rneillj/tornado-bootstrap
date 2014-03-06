#!/usr/bin/env python
"""
    This directory contains a bunch of yaml files. These yaml files define the
    requirements for incoming data. For example, the login_schema will ensure
    that the json body includes a username, and makes sure that username is a
    string. It also ensures there is a password, and makes sure it is a string
    as well. If the json payload contains any other field, it will not be valid
"""

import logging
import os
import yaml

from tornado.web import HTTPError

from pkg_resources import resource_filename
from cerberus import Validator


log = logging.getLogger(__name__)


def validator(schema):
    """ This loads the schema and wraps the method with the validate func """

    file_path = os.path.join(
        resource_filename('app', 'data'),
        '{0}.yaml'.format(schema)
    )

    validator_schema = yaml.load(open(file_path, 'r'))

    def validate(func):
        """ This is the wrapper function we call on initialization """

        def _handler(self, *args, **kwds):

            v = Validator(validator_schema)
            if self.params is None:
                raise HTTPError(400, 'This request requires a body.')
            if not v.validate(self.params):
                errors = [
                    '{0} ({1})'.format(k, v) for k, v in v.errors.iteritems()
                ]
                raise HTTPError(400, ', '.join(errors))
            return func(self, *args, **kwds)

        # These set some things for auto-documentation
        setattr(_handler, "__doc__", func.__doc__)
        setattr(_handler, "validator_schema",  validator_schema)
        setattr(_handler, "schema_name",  schema)
        return _handler

    return validate
