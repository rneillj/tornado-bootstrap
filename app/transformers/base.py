#!/usr/bin/env python
""" Base Transformer """

from app.config import config


class BaseTransformer(object):

    @staticmethod
    def transform_data(self, data, *args, **kwargs):
        """
        Abstract method. Must be implemented as a concrete method by the
        extending class.
        """
        raise NotImplementedError("This is an abstract method. It must be "
                                  "implemented as a concrete method in an "
                                  "inheriting class.")

    @staticmethod
    def transform_list(self, data_list, *args):
        """
        This method returns a list of transformed data objects.
        """
        return [self.transform_data(d, *args) for d in data_list]
