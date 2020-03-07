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
:synopsis: rooms

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""


import threading
import logging
from .event import Notify
from . import utils

logger = logging.getLogger(__name__)


def _check_item_type(item):
    from .installed_plugins import InstalledPlugin
    from .scenes import Scene
    from .devices import Device

    if isinstance(item, (InstalledPlugin, Scene, Device)):
        return item


class Rooms(object):

    def __init__(self, ha_gateway, node):
        self.__lock = threading.RLock()
        self.ha_gateway = ha_gateway
        self.send = ha_gateway.send
        self._rooms = [Room(self, {'id': 0, 'name': 'No Room', 'section': 1})]

        if node is not None:
            for room in node:
                self._rooms += [Room(self, room)]

    @utils.logit
    def new(self, name):
        self._parent.send(
            id='room',
            action='create',
            name=name
        )

    def __iter__(self):
        with self.__lock:
            for room in self._rooms:
                yield room

    def __getattr__(self, item):
        with self.__lock:
            if item in self.__dict__:
                return self.__dict__[item]

            try:
                return self[item]
            except (KeyError, IndexError):
                raise AttributeError

    def __getitem__(self, item):
        with self.__lock:
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

    @utils.logit
    def update_node(self, node, full=False):
        with self.__lock:
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
        self.__lock = threading.RLock()
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
        with self.__lock:
            return 'rooms.{0}'.format(self.id)

    @property
    def section(self):
        with self.__lock:
            return self._parent.ha_gateway.sections[self._section]

    @utils.logit
    def remove(self, item):
        with self.__lock:
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

    @utils.logit
    def _plugin_room(self, plugin, room):
        with self.__lock:
            from .installed_plugins import InstalledPlugin

            if not isinstance(plugin, InstalledPlugin):
                plugin = self._parent.ha_gateway.installed_plugins[plugin]

            if getattr(plugin, 'room', None) is not None:
                plugin.room = room

    @utils.logit
    def _scene_room(self, scene, room):
        with self.__lock:
            from .scenes import Scene

            if not isinstance(scene, Scene):
                scene = self._parent.ha_gateway.scenes[scene]

            if getattr(scene, 'room', None) is not None:
                scene.room = room

    @utils.logit
    def _device_room(self, device, room):
        with self.__lock:
            from .devices import Device

            if not isinstance(device, Device):
                device = self._parent.ha_gateway.devices[device]

            if getattr(device, 'room', None) is not None:
                device.room = room

    @utils.logit
    def get_variables(self):
        with self.__lock:
            return list(
                item for item in self.__dict__.keys()
                if not callable(item) and not item.startswith('_')
            )

    def __iadd__(self, item):
        with self.__lock:
            item = _check_item_type(item)

            if item is not None:
                room = getattr(item, 'room', None)
                if room is not None and room != self:
                    item.room = self

    def __isub__(self, item):
        with self.__lock:
            item = _check_item_type(item)

            if item is not None:
                if item in self:
                    item.room = 0

    def __contains__(self, item):
        with self.__lock:
            item = _check_item_type(item)

            if item is not None:
                room = getattr(item, 'room', None)
                if room == self:
                    return True

            return False

    def __iter__(self):
        with self.__lock:
            return iter(self.devices + self.plugins + self.scenes)

    def __getattr__(self, item):
        with self.__lock:
            from micasaverde_vera.installed_plugins import InstalledPlugin

            if item in self.__dict__:
                return self.__dict__[item]

            for device in self.devices + self.plugins + self.scenes:
                if isinstance(device, InstalledPlugin):
                    name = getattr(device, 'Title', None)
                else:
                    name = getattr(device, 'name', None)

                if name is not None and name.replace(' ', '_').lower() == item:
                    return device
            raise AttributeError

    @property
    def devices(self):
        with self.__lock:
            return list(
                device for device in self._parent.ha_gateway.devices
                if device in self
            )

    @property
    def scenes(self):
        with self.__lock:
            return list(
                scene for scene in self._parent.ha_gateway.scenes
                if scene in self
            )

    @property
    def plugins(self):
        with self.__lock:
            return list(
                plugin for plugin in self._parent.ha_gateway.installed_plugins
                if plugin in self
            )

    @property
    def name(self):
        with self.__lock:
            return self._name

    @name.setter
    def name(self, name):
        with self.__lock:
            if self.id:
                self._parent.send(
                    id='room',
                    action='rename',
                    room=self.id,
                    name=name
                )

    @utils.logit
    def delete(self):
        with self.__lock:
            if self.id:
                self._parent.send(
                    id='room',
                    action='delete',
                    room=self.id
                )

    @utils.logit
    def update_node(self, node):
        with self.__lock:
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

                    Notify(
                        self,
                        self.build_event() + '.{0}.changed'.format(key)
                    )
