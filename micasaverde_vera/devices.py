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

    def __init__(self, ha_gateway, node):
        self.ha_gateway = ha_gateway
        self.send = ha_gateway.send
        self._devices = []

        if node is not None:
            for device in node[:]:
                self._devices += [self.__build(device)]
                if self._devices[-1] is None:
                    self._devices.remove(None)

    def __build(self, device):
        device_type = device.get('device_type', '')

        if not device_type:
            return UnknownDevice(self, device)

        try:
            if 'SceneController:1' in device_type:
                from scenes import Scenes
                self.ha_gateway.scenes = Scenes(self.ha_gateway, device)
                return self.ha_gateway.scenes

            cls_name = create_service_name(device_type)
            mod_name = parse_string(cls_name)

            device_mod = importlib.import_module(
                'micasaverde_vera.core.devices.' + mod_name
            )
            device_cls_name = cls_name[:1].upper() + cls_name[1:]
            device_cls = getattr(
                device_mod,
                device_cls_name.replace('_', '')

            )

            return device_cls(self, device)
        except VeraImportError:
            return None

    def __iter__(self):
        for device in self._devices:
            yield device

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

        for device in self._devices:
            if item in (device.id, device.name):
                return device

        if isinstance(item, int):
            raise IndexError

        raise KeyError

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
                    Notify(device, device.build_event() + '.removed')
                del self._devices[:]

            self._devices += devices[:]


# noinspection PyAttributeOutsideInit
class Device(object):
    """
    This is imported by the generated device files.
    
    This gets used as a parent class for identification purposes.
    There is also a device that can get created that has no device type. This
    device is a upnp device that does absolutely nothing and is also invisible
    so the user does not know of it's existence. Because this device has no
    device type we are not able to attach it to a generated class. So tis is
    basically a do nothing for the device.
    
    isinstance(instance, devices.Device)
    """


class UnknownDevice(Device):

    def __init__(self, parent, node):
        self._parent = parent

        def get(variable):
            return node.pop(variable, None)

        if node is not None:
            self.id = get('id')
            self.name = get('name')
            self.pnp = get('pnp')
            self.device_type = get('device_type')
            self.id_parent = get('id_parent')
            self.disabled = get('disabled')
            self.device_file = get('device_file')
            self.device_json = get('device_json')
            self.impl_file = get('impl_file')
            self.manufacturer = get('manufacturer')
            self.model = get('model')
            self.altid = get('altid')
            self.ip = get('ip')
            self.mac = get('mac')
            self.time_created = get('time_created')
            self.embedded = get('embedded')
            self.invisible = get('invisible')
            self.room = get('room')

            for key, value in node.items():
                self.__dict__[key] = value

    def update_node(self, node, full=False):
        pass

    def delete(self):
        self._parent.send(
            serviceId='urn:micasaverde-com:serviceId:HomeAutomationGateway1',
            id='action',
            action='DeleteDevice',
            DeviceNum=self.id,
        )
