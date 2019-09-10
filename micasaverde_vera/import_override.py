# -*- coding: utf-8 -*-

# **micasaverde_vera** is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# **micasaverde_vera** is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-openzwave. If not, see http://www.gnu.org/licenses.

"""
This file is part of the **micasaverde_vera**
project https://github.com/kdschlosser/MiCasaVerde_Vera.

:platform: Unix, Windows, OSX
:license: GPL(v3)
:synopsis: import wrapper

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

try:
    builtins = __import__('__builtin__')
except ImportError:
    builtins = __import__('builtins')

import threading
import sys
import os
import logging

from .vera_exception import VeraImportError
from .utils import CRC32_from_file, init_core
from .constants import CORE_PATH
from . import utils


logger = logging.getLogger(__name__)


class ImportOverride(object):
    _import = builtins.__import__

    def __init__(self, parent):
        self._parent = parent
        self._rebuilding = threading.Event()
        self._rebuilding.set()
        self._import_errors = []

    @utils.logit
    def start(self):
        builtins.__import__ = self

    @utils.logit
    def stop(self):
        builtins.__import__ = self._import

    # noinspection PyDefaultArgument, PyShadowingBuiltins
    def __call__(self, name, globals={}, locals={}, fromlist=(), level=-1):
        if 'micasaverde_vera.core' in name:
            if name in sys.modules:
                return sys.modules[name]
            try:
                self._rebuilding.wait()

                file_type, mod_name = name.split('.')[-2:]
                core = sys.modules['micasaverde_vera.core']
                crc_cls = getattr(core, file_type.title())
                crc = getattr(crc_cls, mod_name, None)
                import_file = (
                    os.path.join(CORE_PATH, file_type, mod_name + '.py')
                )

                if not os.path.exists(import_file) or crc is None:
                    raise ImportError

                if crc != CRC32_from_file(import_file):
                    if self._rebuilding.isSet():
                        if name in self._import_errors:
                            raise VeraImportError

                        self._import_errors += [name]
                        self._rebuilding.clear()

                        @utils.logit
                        def run():
                            logger.info(
                                'MiCasaVerde Vera: Generated file corruption.'
                            )
                            logger.info('                  Rebuilding files....')
                            self._parent.rebuild_files()
                            init_core()
                            self._rebuilding.set()

                        t = threading.Thread(target=run)
                        t.daemon = True
                        t.start()
                    raise VeraImportError

                mod = self._import(name, globals, locals, fromlist, level)

                if name in self._import_errors:
                    self._import_errors.remove(name)
                return mod

            except ImportError:
                if self._rebuilding.isSet():
                    if name in self._import_errors:
                        raise VeraImportError
                    self._import_errors += [name]
                    self._rebuilding.clear()

                    def run():
                        self._parent.update_files()
                        self._rebuilding.set()

                    t = threading.Thread(target=run)
                    t.daemon = True
                    t.start()
                raise VeraImportError
        else:
            return self._import(name, globals, locals, fromlist, level)
