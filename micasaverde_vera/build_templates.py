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


SSDP_REQUEST = (
    'M-SEARCH * HTTP/1.1\r\n'
    'MX: {0}\r\n'
    'ST: {1}\r\n'
    'HOST: {2}:{3}\r\n'
    'MAN: "ssdp:discover"\r\n'
    '\r\n'
)

CONTROLLER_INFO_TEMPLATE = (
    ('-' * 13) +
    ' Vera Located ' +
    ('-' * 13) +
    '\n'
    '   -IP Address: {0}\n'
    '   -Manufacturer: {1}\n'
    '   -Model Name: {2}\n'
    '   -Model Number: {3}\n'
    '   -Model Description: {4}\n'
    '   -Serial Number: {5}\n'
    '   -Firmware Version: {6}\n'
    '   -ZWave Version: {7}\n'
    '   -Home Id: {8}\n' +
    ('-' * 40) +
    '\n'
)

DEVICE_SUBCLASS_IMPORT = (
    '''from ..services.{module_name} import {class_name} as _{class_name}\n'''
)

DEVICE_SUBCLASS_INIT_TEMPLATE = (
    '''        _{class_name}.__init__(self, parent)\n'''
)

DEVICE_CLASS_TEMPLATE = '''
from micasaverde_vera.event import Notify
from micasaverde_vera.devices import Device

{imports}

class {class_name}(Device, {subclasses}):
    service_ids = ['{device_id}']
    service_types = ['{device_type}']

    def __init__(self, parent, node):
        self._parent = parent
        self._variables = {{
            '{device_id}': {{}}
        }}
        self.argument_mapping = {{
            '{device_id}': {{}}
        }}
        self._jobs = []
        self._pending_jobs = 0
        self._configured = 0

{subclass_inits}
        if node is not None:
            self.update_node(node, False)

        Notify(self, 'Device.{{0}}.Created'.format(self.id))

    def create_variable(self, variable, value):
        """
        Creates a New Variable
        """

        orig_variable = variable
        variable = variable.replace('.', '').replace(' ', '')

        if (variable, orig_variable) in self._variables[self.service_ids[0]]:
            return None
        else:
            self._variables[self.service_ids[0]][(variable, orig_variable)] = (
                value
            )

        def var_getter():
            return self._get_variable(orig_variable)[0]

        def var_setter(val):
            self._get_variable(orig_variable)

            self._parent.send(
                DeviceNum=self.id,
                Value=val,
                Variable=orig_variable,
                id='variableset',
                serviceId='{device_id}'
            )

        prop = property(fget=var_getter, fset=var_setter)

        object.__setattr__(self, variable, prop)

        return self._parent.send(
            DeviceNum=self.id,
            Value=value,
            Variable=orig_variable,
            id='variableset',
            serviceId='{device_id}'
        )

    def set_name(self, new_name):
        try:
            self._get_variable('name')
        except NotImplementedError:
            try:
                self._get_variable('Name')
            except NotImplementedError:
                raise NotImplementedError(
                    'Function set_name is not supported.'
                )

        return self._parent.send(
            id='action',
            serviceId='{device_id}',
            action='SetName',
            DeviceNum=self.id,
            NewName=new_name
        )

    def get_name(self):
        try:
            self._get_variable('name')
        except NotImplementedError:
            try:
                self._get_variable('Name')
            except NotImplementedError:
                raise NotImplementedError(
                    'Function get_name is not supported.'
                )

        return self._parent.send(
            id='action',
            serviceId='{device_id}',
            action='GetName',
            DeviceNum=self.id
        )

    @property
    def name(self):
        try:
            return self._get_variable('Name')[0]
        except NotImplementedError:
            return self._get_variable('name')[0]

    @name.setter
    def name(self, value):
        try:
            self._get_variable('Name')
        except NotImplementedError:
            self._get_variable('name')

        self._parent.send(
            id='device',
            action='rename',
            name=value,
            device=self.id
        )

    @property
    def room(self):
        try:
            value, service, keys = self._get_variable('Room')
        except NotImplementedError:
            value, service, keys = self._get_variable('room')

        return self._parent.get_room(value)

    @room.setter
    def room(self, room):
        try:
            self._get_variable('Room')
        except NotImplementedError:
            self._get_variable('room')

        if not isinstance(room, (int, str)):
            room = room.id

        self._parent.send(
            id='device',
            action='rename',
            device=self.id,
            name=self.name,
            room=room
        )

    def delete(self):
        self._parent.send(
            id='device',
            action='delete',
            device=self.id
        )

    @property
    def Jobs(self):
        return self._jobs

    @property
    def PendingJobs(self):
        return self._pending_jobs

    @property
    def Configured(self):
        return self._configured

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        if item in self._variables:
            return self._variables[item]

        try:
            value, service, keys = self._get_variable(item)
        except NotImplementedError:
            raise AttributeError(
                'Attribute {{0}} is not supported.'.format(item)
            )
        if value is None:
            raise AttributeError(
                'Attribute {{0}} is not supported.'.format(item)
            )
        return value

    def _get_services(self, command):
        services = []
        for service_id in self.service_ids[1:]:
            for value in self.argument_mapping[service_id].values():
                if value['orig_name'] == command:
                    services += [service_id]
                    break

            for keys in self._variables[service_id].keys():
                if command in keys:
                    if service_id not in services:
                        services += [service_id]    
                    break

        return services

    def _get_variable(self, variable, service=None):

        if service is not None:
            if service in self._variables:
                for keys, value in self._variables[service].items():
                    if variable in keys:
                        return value, service, keys
        else:
            for service, variables in self._variables.items():
                for keys, value in variables.items():
                    if variable in keys:
                        return value, service, keys

        raise NotImplementedError(
            'Attribute {{0}} is not supported.'.format(variable)
        )
'''

