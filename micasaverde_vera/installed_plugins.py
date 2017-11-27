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

    def __init__(self, parent, node):
        self._plugins = []
        self._parent = parent

        if node is not None:
            for plugin in node:
                self._plugins += [InstalledPlugin(self, plugin)]

    def get_category(self, number):
        return self._parent.get_category(number)

    def get_plugin(self, number):
        number = str(number)
        if number.isdigit():
            number = int(number)

        for plugin in self._plugins:
            if number in (plugin.Title, plugin.id):
                return plugin

    def update_node(self, node, full=False):
        if node is not None:
            plugins = []
            for plugin in node:
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
                    Notify(
                        plugin,
                        'InstalledPlugin.{0}.Removed'.format(plugin.id)
                    )
                del self._plugins[:]

            self._plugins += plugins[:]


class File(object):
    def __init__(self, parent, node):
        self._parent = parent
        for key, value in node.items():
            self.__dict__[key] = value


class Lua(object):
    def __init__(self, parent, node):
        self._parent = parent
        for key, value in node.items():
            self.__dict__[key] = value

    @property
    def category(self):
        return self._parent.get_category(self.CategoryNum)


class InstalledPlugin(object):

    def __init__(self, parent, node):
        self._parent = parent

        self.files = []
        self.lua = []
        self.devices = []

        for f in node.pop('Files', []):
            self.files += [File(self, f)]

        for lua in node.pop('Lua', []):
            self.lua += [Lua(self, lua)]

        for plugin_device in node.pop('Devices', []):
            device_type = plugin_device['DeviceType']
            for device in parent._parent.devices:
                if device.device_type == device_type:
                    self.devices += [device]

        self.__dict__.update(node)

        Notify(self, 'InstalledPlugin.{0}.Created'.format(self.id))

    def get_category(self, number):
        return self._parent.get_category(number)

    def delete(self):
        self._parent.send(
            id='delete_plugin',
            Plugin_ID=self.id
        )

    def update(self):
        self._parent.send(
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

            for device in self._parent._parent.devices:
                if device.device_type == device_type and device not in devices:
                    Notify(
                        device,
                        'InstalledPlugin.{0}.Device.{1}.Created'.format(
                            self.id,
                            device.id
                        )
                    )
                    devices += [device]

        if full:
            for device in self.devices:
                Notify(
                    device,
                    'InstalledPlugin.{0}.Device.{1}.Removed'.format(
                        self.id,
                        device.id
                    )
                )

            del self.devices[:]
        self.devices += devices[:]
