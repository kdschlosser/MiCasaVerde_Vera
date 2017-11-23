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


class UPNPDevices(object):

    def __init__(self, parent, node):
        self._parent = parent
        self.send = parent.send
        self._devices = []
        self._bindings = []

        if node is not None:
            for device in node:
                self._devices += [UPNPDevice(self, device)]

    def __iter__(self):
        for device in self._devices:
            yield device

    def register_event(self, callback, attribute=None):
        self._bindings += [EventHandler(self, callback, None)]
        return self._bindings[-1]

    def unregister_event(self, event_handler):
        if event_handler in self._bindings:
            self._bindings.remove(event_handler)

    def update_node(self, node, full=False):
        if node is not None:
            devices = []

            for device in node:
                udn = device['udn']

                for found_device in self._devices[:]:
                    if found_device.udn == udn:
                        self._devices.remove(found_device)
                else:
                    found_device = UPNPDevice(self, device)
                    for event_handler in self._bindings:
                        event_handler('new', upnp_device=found_device)

                devices += [found_device]

            if full:
                for device in self._devices:
                    for event_handler in self._bindings:
                        event_handler('remove', upnp_device=device)

                del self._devices[:]

            self._devices += devices


class UPNPDevice(object):

    def __init__(self, parent, node):
        self._parent = parent
        for key, value in node.items():
            self.__dict__[key] = value
