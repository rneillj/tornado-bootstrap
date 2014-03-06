#!/usr/bin/env python

import logging
import sys


def configure_logging(log_level):
    """ setup application logging """

    log = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    f = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    handler.setFormatter(logging.Formatter(f))
    log.addHandler(handler)
    log.setLevel(log_level)

    return log
