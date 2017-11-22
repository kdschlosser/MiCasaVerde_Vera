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

"""
<sections>
    <section id="1" name="My Home"></section>
</sections>
"""

from event import EventHandler


class Sections(object):

    def __init__(self, parent, node):
        self._parent = parent
        self.send = parent.send
        self._sections = []
        self._bindings = []

        if node is not None:
            for section in node:
                self._sections += [Section(self, section)]

    def register_event(self, callback, attribute=None):
        self._bindings += [EventHandler(self, callback, None)]
        return self._bindings[-1]

    def unregister_event(self, event_handler):
        if event_handler in self._bindings:
            self._bindings.remove(event_handler)

    def get_section(self, number):
        number = str(number)

        if number.isdigit():
            number = int(number)

        for section in self._sections:
            if number in (section.name, section.id):
                return section

    def update_node(self, node, full=False):
        if node is not None:
            sections = []

            for section in node:
                id = section['id']
                for found_section in self._sections[:]:
                    if found_section.id == id:
                        self._sections.remove(found_section)
                        break
                else:
                    found_section = Section(self, section)

                    for event_handler in self._bindings:
                        event_handler('new', section=found_section)

                sections += [found_section]

            if full:
                for section in self._sections:
                    for event_handler in self._bindings:
                        event_handler('remove', section=section)

                del self._sections[:]


            self._sections += sections


class Section(object):

    def __init__(self, parent, node):
        self._parent = parent

        for key, value in node.items():
            self.__dict__[key] = value
