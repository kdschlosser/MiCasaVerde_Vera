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


class InstalledPlugins(object):

    def __init__(self, ha_gateway, node):
        self._plugins = []
        self.ha_gateway = ha_gateway
        self.send = ha_gateway.send

        if node is not None:
            self._plugins = [InstalledPlugin(self, plugin) for plugin in node]

    def update_node(self, node, full=False):
        if node is not None:
            plugins = []
            for plugin in node:
                # noinspection PyShadowingBuiltins
                id = plugin['id']
                for found_plugin in self._plugins:
                    if found_plugin.id == id:
                        found_plugin.update_node(plugin, full)
                        self._plugins.remove(found_plugin)
                        break
                else:
                    found_plugin = InstalledPlugin(self, plugin)

                plugins += [found_plugin]

            if full:
                for plugin in self._plugins:
                    Notify(plugin, plugin.build_event() + '.removed')
                del self._plugins[:]

            self._plugins += plugins[:]

    def __iter__(self):
        for plugin in self._plugins:
            yield plugin

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

        for plugin in self._plugins:
            if item in (plugin.Title, plugin.id):
                return plugin
        if isinstance(item, int):
            raise IndexError
        raise KeyError


class File(object):
    def __init__(self, parent, node):
        self._parent = parent
        for key, value in node.items():
            self.__dict__[key] = value


class Lua(object):
    def __init__(self, parent, node):
        self._parent = parent
        self.CategoryNum = node.pop('CategoryNum', None)

        for key, value in node.items():
            self.__dict__[key] = value

    @property
    def category(self):
        return self._parent.parent.ha_gateway.categories[self.CategoryNum]


class InstalledPlugin(object):

    def __init__(self, parent, node):
        self.parent = parent

        self.files = []
        self.lua = []
        self.devices = []

        for f in node.pop('Files', []):
            self.files += [File(self, f)]

        for lua in node.pop('Lua', []):
            self.lua += [Lua(self, lua)]

        for plugin_device in node.pop('Devices', []):
            device_type = plugin_device['DeviceType']
            for device in parent.ha_gateway.devices:
                if device.device_type == device_type:
                    self.devices += [device]

        self.id = node.pop('id', None)

        for k, v in node.items():
            self.__dict__[k] = v

        Notify(self, self.build_event() + '.created'.format(self.id))

    def build_event(self):
        return 'installed_plugins.{0}'.format(self.id)

    def delete(self):
        self.parent.send(
            id='delete_plugin',
            Plugin_ID=self.id
        )

    def update(self):
        self.parent.send(
            id='update_plugin',
            Plugin_ID=self.id
        )

    def update_node(self, node, full=False):

        devices = []

        for plugin_device in node.pop('Devices', []):
            device_type = plugin_device['DeviceType']

            for device in self.devices[:]:
                if device.device_type == device_type:
                    devices += [device]
                    self.devices.remove(device)

            for device in self._parent.parent.devices:
                plugin = getattr(device, 'plugin', None)
                if plugin == self and device not in devices:
                    Notify(
                        device,
                        self.build_event() + '.devices.{0}.created'.format(
                            device.id
                        )
                    )
                    devices += [device]

        if full:
            for device in self.devices:
                Notify(
                    device,
                    self.build_event() + '.devices.{0}.removed'.format(
                        device.id
                    )
                )

            del self.devices[:]
        self.devices += devices[:]
