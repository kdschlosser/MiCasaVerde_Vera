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