CLASS_TEMPLATE = '''
_default_variables = {{
    '{service_id}': {{{attributes}
    }}
}}

_argument_mapping = {{
    '{service_id}': {{{argument_mappings}
    }}
}}


class {class_name}(object):
    """
    Attributes:
{class_doc}
    """

    def __init__(self, parent):
        self._parent = parent
        self._variables = getattr(self, '_variables', dict())
        self.argument_mapping = getattr(self, 'argument_mapping', dict())

        def iter_mapping(mapping, storage):
            for key, value in mapping.items():
                if isinstance(value, dict):
                    storage[key] = dict()
                    iter_mapping(value, storage[key])
                else:
                    storage[key] = value

        iter_mapping(_default_variables, self._variables)
        iter_mapping(_argument_mapping, self.argument_mapping)

        self.service_ids = getattr(self, 'service_ids', [])
        self.service_types = getattr(self, 'service_types', [])

        self.service_ids.append('{service_id}')
        self.service_types.append('{service_type}')

    def _get_variable(self, variable, service=None):
        raise NotImplementedError

    def _get_services(self, variable):
        raise NotImplementedError
{properties}{methods}'''

ATTR_DOC_TEMPLATE = """        {attr_name} {attr_type}: {attr_docs}\n"""

STATE_TEMPLATE = "\n        ('{attr_name}', '{orig_attr_name}'): None,"

ALLOWED_VALUES_TEMPLATE = '''
            Allowed Values:
                {values}
'''

ALLOWED_RANGE_TEMPLATE = '''
            Allowed Range:
                {values}
'''

ARGUMENT_TEMPLATE = ''',
            '{argument_name}': '{orig_argument_name}\''''

METHOD_ARGUMENT_TEMPLATE = '''
        '{method_name}': {{
            'orig_name': '{orig_method_name}'{arguments}
        }},'''

SERVICE_SEND_TEMPLATE = '''
        services = self._get_services('{second_name}')
        if services:
            for service_id in services:
                {{use_return}}self._parent.send(
                    serviceId=service_id,{{send_arguments}}
                )

        else:
            raise NotImplementedError(
                'Attribute {second_name} is not supported.'
            )
'''

SERVICE_SEND_ARGUMENT_TEMPLATE = '''
                    {keyword}={value},'''

SEND_TEMPLATE = '''        {use_return}self._parent.send({send_arguments}
        )'''

SEND_ARGUMENT_TEMPLATE = '''
            {keyword}={value},'''

PROPERTY_TEMPLATE = '''
    @property
    def {method}(self):
        return self._get_variable('{second_name}')[0]

    @{method}.setter
    def {method}(self, value):
'''

METHOD_TEMPLATE = '''
    def {method}(self, {keywords}):
'''

HEADER_TEMPLATE = """# -*- coding: utf-8 -*-
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
#
#
# ******************* THIS FILE IS AUTOMATICALLY GENERATED *******************
# ******************************* DO NOT MODIFY ******************************

"""
