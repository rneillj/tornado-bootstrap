#!/usr/bin/env python
""" Testing Task """

import os
import sys
import logging
import unittest

from paver.easy import task, cmdopts, path

from app.config import config


@task
@cmdopts([
    ('mock', 'm', 'Use mocked data'),
    ('verbose', 'v', 'Verbose output'),
    ('quiet', 'q', 'Minimal output'),
    ('failfast', 'f', 'Stop on first failure'),
    ('start_location=',
     's',
     'Directory (or module path) to start discovery ("test" default)'),
])
def test(options):
    """ Run the functional and unit tests """
    install_dependencies(options.setup)

    logging.basicConfig(
        file=sys.stdout,
        level=logging.ERROR,
        format="%(asctime)s %(levelname)s "
               "[%(filename)s:%(lineno)d] %(message)s"
    )

    # Build the config for anything that consumes the variables
    config.load_file("ops/config.yaml")

    test_options = dict(getattr(options, 'test', {}))
    start_location = test_options.pop('start_location', 'test')
    module = 'test*.py'

    if test_options.pop('quiet', False):
        test_options['verbosity'] = 0

    if test_options.pop('verbose', False):
        test_options['verbosity'] = 2

    if test_options.pop('mock', False):
        print("Using Mocked data")

    runner = unittest.TextTestRunner(**test_options)

    if ".py" in start_location:
        location = start_location.split("/")
        start_location = "/".join(location[:-1])
        module = location[-1]

    suite = unittest.defaultTestLoader.discover(start_location, module)

    if not runner.run(suite).wasSuccessful():
        raise SystemExit(False)


@task
def coverage(options):
    """ Run a test coverage report against the application """
    install_dependencies(options.setup)
    build_dist()
    run_coverage('report', show_missing=False)


@task
def html_coverage(options):
    """
    Run an html test coverage report, putting the results into dist/cov_html
    """
    install_dependencies(options.setup)
    build_dist()
    run_coverage('html_report', directory='dist/cov_html')


def build_dist():
    """ Create the dist directory if it doesn't already exist """

    dist = path('dist')

    if dist.exists():
        return

    os.mkdir(dist)


def run_coverage(report_method, **kwargs):
    """ Run a coverage method against the test suite """

    from coverage import coverage as _coverage

    # Exclude third-party modules from coverage calculations.
    files = list(path('app').walkfiles('*.py'))

    # start the coverage recording
    c = _coverage(source=files)
    c.start()
    test()

    # create the report
    c.stop()
    getattr(c, report_method)(include=files, **kwargs)
    c.erase()


def install_dependencies(setup):
    from setuptools import dist
    distribution = dist.Distribution(attrs=setup)
    distribution.fetch_build_eggs(setup.install_requires)


__all__ = [
    'test',
    'coverage',
    'html_coverage'
]
