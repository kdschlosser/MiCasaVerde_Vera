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
    '''# noinspection PyUnresolvedReferences
from micasaverde_vera.core.services.{module_name} import (
    {class_name} as _{class_name},
    )
'''
)

DEVICE_SUBCLASS_INIT_TEMPLATE = (
    '''        _{class_name}.__init__(self, parent)
'''
)


DEVICE_CLASS_TEMPLATE = '''
# noinspection PyUnresolvedReferences
from micasaverde_vera.event import Notify
# noinspection PyUnresolvedReferences
from micasaverde_vera.devices import Device
# noinspection PyUnresolvedReferences
from micasaverde_vera.vera_exception import VeraNotImplementedError

{imports}

# noinspection PyPep8Naming
class {class_name}(Device, {subclasses}):

    def __init__(self, parent, node):
        self._parent = parent
        self.__lock = threading.RLock()
        
        self.service_ids = [
            '{device_id}'
        ]
        self.service_types = [
            '{device_type}'
        ]
        
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

        Notify(self, self.build_event() + '.created')
        
    def build_event(self):
        with self.__lock:
            return 'devices.{{0}}'.format(self.id)

    def create_variable(self, variable, value):
        """
        Creates a New Variable
        """
        
        with self.__lock:
            orig_variable = variable
            variable = variable.replace('.', '').replace(' ', '')

            if (
                variable,
                orig_variable
            ) in self._variables[self.service_ids[0]]:
                return None
                
            else:
                self._variables[
                    self.service_ids[0]
                ][(variable, orig_variable)] = value

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

            setattr(self, variable, prop)

            return self._parent.send(
                DeviceNum=self.id,
                Value=value,
                Variable=orig_variable,
                id='variableset',
                serviceId='{device_id}'
            )

    def set_name(self, new_name):
        with self.__lock:    
            try:
                self._get_variable('name')
            except VeraNotImplementedError:
                try:
                    self._get_variable('Name')
                except VeraNotImplementedError:
                    raise VeraNotImplementedError(
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
        with self.__lock:
            try:
                self._get_variable('name')
            except VeraNotImplementedError:
                try:
                    self._get_variable('Name')
                except VeraNotImplementedError:
                    raise VeraNotImplementedError(
                        'Function get_name is not supported.'
                    )

            return self._parent.send(
                id='action',
                serviceId='{device_id}',
                action='GetName',
                DeviceNum=self.id
            )
        
    @property
    def category(self):
        with self.__lock:
            try:
                category = getattr(self, 'category_num')
            except VeraNotImplementedError as err:
                try:
                    return getattr(self, 'plugin').Title
                except VeraNotImplementedError:
                    raise err
                
            return self._parent.ha_gateway.categories[category]
        
    @property
    def sub_category(self):
        with self.__lock:
            try:
                sub_category = getattr(self, 'subcategory_num')
            except VeraNotImplementedError as err:
                try:
                    return getattr(self, 'plugin').Title
                except VeraNotImplementedError:
                    raise err
            else:
                category = getattr(self, 'category_num')
            
            subcategory = '{{0}}.{{1}}'.format(category, sub_category)
            return self._parent.ha_gateway.categories[subcategory]
        
    @property
    def plugin(self):
        with self.__lock:
            plugin = self._get_variable('plugin')[0]
            return self._parent.ha_gateway.installed_plugins[plugin]

    @property
    def name(self):
        with self.__lock:
            try:
                return self._get_variable('Name')[0]
            except VeraNotImplementedError:
                return self._get_variable('name')[0]

    @name.setter
    def name(self, value):
        with self.__lock:
            try:
                self._get_variable('Name')
            except VeraNotImplementedError:
                self._get_variable('name')

            self._parent.send(
                id='device',
                action='rename',
                name=value,
                device=self.id
            )

    @property
    def room(self):
        with self.__lock:
            try:
                value, service, keys = self._get_variable('Room')
            except VeraNotImplementedError:
                value, service, keys = self._get_variable('room')

            return self._parent.ha_gateway.rooms[value]

    @room.setter
    def room(self, room):
        with self.__lock:
            try:
                self._get_variable('Room')
            except VeraNotImplementedError:
                self._get_variable('room')
            
            # noinspection PyUnresolvedReferences
            from micasaverde_vera.rooms import Room 

            if isinstance(room, Room):
                room = room.id
        
            room = int(str(room))
    
            self._parent.send(
                id='device',
                action='rename',
                device=self.id,
                name=self.name,
                room=room
            )

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

    @property
    def Jobs(self):
        with self.__lock:
            return self._jobs

    @property
    def PendingJobs(self):
        with self.__lock:
            return self._pending_jobs

    @property
    def Configured(self):
        with self.__lock:
            return self._configured

    def __getattr__(self, item):
        with self.__lock:
            if item in self.__dict__:
                return self.__dict__[item]

            if item in self._variables:
                return self._variables[item]

            try:
                value, service, keys = self._get_variable(item)
            except VeraNotImplementedError:
                value = None
            
            if value is None:
                for cls in self.__class__.__mro__[:-1]:
                    if item in cls.__dict__:
                        attr = cls.__dict__[item]
                    
                        if isinstance(attr, property):
                            return attr.fget(self)
                        
                        return attr
                raise VeraNotImplementedError(
                    'Attribute {{0}} is not supported.'.format(item)
                )
            return value

    def _get_services(self, command):
        with self.__lock:
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
        with self.__lock:
            if service is not None:
                if service in self._variables:
                    for keys, value in self._variables[service].items():
                        if variable in keys and value is not None:
                            return value, service, keys
            else:
                for service, variables in self._variables.items():
                    for keys, value in variables.items():
                        if variable in keys and value is not None:
                            return value, service, keys

            raise VeraNotImplementedError(
                'Attribute {{0}} is not supported.'.format(variable)
            )
        
    def get_functions(self):
        with self.__lock:
            import inspect
            res = []

            for cls in self.__class__.__mro__[:-1]:
                for attribute in inspect.classify_class_attrs(cls):
                    if attribute.kind == 'method':
                        res += [attribute.name]

            return sorted(
                list(item for item in set(res) if not item.startswith('_'))
            )

    def get_variables(self):
        with self.__lock:
            import inspect
            res = []
            
            for service_id in self.service_ids:
                for keys, value in self._variables[service_id].items():
                    if value is not None:
                        res += [keys[0]]
                        
            for cls in self.__class__.__mro__[:-1]:
                for attribute in inspect.classify_class_attrs(cls):
                    if attribute.kind in ('property', 'data'):
                        try:
                            if getattr(self, attribute.name) is not None:
                                res += [attribute.name]
                        except VeraNotImplementedError:
                            continue
            res = set(res)

            return sorted(
                list(item for item in res if not item.startswith('_'))
            )

    def __dir__(self):
        """
        Modifies the output when using dir()

        This modifies the output when dir() is used on an instance of this 
        device. The purpose for this is not all devices will use every 
        component of this class.
        """
        with self.__lock:
            return self.get_functions() + self.get_variables()
        
    def update_node(self, node, full=False):
        """
        Updates the device with data retrieved from the Vera

        This is internally used.
        """
        
        with self.__lock:
            def check_value(variable, value, service_id=None):
                if service_id is not None:
                    if service_id not in self._variables:
                        if service_id.endswith('ZWaveDevice1'):
                            # noinspection PyUnresolvedReferences
                            from micasaverde_vera.utils import copy_dict
                            # noinspection PyUnresolvedReferences
                            from micasaverde_vera.z_wave_device_1 import (
                                ZWaveDevice1 as service
                            )
                        
                        else:
                            # noinspection PyUnresolvedReferences
                            from micasaverde_vera.utils import (
                                import_service,
                                copy_dict
                            )
                
                            service = import_service(state['service'])
                        
                        if service is None:
                            return
                        
                        if service is False:
                            print(
                                'MiCasaVerde Vera: '
                                'Unknown service {{0}}'.format(service_id)
                            )
                            self._variables[service_id] = dict()
                        else:                
                            service_instance = service(self._parent)
                    
                            copy_dict(
                                service_instance._variables,
                                self._variables
                            )
                            copy_dict(
                                service_instance.argument_mapping,
                                self.argument_mapping
                            )
                    
                            self.service_ids += [
                                service_instance.service_ids[-1]
                            ]
                            self.service_types += [
                                service_instance.service_types[-1]
                            ]
                        
                            if not isinstance(self, service):
                                self.__class__.__bases__ += (service,)
                        
                    try:
                        old_value, service_id, keys = self._get_variable(
                            variable,
                            service_id
                        )
                    except VeraNotImplementedError:
                        old_value = None
                        keys = (variable, variable)
                else:
                    try:
                        (
                            old_value,
                            service_id,
                            keys
                        ) = self._get_variable(variable)
                        
                    except VeraNotImplementedError:
                        old_value = None
                        keys = (variable, variable)
                        service_id = self.service_ids[0]

                if old_value != value:
                    self._variables[service_id][keys] = value
                    if full:
                        Notify(
                            self,
                            self.build_event() + '.{{0}}.{{1}}.changed'.format(
                                service_id.split(':')[-1],
                                variable.replace('.', '')
                            )
                        )

            if node is not None:
                if 'tooltip' in node:
                    del node['tooltip']

                for state in node.pop('states', []):
                    check_value(
                        state['variable'],
                        state['value'],
                        state['service']
                    )
    
                for node_key, node_value in node.items():
                    check_value(node_key, node_value)
'''

