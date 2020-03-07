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
:synopsis: sections

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

import logging
import threading
from .event import Notify
from . import utils

logger = logging.getLogger(__name__)


class Sections(object):

    def __init__(self, parent, node):
        self.__lock = threading.RLock()
        self._parent = parent
        self.send = parent.send
        self._sections = []

        if node is not None:
            for section in node:
                self._sections += [Section(self, section)]

    def __iter__(self):
        with self.__lock:
            for section in self._sections:
                yield section

    def __getattr__(self, item):
        with self.__lock:
            if item in self.__dict__:
                return self.__dict__[item]

            try:
                return self[item]
            except (IndexError, KeyError):
                raise AttributeError

    def __getitem__(self, item):
        with self.__lock:
            item = str(item)
            if item.isdigit():
                item = int(item)

            for section in self._sections:
                name = getattr(section, 'name', None)
                if name is not None and name.replace(' ', '_').lower() == item:
                    return section
                if item in (section.id, section.name):
                    return section

            if isinstance(item, int):
                raise IndexError

            raise KeyError

    @utils.logit
    def update_node(self, node, full=False):
        with self.__lock:
            if node is not None:
                sections = []

                for section in node:
                    # noinspection PyShadowingBuiltins
                    id = section['id']
                    for found_section in self._sections[:]:
                        if found_section.id == id:
                            self._sections.remove(found_section)
                            break
                    else:
                        found_section = Section(self, section)

                    sections += [found_section]

                if full:
                    for section in self._sections:
                        Notify(section, section.build_event() + '.removed')
                    del self._sections[:]

                self._sections += sections


class Section(object):

    def __init__(self, parent, node):
        self._parent = parent

        self.id = node.pop('id', None)
        self.name = node.pop('name', None)

        for key, value in node.items():
            self.__dict__[key] = value

        Notify(self, self.build_event() + '.created')

    def build_event(self):
        return 'sections.{0}'.format(self.id)
