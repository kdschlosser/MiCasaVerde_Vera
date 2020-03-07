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
:synopsis: installed plugins

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""


import threading
import logging
from .event import Notify
from . import utils

logger = logging.getLogger(__name__)


class InstalledPlugins(object):

    def __init__(self, ha_gateway, node):
        self.__lock = threading.RLock()
        self._plugins = []
        self.ha_gateway = ha_gateway
        self.send = ha_gateway.send

        if node is not None:
            self._plugins = [InstalledPlugin(self, plugin) for plugin in node]

    @utils.logit
    def update_node(self, node, full=False):
        with self.__lock:
            if node is not None:
                plugins = []
                for plugin in node:
                    # noinspection PyShadowingBuiltins
                    id = plugin['id']

                    try:
                        found_plugin = self[id]
                        found_plugin.update_node(plugin, full)
                        self._plugins.remove(found_plugin)
                    except IndexError:
                        found_plugin = InstalledPlugin(self, plugin)
                    plugins += [found_plugin]

                if full:
                    for plugin in self._plugins:
                        Notify(plugin, plugin.build_event() + '.removed')
                    del self._plugins[:]

                    self._plugins += plugins[:]

    def __iter__(self):
        with self.__lock:
            for plugin in self._plugins:
                yield plugin

    def __getattr__(self, item):
        with self.__lock:
            if item in self.__dict__:
                return self.__dict__[item]

            try:
                return self[item]
            except (KeyError, IndexError):
                raise AttributeError

    # noinspection PyUnresolvedReferences
    def __getitem__(self, item):
        with self.__lock:
            item = str(item)
            if item.isdigit():
                item = int(item)

            for plugin in self._plugins:
                if item in (plugin.Title, plugin.id):
                    return plugin
            if isinstance(item, int):
                raise IndexError
            raise KeyError

    # noinspection PyUnresolvedReferences
    @utils.logit
    def get_variables(self):
        with self.__lock:
            return list(plugin.Title for plugin in self._plugins)


class File(object):

    # noinspection PyShadowingBuiltins
    def __init__(self, parent, id, node):
        self.__lock = threading.RLock()
        self._parent = parent
        self.id = id

        for key, value in node.items():
            self.__dict__[key] = value

        Notify(
            self,
            self.build_event() + '.created'
        )

    @utils.logit
    def get_variables(self):
        with self.__lock:
            return list(
                item for item in self.__dict__.keys()
                if not callable(item) and not item.startswith('_')
            )

    def build_event(self):
        with self.__lock:
            return self._parent.build_event() + '.File.{0}'.format(self.id)

    @utils.logit
    def update_node(self, node):
        with self.__lock:
            for key, value in node.items():
                old_value = getattr(self, key, None)
                if old_value != value:
                    setattr(self, key, value)
                    Notify(
                        self,
                        self.build_event() + '.{0}.changed'.format(key)
                    )


class Files(object):
    def __init__(self, parent, node):
        self.__lock = threading.RLock()
        self.parent = parent
        self.files = node

    def __iter__(self):
        with self.__lock:
            for f in self.files:
                yield f

    @utils.logit
    def update_node(self, node):
        with self.__lock:
            files = []
            for f in node:
                if f in self.files:
                    self.files.remove(f)
                    files += [f]
                else:
                    files += [f]
                    Notify(self, self.parent.build_event() + '.files.changed')

            if self.files:
                Notify(self, self.parent.build_event() + '.files.changed')

            del self.files[:]
            self.files += files[:]


class Luas(object):
    def __init__(self, parent, node):
        self.__lock = threading.RLock()
        self.parent = parent
        self.luas = node

    def __iter__(self):
        with self.__lock:
            for lua in self.luas:
                yield lua

    @utils.logit
    def update_node(self, node):
        with self.__lock:
            luas = []
            for lua in node:
                if lua in self.luas:
                    self.luas.remove(lua)
                    luas += [lua]
                else:
                    luas += [lua]
                    Notify(self, self.parent.build_event() + '.lua.changed')

            if self.luas:
                Notify(self, self.parent.build_event() + '.lua.changed')

            del self.luas[:]
            self.luas += luas[:]


class Devices(object):

    def __init__(self, parent, node):
        self.__lock = threading.RLock()
        self.parent = parent
        self.devices = []

        for plugin_device in node:
            device_type = plugin_device['DeviceType']
            for device in parent.parent.ha_gateway.devices:
                if device.device_type == device_type:
                    self.devices += [device]

    def __iter__(self):
        with self.__lock:
            for device in self.devices:
                yield device

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

            for device in self.devices:
                name = getattr(device, 'name', None)

                if item in (name, device.id):
                    return device
            if isinstance(item, int):
                raise IndexError
            raise KeyError

    @utils.logit
    def update_node(self, node):

        with self.__lock:
            devices = []

            for plugin_device in node:
                plugin_device_type = plugin_device['DeviceType']

                for device in self.parent.parent.ha_gateway.devices:
                    if device.device_type == plugin_device_type:
                        if device in self.devices:
                            devices += [device]
                            self.devices.remove(device)
                        elif device not in devices:
                            devices += [device]
                            Notify(
                                device,
                                self.parent.build_event() +
                                '.devices.{0}.created'.format(device.id)
                            )

            for device in self.devices:
                Notify(
                    device,
                    (
                        self.parent.build_event() +
                        '.devices.{0}.removed'.format(device.id)
                    )
                )

            del self.devices[:]
            self.devices = devices[:]


class InstalledPlugin(object):

    def __init__(self, parent, node):
        self.__lock = threading.RLock()
        self.parent = parent
        self.id = node.pop('id', None)
        self.files = Files(self, node.pop('Files', []))
        self.lua = Luas(self, node.pop('Lua', []))
        self.devices = Devices(self, node.pop('Devices', []))

        for k, v in node.items():
            self.__dict__[k] = v

        Notify(self, self.build_event() + '.created')

    def __iter__(self):
        return iter(self.devices)

    @utils.logit
    def get_variables(self):
        with self.__lock:
            return list(
                item for item in self.__dict__.keys()
                if not callable(item) and not item.startswith('_')
            )

    def build_event(self):
        with self.__lock:
            return 'installed_plugins.{0}'.format(self.id)

    @utils.logit
    def delete(self):
        with self.__lock:
            self.parent.send(
                id='delete_plugin',
                Plugin_ID=self.id
            )

    @utils.logit
    def update(self):
        with self.__lock:
            self.parent.send(
                id='update_plugin',
                Plugin_ID=self.id
            )

    @utils.logit
    def update_node(self, node, _=False):
        with self.__lock:
            self.devices.update_node(node.pop('Devices', []))
            self.lua.update_node(node.pop('Lua', []))
            self.files.update_node(node.pop('Files', []))

            for key, value in node.items():
                old_value = getattr(self, key, None)
                if old_value != value:
                    setattr(self, key, value)
                    Notify(
                        self,
                        self.build_event() + '{0}.changed'.format(key)
                    )
