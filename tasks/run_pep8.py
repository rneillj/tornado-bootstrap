#!/usr/bin/env python

from paver.easy import task, sh


@task
def run_pep8(options):
    """ run pep8 against codebase """

    sh('%s %s' % ('pep8', 'app/*.py'))
    sh('%s %s' % ('pep8', 'tasks/*.py'))
    sh('%s %s' % ('pep8', 'pavement.py'))
