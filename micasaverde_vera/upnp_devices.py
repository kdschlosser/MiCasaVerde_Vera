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
:synopsis: upnp devices

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

import logging
import threading
from .event import Notify
from . import utils

logger = logging.getLogger(__name__)

ATTRIBUTES = ('udn', 'name', 'url', 'ip', 'device_type', 'discovery_date')


class UPNPDevices(object):

    def __init__(self, parent, node):
        self.__lock = threading.RLock()
        self._parent = parent
        self.send = parent.send
        self._devices = []

        if node is not None:
            for device in node:
                self._devices += [UPNPDevice(self, device)]

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
                return self._devices[int(item)]

            for device in self._devices:
                if item == device.udn:
                    return device

            raise KeyError

    @utils.logit
    def update_node(self, node, _=False):
        with self.__lock:
            if node is not None:
                devices = []

                for device in node:
                    for found_device in self._devices[:]:
                        for attr in ATTRIBUTES:
                            found_value = getattr(found_device, attr, None)
                            device_value = device.get(attr, None)
                            if found_value != device_value:
                                break
                        else:
                            self._devices.remove(found_device)
                            break
                    else:
                        found_device = UPNPDevice(self, device)

                    devices += [found_device]

                del self._devices[:]
                self._devices += devices


class UPNPDevice(object):

    def __init__(
        self,
        parent,
        node
    ):
        self._parent = parent
        self.udn = node.pop('udn', None)

        for key, value in node.items():
            self.__dict__[key] = value

        Notify(
            self,
            self.build_event() + '.created'
        )

    def build_event(self):
        return 'upnp_devices.{0}'.format(self.udn)