CLASS_TEMPLATE = '''
# noinspection PyUnresolvedReferences
from micasaverde_vera.vera_exception import VeraNotImplementedError


_default_variables = {{
    '{service_id}': {{{attributes}
    }}
}}

_argument_mapping = {{
    '{service_id}': {{{argument_mappings}
    }}
}}


# noinspection PyPep8Naming
class {class_name}(object):
    """
    Properties:
{class_doc}
    """

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
            '{service_id}'
        )
        self.service_types.append(
            '{service_type}'
        )

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
                raise VeraNotImplementedError(
                    'Attribute {second_name} is not supported.'
                )
'''

SERVICE_SEND_ARGUMENT_TEMPLATE = '''
                        {keyword}={value},'''

SEND_TEMPLATE = '''            {use_return}self._parent.send({send_arguments}
        )'''

SEND_ARGUMENT_TEMPLATE = '''
                    {keyword}={value},'''

PROPERTY_TEMPLATE = '''
    @property
    def {method}(self):
        with self.__lock:
            return self._get_variable('{second_name}')[0]

    @{method}.setter
    def {method}(self, value):
        with self.__lock:'''

METHOD_TEMPLATE = '''
    def {method}(self, {keywords}):
        with self.__lock:
'''

HEADER_TEMPLATE = """# -*- coding: utf-8 -*-
#
# This file is part of EventGhost.
# Copyright © 2005-2018 EventGhost Project <http://www.eventghost.net/>
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


from __future__ import print_function
import threading"""
