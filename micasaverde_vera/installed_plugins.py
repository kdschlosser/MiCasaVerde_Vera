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
<InstalledPlugins2>
    <InstalledPlugins Version="25742" AllowMultiple="0" Title="Wunderground Weather Plugin" Icon="plugins/icons/45.png" Instructions="http://code.mios.com/trac/mios_weather" Hidden="0" AutoUpdate="1" VersionMajor="1" VersionMinor="58" SupportedPlatforms="**((NULL))**" MinimumVersion="**((NULL))**" DevStatus="**((NULL))**" Approved="1" id="45" timestamp="1486651137">
        <Files>
            <File SourceName="D_Weather.xml" SourcePath="**((NULL))**" DestName="D_Weather.xml" DestPath="" Compress="1" Encrypt="0" Role="D"></File>
            <File SourceName="D_Weather.json" SourcePath="**((NULL))**" DestName="D_Weather.json" DestPath="" Compress="1" Encrypt="0" Role="J"></File>
            <File SourceName="S_Weather.xml" SourcePath="**((NULL))**" DestName="S_Weather.xml" DestPath="" Compress="1" Encrypt="0" Role="S"></File>
            <File SourceName="I_WUIWeather.xml" SourcePath="**((NULL))**" DestName="I_WUIWeather.xml" DestPath="" Compress="1" Encrypt="1" Role="I"></File>
        </Files>
        <Devices>
            <Device DeviceFileName="D_Weather.xml" DeviceType="urn:demo-micasaverde-com:device:weather:1" ImplFile="I_WUIWeather.xml" Invisible="0" CategoryNum="**((NULL))**"></Device>
        </Devices>
        <Lua>
            <Lu FileName="L_LuaXP.lua"></Lu>
            <Lu FileName="L_SiteSensor1.lua"></Lu>
        </Lua>
    </InstalledPlugins>
</InstalledPlugins2>
"""

from event import EventHandler


class InstalledPlugins(object):
    _plugins = []

    def __init__(self, parent, node):
        self._parent = parent
        self._bindings = []

        if node is not None:
            for plugin in node:
                self._plugins += [InstalledPlugin(self, plugin)]

    def register_event(self, callback, attribute=None):
        self._bindings += [EventHandler(self, callback, None)]
        return self._bindings[-1]

    def unregister_event(self, event_handler):
        if event_handler in self._bindings:
            self._bindings.remove(event_handler)

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
                    for event_handler in self._bindings:
                        event_handler('new', plugin=found_plugin)

                plugins += [found_plugin]

            if full:
                for plugin in self._plugins:
                    for event_handler in self._bindings:
                        event_handler('remove', plugin=plugin)

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
        self._bindings = []

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

    def register_event(self, callback, attribute=None):
        self._bindings += [EventHandler(self, callback, None)]
        return self._bindings[-1]

    def unregister_event(self, event_handler):
        if event_handler in self._bindings:
            self._bindings.remove(event_handler)

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
                    for event_handler in self._bindings:
                        event_handler('new', plugin=self, device=device)

                    devices += [device]

        if full:
            for device in self.devices:
                for event_handler in self._bindings:
                    event_handler('remove', plugin=self, device=device)

            del self.devices[:]
        self.devices += devices[:]
