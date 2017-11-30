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

import importlib
from event import Notify
from utils import create_service_name, parse_string
from vera_exception import VeraImportError


class Devices(object):

    def __init__(self, parent, node):
        self._parent = parent
        self.send = parent.send
        self._devices = []

        if node is not None:
            for device in node[:]:
                self._devices += [self.__build(device)]
                if self._devices[-1] is None:
                    self._devices.remove(None)

    def __build(self, device):
        device_type = device.get('device_type')
        try:
            if 'SceneController:1' in device_type:
                from scenes import Scenes

                self._parent.scenes = Scenes(self._parent, device)
                self._parent.get_scene = self._parent.scenes.get_scene

                return self._parent.scenes

            cls_name = create_service_name(device_type)
            mod_name = parse_string(cls_name)

            device_mod = importlib.import_module(
                'micasaverde_vera.core.devices.' + mod_name
            )
            device_cls = getattr(
                device_mod,
                cls_name[:1].upper() + cls_name[1:]
            )

            return device_cls(self, device)
        except VeraImportError:
            return None

    def get_room(self, number):
        return self._parent.get_room(number)

    def get_category(self, number):
        return self._parent.get_category(number)

    def get_geofence(self, number):
        return self._parent.get_geofence(number)

    def get_section(self, number):
        return self._parent.get_section(number)

    def get_user(self, number):
        return self._parent.get_user(number)

    def get_plugin(self, number):
        return self._parent.get_plugin(number)

    def get_device(self, number):
        number = str(number)
        if number.isdigit():
            number = int(number)

        for device in self._devices:
            if number in (device.name, device.id):
                return device

    def __iter__(self):
        for device in self._devices:
            yield device

    def update_node(self, node, full=False):
        if node is not None:
            if 'status' in node:
                del node['status']
            devices = []
            for device in node:
                # noinspection PyShadowingBuiltins
                id = device['id']
                for found_device in self._devices[:]:
                    if found_device.id == id:
                        found_device.update_node(device, full)
                        self._devices.remove(found_device)
                        break
                else:
                    if (
                        'device_type' in device and
                        'SceneController:1' in device['device_type'] and
                        self._parent.scenes is not None
                    ):
                        self._parent.scenes.update_node(device, full)
                        found_device = self._parent.scenes
                    else:
                        found_device = self.__build(device)

                if found_device is not None:
                    devices += [found_device]

            if full:
                for device in self._devices:
                    Notify(
                        device,
                        'Device.{0}.Removed'.format(device.id)
                    )
                del self._devices[:]

            self._devices += devices[:]


# noinspection PyAttributeOutsideInit
class Device(object):
    """
    This is imported by the generated device files.
    
    This gets used as a subclass for identification purposes only.
    
    isinstance(instance, devices.Device)
    """
