#!/usr/bin/env python

import os
import pkgutil


def autoload(dirname):
    """ autoload all modules in a directory """

    for path, directories, files in os.walk(dirname):
        for importer, package_name, _ in pkgutil.iter_modules([path]):
            # Supposedly, this means the module is already loaded, but that is
            # not the case for tests. It shouldn't hurt to reload them anyways.
            # if package_name not in sys.modules or True:
            importer.find_module(package_name).load_module(package_name)
