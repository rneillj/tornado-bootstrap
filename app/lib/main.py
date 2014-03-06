#!/usr/bin/env python

import logging
import os

import tornado.httpserver
import tornado.web
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler

from app.lib.log import configure_logging
from app.lib.route import get_routes

from app.config import config
from optparse import OptionParser

log = logging.getLogger(__name__)


def command_line_options():
    """ command line configuration """

    parser = OptionParser(usage="usage: %prog [options] <config_file>")

    parser.add_option('-d', '--debug',
                      action="store_true",
                      dest="debug",
                      default=False,
                      help="Start the application in debugging mode.")

    parser.add_option('-p', '--port',
                      action="store",
                      dest="port",
                      default=3000,
                      help="Set the port to listen to on startup.")

    parser.add_option('-a', '--address',
                      action="store",
                      dest="address",
                      default=None,
                      help="Set the address to listen to on startup. Can be a "
                      "hostname or an IPv4/v6 address.")

    parser.add_option('-m', '--mock',
                      action="store_true",
                      dest="mock",
                      default=False,
                      help="Only use Mock (fake) data")

    parser.add_option('-l', '--level',
                      choices=['DEBUG',
                               'INFO',
                               'WARNING',
                               'ERROR',
                               'CRITICAL'],
                      dest="log_level",
                      default='DEBUG',
                      help="Set the log level. Logging messages which are "
                           "less severe than the specified level will not "
                           "be logged.")

    options, args = parser.parse_args()

    if len(args) >= 1:
        config.load_file(args[0])

    return options


def main(handler_path="app"):
    """ entry point for the application """

    root = os.path.dirname(__file__)

    # get the command line options
    options = command_line_options()

    log = configure_logging(options.log_level)

    # setup the application
    log.info("Starting the application")
    application = tornado.web.Application(
        get_routes(root, handler_path),
        debug=options.debug
    )

    if(options.mock):
        set_mock_data()

    # start the ioloop
    log.info("Starting the application on port %d" % (options.port))
    application.listen(options.port, options.address)
    IOLoop.instance().start()
