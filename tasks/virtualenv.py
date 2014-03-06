#!/usr/bin/env python

import os
import shutil
import sys

from paver.easy import task, needs, Bunch, options, call_task, sh, cmdopts

# default options
options(
    root_dir=".",
    bootstrap=Bunch(bootstrap_dir="."),
    virtualenv=Bunch()
)


@task
@cmdopts([('root_dir=', 'd', 'location of virtualenv to destroy')])
def destroy_virtualenv(options):
    """ destroy virtual environment """

    for d in ['build', 'dist', 'bin', 'include', 'lib',
              'vcenter_api.egg-info']:
        directory = os.path.join(options.root_dir, d)
        if os.path.exists(directory):
            shutil.rmtree(directory)

    for f in ['bootstrap.py', '.Python']:
        directory = os.path.join(options.root_dir, f)
        if os.path.exists(directory):
            os.remove(f)


@task
@cmdopts([('root_dir=', 'd', 'where to deploy virtualenv')],
         share_with=['destroy_virtualenv'])
@needs('destroy_virtualenv')
def create_virtualenv(options):
    """ create virtual environment """

    try:
        import virtualenv
    except ImportError as e:
        raise RuntimeError("virtualenv is needed for bootstrap")

    options.virtualenv.dest_dir = options.root_dir
    options.virtualenv.no_site_packages = True
    options.virtualenv.paver_command_line = "develop"
    call_task('paver.virtual.bootstrap')
    sh('%s %s' % (sys.executable, 'bootstrap.py'))
