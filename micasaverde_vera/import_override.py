# -*- coding: utf-8 -*-
#
# This file is part of EventGhost.
# Copyright © 2005-2016 EventGhost Project <http://www.eventghost.net/>
#
# EventGhost is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# EventGhost is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with EventGhost. If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function
try:
    builtins = __import__('__builtin__')
except ImportError:
    builtins = __import__('builtins')

import threading
import sys
import os
from vera_exception import VeraImportError
from utils import CRC32_from_file, init_core
from constants import CORE_PATH


class ImportOverride(object):
    _import = builtins.__import__

    def __init__(self, parent):
        self._parent = parent
        self._rebuilding = threading.Event()
        self._rebuilding.set()

    def start(self):
        builtins.__import__ = self

    def stop(self):
        builtins.__import__ = self._import

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
                        self._rebuilding.clear()

                        def run():
                            print(
                                'MiCasaVerde Vera: Generated file corruption.'
                            )
                            print('                  Rebuilding files....')
                            self._parent.rebuild_files()
                            init_core()
                            self._rebuilding.set()

                        t = threading.Thread(target=run)
                        t.daemon = True
                        t.start()
                    raise VeraImportError

                return self._import(name, globals, locals, fromlist, level)

            except ImportError:
                if self._rebuilding.isSet():
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
