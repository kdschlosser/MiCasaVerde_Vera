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
:synopsis: zwave device 1 class

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

import logging
import threading
# noinspection PyUnresolvedReferences
from micasaverde_vera.vera_exception import VeraNotImplementedError
from micasaverde_vera import utils

logger = logging.getLogger(__name__)

_default_variables = {
    'urn:micasaverde-com:serviceId:ZWaveDevice1': {
        ('Capabilities', 'Capabilities'): None,
        ('ManufacturerInfo', 'ManufacturerInfo'): None,
        ('VersionInfo', 'VersionInfo'): None,
        ('NodeInfo', 'NodeInfo'): None,
        ('Neighbors', 'Neighbors'): None,
        ('LastReset', 'LastReset'): None,
        ('AssociationNum', 'AssociationNum'): None,
        ('PollOk', 'PollOk'): None,
        ('ConfiguredWakeupInterval', 'ConfiguredWakeupInterval'): None,
        ('FirmwareInfo', 'FirmwareInfo'): None,
        ('MultiChEndpoint', 'MultiChEndpoint'): None,
        ('MultiChCapabilities', 'MultiChCapabilities'): None,
        ('ConfiguredName', 'ConfiguredName'): None,
        ('ConfiguredVariable', 'ConfiguredVariable'): None,
        ('ConfiguredAssoc', 'ConfiguredAssoc'): None,
        ('MeterType', 'MeterType'): None,
        ('MeterScale', 'MeterScale'): None,
        ('SetPointInfo', 'SetPointInfo'): None,
        ('SensorMlType', 'SensorMlType'): None,
        ('SensorBiType', 'SensorBiType'): None,
        ('SensorMlScale', 'SensorMlScale'): None,
        ('SubscribedAlarms', 'SubscribedAlarms'): None,
        ('PollSettings', 'PollSettings'): None,
        ('LastNnu', 'LastNnu'): None,
        ('LastArr', 'LastArr'): None,
        ('PollNoReply', 'PollNoReply'): None,
        ('LastRouteUpdate', 'LastRouteUpdate'): None,
    }
}

_argument_mapping = {
    'urn:micasaverde-com:serviceId:ZWaveDevice1': {}
}


class ZWaveDevice1(object):

    @utils.logit
    def __init__(self, parent):
        self.__lock = threading.RLock()
        self._parent = parent
        self._variables = getattr(self, '_variables', dict())
        self.argument_mapping = getattr(self, 'argument_mapping', dict())

        # noinspection PyUnresolvedReferences
        from micasaverde_vera.utils import copy_dict

        copy_dict(_default_variables, self._variables)
        copy_dict(_argument_mapping, self.argument_mapping)

        self.service_ids = getattr(self, 'service_ids', [])
        self.service_types = getattr(self, 'service_types', [])

        self.service_ids.append(
            'urn:micasaverde-com:serviceId:ZWaveDevice1'
        )
        self.service_types.append(
            'urn:schemas-micasaverde-com:service:ZWaveDevice:1'
        )

    def _get_variable(self, variable, service=None):
        raise NotImplementedError

    def _get_services(self, variable):
        raise NotImplementedError
