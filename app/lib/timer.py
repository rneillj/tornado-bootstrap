#!/usr/bin/env python

import logging

import time

log = logging.getLogger(__name__)


class timer(object):

    def __init__(self, msg):
        self.msg = msg

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        total = (time.time() - self.start_time) * 1000
        log.info(self.msg.format(total))
