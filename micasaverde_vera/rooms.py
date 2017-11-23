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


from event import EventHandler


class Rooms(object):

    def __init__(self, parent, node):
        self._rooms = []
        self._parent = parent
        self.send = parent.send
        self._bindings = []

        if node is not None:
            for room in node:
                self._rooms += [Room(self, room)]

    def register_event(self, callback, attribute=None):
        self._bindings += [EventHandler(self, callback, None)]
        return self._bindings[-1]

    def unregister_event(self, event_handler):
        if event_handler in self._bindings:
            self._bindings.remove(event_handler)

    def get_room(self, number):
        number = str(number)
        if number.isdigit():
            number = int(number)

        for room in self._rooms:
            if number in (room.name, room.id):
                return room

    def get_section(self, number):
        return self._parent.get_section(number)

    def update_node(self, node, full=False):
        if node is not None:
            rooms = []
            for room in node:
                id = room['id']

                for found_room in self._rooms[:]:
                    if found_room.id == id:
                        found_room.update_node(room)
                        self._rooms.remove(found_room)
                        break
                else:
                    found_room = Room(self, room)

                    for event_handler in self._bindings:
                        event_handler('new', room=found_room)

                rooms += [found_room]

            if full:
                for room in self._rooms:
                    for event_handler in self._bindings:
                        event_handler('remove', room=room)

                del self._rooms[:]

            self._rooms += rooms


class Room(object):
    def __init__(self, parent, node):
        self._parent = parent
        self._bindings = []

        def get(attr):
            return node.pop(attr, None)

        self.id = get('id')
        self._section = get('section')
        self._name = get('name')

        for key, value in node.items():
            self.__dict__[key] = value

    def register_event(self, callback, attribute=None):
        self._bindings += [EventHandler(self, callback, attribute)]
        return self._bindings[-1]

    def unregister_event(self, event_handler):
        if event_handler in self._bindings:
            self._bindings.remove(event_handler)

    @property
    def section(self):
        return self._parent.get_section(self._section)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._parent.send(id='room', action='rename', room=self.id, name=name)

    def delete(self):
        self._parent.send(id='room', action='delete', room=self.id)

    def update_node(self, node):
        for key, value in node.items():
            if key == 'name':
                old_value = self._name
            elif key == 'section':
                old_value = self._section
            else:
                old_value = getattr(self, key, None)

            if old_value is None:
                for event_handler in self._bindings:
                    event_handler('new', room=self, attribute=key, value=value)
                setattr(self, key, value)

            elif old_value != value:
                for event_handler in self._bindings:
                    event_handler(
                        'changed',
                        room=self,
                        attribute=key,
                        value=value
                    )
                if key == 'name':
                    self._name = value
                elif key == 'section':
                    self._section = value
                else:
                    setattr(self, key, value)
