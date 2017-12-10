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

# noinspection PyUnresolvedReferences
from micasaverde_vera.vera_exception import VeraNotImplementedError


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

    def __init__(self, parent):
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
