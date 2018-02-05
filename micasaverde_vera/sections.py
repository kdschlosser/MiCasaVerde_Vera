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

import threading
from event import Notify


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
