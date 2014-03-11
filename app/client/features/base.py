#!/usr/bin/env python


class BaseFeature(object):

    def __init__(self, client, next_feature, *args, **kwargs):
        self.client = client
        self.next_feature = next_feature
        self.args = args
        self.kwargs = kwargs
