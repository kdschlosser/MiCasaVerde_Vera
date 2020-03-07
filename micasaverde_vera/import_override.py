# -*- coding: utf-8 -*-

# MIT License
#
# Copyright 2020 Kevin G. Schlosser
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""
This file is part of the **micasaverde_vera**
project https://github.com/kdschlosser/MiCasaVerde_Vera.

:platform: Unix, Windows, OSX
:license: MIT
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
