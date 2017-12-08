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


from event import Notify


def _check_item_type(item):
    from installed_plugins import InstalledPlugin
    from scenes import Scene
    from devices import Device

    if isinstance(item, (InstalledPlugin, Scene, Device)):
        return item


class Rooms(object):

    def __init__(self, ha_gateway, node):
        self.ha_gateway = ha_gateway
        self.send = ha_gateway.send
        self._rooms = [Room(self, {'id': 0, 'name': 'No Room', 'section': 1})]

        if node is not None:
            for room in node:
                self._rooms += [Room(self, room)]

    def new(self, name):
        self._parent.send(
            id='room',
            action='create',
            name=name
        )

    def __iter__(self):
        for room in self._rooms:
            yield room

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        try:
            return self[item]
        except (KeyError, IndexError):
            raise AttributeError

    def __getitem__(self, item):
        item = str(item)
        if item.isdigit():
            item = int(item)

        for room in self._rooms:
            name = getattr(room, 'name', None)
            if name is not None and name.replace(' ', '_').lower() == item:
                return room
            if item in (room.id, room.name):
                return room
        if isinstance(item, int):
            raise IndexError

        raise KeyError

    def update_node(self, node, full=False):
        if node is not None:
            rooms = [self._rooms.pop(0)]
            for room in node:
                # noinspection PyShadowingBuiltins
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
                    Notify(room, room.build_event() + '.removed')
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

        Notify(self, self.build_event() + '.created')

    def build_event(self):
        return 'rooms.{0}'.format(self.id)

    @property
    def section(self):
        return self._parent.ha_gateway.sections[self._section]

    def remove(self, item):
        item = _check_item_type(item)

        if item is not None and item.room == self:
            item.room = 0

    def remove_plugin(self, plugin):
        self._plugin_room(plugin, 0)

    def remove_scene(self, scene):
        self._scene_room(scene, 0)

    def remove_device(self, device):
        self._device_room(device, 0)

    def add_plugin(self, plugin):
        self._plugin_room(plugin, self.id)

    def add_scene(self, scene):
        self._scene_room(scene, self.id)

    def add_device(self, device):
        self._device_room(device, self.id)

    def _plugin_room(self, plugin, room):
        from installed_plugins import InstalledPlugin
        if not isinstance(plugin, InstalledPlugin):
            plugin = self._parent.ha_gateway.installed_plugins[plugin]

        if getattr(plugin, 'room', None) is not None:
            plugin.room = room

    def _scene_room(self, scene, room):
        from scenes import Scene
        if not isinstance(scene, Scene):
            scene = self._parent.ha_gateway.scenes[scene]

        if getattr(scene, 'room', None) is not None:
            scene.room = room

    def _device_room(self, device, room):
        from devices import Device
        if not isinstance(device, Device):
            device = self._parent.ha_gateway.devices[device]

        if getattr(device, 'room', None) is not None:
            device.room = room

    def __radd__(self, item):
        item = _check_item_type(item)

        if item is not None:
            room = getattr(item, 'room', None)
            if room is not None and room != self:
                item.room = self

    def __rsub__(self, item):
        item = _check_item_type(item)

        if item is not None:
            if item in self:
                item.room = 0

    def __contains__(self, item):
        item = _check_item_type(item)

        if item is not None:
            room = getattr(item, 'room', None)
            if room == self:
                return True

        return False

    def __iter__(self):
        return iter(self.devices + self.plugins + self.scenes)

    def __getattr__(self, item):
        from micasaverde_vera.installed_plugins import InstalledPlugin

        if item in self.__dict__:
            return self.__dict__[item]

        for device in self:
            if isinstance(device, InstalledPlugin):
                name = getattr(device, 'Title', None)
            else:
                name = getattr(device, 'name', None)

            if name is not None and name.replace(' ', '_').lower() == item:
                return device
        raise AttributeError

    @property
    def devices(self):
        return list(
            device for device in self._parent.ha_gateway.devices
            if device in self
        )

    @property
    def scenes(self):
        return list(
            scene for scene in self._parent.ha_gateway.scenes
            if scene in self
        )

    @property
    def plugins(self):
        return list(
            plugin for plugin in self._parent.ha_gateway.installed_plugins
            if plugin in self
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

                Notify(self, self.build_event() + '.{0}.changed'.format(key))
