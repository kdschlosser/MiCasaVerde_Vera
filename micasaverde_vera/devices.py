# -*- coding: utf-8 -*-

# **micasaverde_vera** is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# **micasaverde_vera** is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-openzwave. If not, see http://www.gnu.org/licenses.

"""
This file is part of the **micasaverde_vera**
project https://github.com/kdschlosser/MiCasaVerde_Vera.

:platform: Unix, Windows, OSX
:license: GPL(v3)
:synopsis: devices

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

import threading
import logging
from .event import Notify
from .vera_exception import VeraNotImplementedError
from . import utils


logger = logging.getLogger(__name__)


class Devices(object):

    def __init__(self, ha_gateway, node):
        self.__lock = threading.RLock()
        self.ha_gateway = ha_gateway
        self.send = ha_gateway.send
        self._devices = []
        self._device_error = []

        if node is not None:
            for device in node[:]:
                self._devices += [self.__get_device_class(device)]
                if self._devices[-1] is None:
                    self._devices.remove(None)

    @utils.logit
    def get_variables(self):
        with self.__lock:
            res = []

            for device in self._devices:
                try:
                    res += [device.name]
                except (VeraNotImplementedError, AttributeError):
                    res += [str(device.id)]
            return res

    @utils.logit
    def __get_device_class(self, device):
        device_type = device.get('device_type', '')

        if not device_type:
            return UnknownDevice(self, device)

        if device_type in self._device_error:
            return None

        if 'SceneController:1' in device_type:
            from .scenes import Scenes
            self.ha_gateway.scenes = Scenes(self.ha_gateway, device)
            return self.ha_gateway.scenes

        from .utils import import_device

        device_cls = import_device(device_type)

        if device_cls is None:
            return None

        if device_cls is False:
            self._device_error += [device_type]
            logger.error('MiCasaVerde_Vera: Unknown device {0}'.format(device_type))

        else:
            return device_cls(self, device)

    def __iter__(self):
        with self.__lock:
            for device in self._devices:
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

            for device in self._devices:
                name = getattr(device, 'name', None)
                if name is not None and name.replace(' ', '_').lower() == item:
                    return device
                if item in (device.id, device.name):
                    return device

            if isinstance(item, int):
                raise IndexError('{0} not found'.format(item))

            raise KeyError('{0} not found'.format(item))

    @utils.logit
    def update_node(self, node, full=False):
        with self.__lock:
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
                        found_device = self.__get_device_class(device)

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
        self.__lock = threading.RLock()
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

    @utils.logit
    def update_node(self, node, full=False):
        pass

    @utils.logit
    def delete(self):
        with self.__lock:
            self._parent.send(
                serviceId=(
                    'urn:micasaverde-com:serviceId:HomeAutomationGateway1'
                ),
                id='action',
                action='DeleteDevice',
                DeviceNum=self.id,
            )

    @utils.logit
    def get_variables(self):
        with self.__lock:
            return list(
                item for item in self.__dict__.keys()
                if not callable(item) and not item.startswith('_')
            )
