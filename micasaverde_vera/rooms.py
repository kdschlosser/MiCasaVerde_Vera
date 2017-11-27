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

from devices import Device
from scenes import Scene
from installed_plugins import InstalledPlugin
from event import Notify

class Rooms(object):

    def __init__(self, parent, node):
        self._parent = parent
        self.send = parent.send
        self._rooms = [Room(self, dict(id=0, name='No Room', section=1))]

        if node is not None:
            for room in node:
                self._rooms += [Room(self, room)]

    def new(self, name):
        self._parent.send(
            id='room',
            action='create',
            name=name
        )

    @property
    def devices(self):
        return self._parent.devices

    @property
    def plugins(self):
        return self._parent.installed_plugins

    @property
    def scenes(self):
        return self._parent.scenes

    def get_room(self, room):
        room = str(room)
        if room.isdigit():
            room = int(room)

        for r in self._rooms:
            if room in (r.name, r.id):
                return r

    def get_section(self, section):
        return self._parent.get_section(section)

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

                rooms += [found_room]

            if full:
                for room in self._rooms:
                    Notify(room, 'Room.{0}.Removed'.format(room.id))
                del self._rooms[:]

            self._rooms += rooms


class Room(object):
    def __init__(self, parent, node):
        self._parent = parent

        def get(attr):
            return node.pop(attr, None)

        self.id = get('id')
        self._section = get('section')
        self._name = get('name')

        for key, value in node.items():
            self.__dict__[key] = value

        Notify(self, 'Room.{0}.Created'.format(self.id))

    @property
    def section(self):
        return self._parent.get_section(self._section)

    def remove(self, item):
        item = self._locate_item(item)

        if item is not None and item.room == self:
            item.room = 0

    def remove_plugin(self, plugin):
        self.remove(self._parent.plugins.get_plugin(plugin))

    def remove_scene(self, scene):
        self.remove(self._parent.scenes.get_scene(scene))

    def remove_device(self, device):
        self.remove(self._parent.devices.get_device(device))

    def add(self, item):
        item = self._locate_item(item)

        if item is not None and item.room != self:
            item.room = self

    def add_plugin(self, plugin):
        self.add(self._parent.plugins.get_plugin(plugin))

    def add_scene(self, scene):
        self.add(self._parent.scenes.get_scene(scene))

    def add_device(self, device):
        self.add(self._parent.devices.get_device(device))

    def _locate_item(self, item):
        if not isinstance(item, (Device, Scene, InstalledPlugin)):
            found_item = self._parent.devices.get_device(item)
            if found_item is None:
                found_item = self._parent.plugins.get_plugin(item)
            if found_item is None:
                found_item = self._parent.scenes.get_scene(item)
            item = found_item
        return item

    def __radd__(self, item):
        item = self._locate_item(item)

        if item is not None and item.room != self:
            item.room = self

    def __rsub__(self, item):
        item = self._locate_item(item)

        if item is not None and item.room == self:
            item.room = 0

    def __contains__(self, item):
        item = self._locate_item(item)

        if item is not None and item.room == self:
            return True

        return False

    def __iter__(self):
        return iter(self.devices + self.plugins + self.scenes)

    @property
    def devices(self):
        res = []

        for device in self._parent.devices:
            try:
                if device.room == self:
                    res += device
            except AttributeError:
                pass
        return res

    @property
    def scenes(self):
        return list(
            scene for scene in self._parent.scenes
            if scene.room == self
        )

    @property
    def plugins(self):
        return list(
            plugin for plugin in self._parent.installed_plugins
            if plugin.room == self
        )

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if self.id:
            self._parent.send(
                id='room',
                action='rename',
                room=self.id,
                name=name
            )

    def delete(self):
        if self.id:
            self._parent.send(
                id='room',
                action='delete',
                room=self.id
            )

    def update_node(self, node):
        for key, value in node.items():
            if key == 'name':
                old_value = self._name
            elif key == 'section':
                old_value = self._section
            else:
                old_value = getattr(self, key, None)

            if old_value != value:
                if key == 'name':
                    self._name = value
                elif key == 'section':
                    self._section = value
                else:
                    setattr(self, key, value)

                Notify(self, 'Room.{0}.{1}.Changed'.format(self.id, key))
