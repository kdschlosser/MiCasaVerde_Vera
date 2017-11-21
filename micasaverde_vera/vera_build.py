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


import os
import sys
import socket
import requests
import xml.etree.cElementTree as ElementTree
from utils import parse_string, create_service_name


HEADER = """# -*- coding: utf-8 -*-
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

if os.name == 'nt':
    BUILD_PATH = os.path.join(
        os.path.expandvars('%APPDATA%'),
        'MiCasaVerde_Vera'
    )

else:
    BUILD_PATH = os.path.join(os.path.expanduser('~'), '.MiCasaVerde_Vera')


DEVICES_PATH = os.path.join(BUILD_PATH, 'devices')
SERVICES_PATH = os.path.join(BUILD_PATH, 'services')


if not os.path.exists(BUILD_PATH):
    os.makedirs(BUILD_PATH)
    with open(os.path.join(BUILD_PATH, '__init__.py'), 'w') as f:
        f.write('')

if not os.path.exists(DEVICES_PATH):
    os.makedirs(DEVICES_PATH)
    with open(os.path.join(DEVICES_PATH, '__init__.py'), 'w') as f:
        f.write('')

if not os.path.exists(SERVICES_PATH):
    os.makedirs(SERVICES_PATH)
    with open(os.path.join(SERVICES_PATH, '__init__.py'), 'w') as f:
        f.write('')


# sys.path.append(BUILD_PATH)

SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900
SSDP_MX = 10
SSDP_ST = "upnp:rootdevice"

SSDP_REQUEST = (
    'M-SEARCH * HTTP/1.1\r\n'
    'MX: %d\r\n'
    'ST: %s\r\n'
    'HOST: %s:%d\r\n'
    'MAN: "ssdp:discover"\r\n'
    '\r\n' % (SSDP_MX, SSDP_ST, SSDP_ADDR, SSDP_PORT)
)

DEVICE_SUBCLASS_IMPORT = (
    '''from ..services.{module_name} import {class_name} as _{class_name}\n'''
)
DEVICE_SUBCLASS_INIT_TEMPLATE = (
    '''        _{class_name}.__init__(self, parent)\n'''
)
DEVICE_CLASS_TEMPLATE = '''
from micasaverde_vera.event import EventHandler

{imports}

class {class_name}({subclasses}):
    _service_id = '{device_id}'
    _service_type = '{device_type}'
    
    def __init__(self, parent, node):
        self._parent = parent
        self._variables = dict()
        self._bindings = []
        self._jobs = []
        self._pending_jobs = 0
        self._configured = 0
        
{subclass_inits}
        if node is not None:
            def update_variables(key, value):
                for k in self._variables.keys()[:]:
                    if key in k:
                        self._variables[k] = value
                        break
                else:
                    self._variables[(key, key)] = value
                    
            for state in node.pop('states', []):
                update_variables(state['variable'], state['value'])
            
            for attr_name, attr_value in node.items():
                update_variables(attr_name, attr_value)
                
    def register_event(self, callback, attribute=None):
        self._bindings += [EventHandler(self, callback, attribute)]
        return self._bindings[-1]

    def unregister_event(self, event_handler):
        if event_handler in self._bindings:
            self._bindings.remove(event_handler)
            
    @property
    def name(self):
        for key, value in self._variables.items():
            if 'name' in key:
                return value
        raise AttributeError('Attribute name is not found.')
        
    @name.setter
    def name(self, value):
        for key in self._variables.keys():
            if 'name' in key:
                self._parent.send(
                    DeviceNum=self.id,
                    Value=value,
                    Variable='name',
                    id='variableset',
                    serviceId='{device_id}'
                )
                break
        else:
            raise AttributeError('Attribute name is not found.')
    
    @property
    def Jobs(self):
        return self._jobs
        
    @Jobs.setter
    def Jobs(self, value):
        self._jobs = value
        
    @property
    def PendingJobs(self):
        return self._pending_jobs
        
    @PendingJobs.setter
    def PendingJobs(self, value):
        self._pending_jobs = value
        
    @property
    def Configured(self):
        return self._configured
        
    @Configured.setter
    def Configured(self, value):
        self._configured = value
    
    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
            
        for key, value in self._variables.items():
            if item in key:
                if value is None:
                    raise AttributeError(
                        'Attribute {{0}} is not used '
                        'for this device.'.format(item)
                    )
                return value
            
        raise AttributeError('Attribute {{0}} is not found.'.format(item))
    
    def __setattr__(self, key, value):
        if key.startswith('_'):
            object.__setattr__(self, key, value)
        elif isinstance(getattr(self.__class__, key, None), property):
            object.__setattr__(self, key, value)
        elif (
            isinstance(
                getattr(self.__class__, key.replace('.', ''), None),
                property
            )
        ):
            object.__setattr__(self, key.replace('.', ''), value)
        else:
            raise AttributeError(
                'You are not allowed to set attribute {{0}}.'.format(key)
            )
    
    def update_node(self, node, _):
        """
        Updates the device with data retreived from the Vera
        
        This is internally used.
        """
        
        del node['tooltip']
        
        def check_value(variable, value):
            found_value = getattr(self, variable, None)
            if found_value is None:
                for event_handler in self._bindings:
                    event_handler(
                        'new',
                        device=self,
                        attribute=variable,
                        value=value
                    )
                
                self._variables[(variable, variable)] = value
            
            elif found_value != value:
                for event_handler in self._bindings:
                    event_handler(
                        'change',
                        device=self,
                        attribute=variable,
                        value=value
                    )
                
                for key in self._variables.keys()[:]:
                    if variable in key:
                        self._variables[key] = value
        
        if node is not None:
            for state in node.pop('states', []):
                check_value(state['variable'], state['value'])
            
            for item in node.items():
                check_value(*item)
    
    def __dir__(self):
        """
        Modifies the output when using dir()
        
        This modifies the output when dir() is used on an instance of this 
        device. The purpose for this is not all devices will use every 
        component of this class.
        """
        
        dir_list = dir(self.__class__)
        keys = list(
            key[1] for (key, value) in self._variables.items()
            if value is not None
        )
        
        return sorted(list(set(keys + dir_list)))
'''

CLASS_TEMPLATE = '''
_default_variables = {{{attributes}
}}


class {class_name}(object):
    """
    Attributes:
{class_doc}
    """
    
    def __init__(self, parent):
        self._parent = parent
        self._variables = getattr(self, '_variables', dict())
        for key, value in _default_variables.items():
            if key not in self._variables:
                self._variables[key] = value
{properties}{methods}
'''

ATTR_DOC_TEMPLATE = """        {attr_name} {attr_type}: {attr_docs}\n"""
STATE_TEMPLATE = "\n    {attr_name}: None,"
ALLOWED_VALUES_TEMPLATE = '''
            Allowed Values:
                {values}
'''

ALLOWED_RANGE_TEMPLATE = '''
            Allowed Range:
                {values}
'''


SEND_TEMPLATE = '''        self._parent.send({send_arguments}
        )'''
SEND_ARGUMENT_TEMPLATE = '''
            {keyword}={value},'''

PROPERTY_TEMPLATE = '''
    @property
    def {method}(self):
        for key, value in self._variables.items():
            if '{second_name}' in key:
                return value

    @{method}.setter
    def {method}(self, value):
{send_template}
'''

METHOD_TEMPLATE = '''
    def {method}(self, {keywords}):
{send_template}
'''

DATA_TYPES = dict(
    string='(str)',
    char='(str)',
    boolean='(bool)',
    ui4='(int)',
    ui1='(int)',
    ui2='(int)',
    i1='(int)',
    number='(int)',
    i4='(int)',
    float='(float)'
)

NUMBER_MAPPING = {
    '1': 'one_',
    '2': 'two_',
    '3': 'three_',
    '4': 'four_',
    '5': 'five_',
    '6': 'six_',
    '7': 'seven_',
    '8': 'eight_',
    '9': 'nine_',
    '0': 'zero_'
}


URL = 'http://{ip_address}/cgi-bin/cmh/'
GET_UPNP_FILES = URL + 'get_upnp_files.sh'
VIEW_UPNP_FILE = URL + 'view_upnp_file.sh?file={file}'
SYS_INFO = URL + 'sysinfo.sh'
CATEGORIES = 'http://{ip_address}/cmh/js/config/constants.js'
CATEGORY_LANG = 'http://{ip_address}/cmh/js/config/lang.js'
VERA_INFO = 'http://{ip_address}/upnp/vera.xml'

vera_files = os.listdir(BUILD_PATH)


def print_list(l, indent):

    for item in l:
        if isinstance(item, list):
            if len(item) > 2:
                print indent + '['
                print_list(item, indent + '    ')
                print indent + ']'
            else:
                print indent + repr(item)
        else:
            print indent + repr(item)


def print_dict(d, indent=''):
    for key, value in d.items():
        if isinstance(value, dict):
            print indent, key, ':'
            print_dict(value, indent + '    ')
        elif isinstance(value, list):
            print indent + key + ':'
            print_list(value, indent + '    ')
        else:
            print indent + key + ':', value


def make_property_template(method, second_name, send_arguments):
    send_template = SEND_TEMPLATE.format(
        send_arguments=send_arguments
    )
    template = PROPERTY_TEMPLATE.format(
        method=method,
        second_name=second_name,
        send_template=send_template
    )
    return template


def make_method_template(method, keywords, send_arguments):
    send_template = '        return ' + SEND_TEMPLATE.format(
        send_arguments=send_arguments
    )[8:]

    template = METHOD_TEMPLATE.format(
        keywords=', '.join(keywords),
        method=method,
        send_template=send_template
    )
    return template


def make_class_template(
    service_type,
    methods,
    attributes,
    class_doc,
    properties
):
    service_name = create_service_name(service_type)
    class_name = service_name.replace('_', '')

    cls_methods = ''
    for method_name, params in methods.items():
        keywords, send_arguments = params

        send_arguments = ''.join(
            SEND_ARGUMENT_TEMPLATE.format(
                keyword=keyword,
                value=value
            )
            for keyword, value in send_arguments
        )

        cls_methods += make_method_template(
            method_name,
            keywords,
            send_arguments
        )

    cls_properties = ''
    for property_name, items in properties.items():
        second_name, send_arguments = items

        send_arguments = ''.join(
            SEND_ARGUMENT_TEMPLATE.format(keyword=keyword, value=value)
            for keyword, value in send_arguments
        )
        cls_properties += (
            make_property_template(property_name, second_name, send_arguments)
        )


    cls_attributes = ''.join(
        STATE_TEMPLATE.format(attr_name=attribute)
        for attribute in attributes
    )

    template = CLASS_TEMPLATE.format(
        class_name=class_name,
        methods=cls_methods,
        properties=cls_properties,
        attributes=cls_attributes,
        class_doc=class_doc

    )

    return template


def make_templates(devices, services):
    if __name__ == "__main__":
        print('')
        print('')
        print('Building Templates....')

    for device_type, params in devices.items():
        device_id = params['device_id']
        device_name = create_service_name(device_type)
        class_name = device_name.replace('_', '')
        file_name = parse_string(class_name) + '.py'

        imports = []
        subclasses = []
        subclass_inits = []

        for subclass in params['subclasses']:
            subclass_name = create_service_name(subclass).replace('_', '')
            subclass_module = parse_string(subclass_name)
            subclasses += ['_' + subclass_name]

            imports += [
                DEVICE_SUBCLASS_IMPORT.format(
                    module_name=subclass_module,
                    class_name=subclass_name
                )
            ]
            subclass_inits += [
                DEVICE_SUBCLASS_INIT_TEMPLATE.format(
                    class_name=subclass_name
                )
            ]

        template = DEVICE_CLASS_TEMPLATE.format(
            device_type=device_type,
            device_id=device_id,
            class_name=class_name,
            subclasses=', '.join(subclasses),
            subclass_inits=''.join(subclass_inits),
            imports=''.join(imports)
        )

        template = template.replace(
            'self, ):',
            'self):'
        ).replace(
            ',\n        )',
            '\n        )'
        )

        file_path = os.path.join(DEVICES_PATH, file_name)

        with open(file_path, 'w') as f:
            f.write(HEADER)
            f.write(template)

    for service_type, params in services.items():
        service_name = create_service_name(service_type)
        class_name = service_name.replace('_', '')
        file_name = parse_string(class_name) + '.py'

        template = make_class_template(service_type, **params)
        template = template.replace(
            'self, ):',
            'self):'
        ).replace(
            ',\n        )',
            '\n        )'
        )

        file_path = os.path.join(SERVICES_PATH, file_name)
        if __name__ == "__main__":
            print('Writing File {0} ....'.format(file_path))

        with open(file_path, 'w') as f:
            f.write(HEADER)
            f.write(template)


def create_class_methods(
    service_xmlns,
    service_id,
    actions,
    methods,
    attributes
):
    gateway = True if service_id.find('HomeAutomationGateway') > -1 else False
    for action in actions:
        name = action.find('%sname' % service_xmlns).text
        arguments = action.find('%sargumentList' % service_xmlns)

        send_arguments = [
            ['id', "'action'"],
            ['serviceId', '%r' % service_id],
            ['action', '%r' % name],
            ['DeviceNum', 'self.id']
        ]
        keywords = []

        name = name.replace('/', '')
        if name[0].isdigit():
            name = NUMBER_MAPPING[name[0]] + name[1:]

        if arguments is not None:
            for argument in arguments:
                direction = argument.find('%sdirection' % service_xmlns)
                related = argument.find(
                    '%srelatedStateVariable' % service_xmlns
                )

                if related is not None and related.text not in attributes:
                    attributes += [related.text]

                if direction is not None and direction.text == 'in':
                    arg_name = argument.find('%sname' % service_xmlns).text

                    if arg_name in ('DeviceNum', 'DataFormat'):
                        continue

                    p_arg_name = parse_string(arg_name)
                    if p_arg_name == 'reload':
                        p_arg_name = 'lua_reload'

                    send_arguments += [[arg_name, p_arg_name]]
                    keywords += [p_arg_name]

        p_name = parse_string(name)
        if p_name == 'continue':
            p_name = 'Continue'

        if not gateway and 'DeviceNum' in attributes:
            send_arguments += [['DeviceNum', 'self.DeviceNum']]

        if p_name not in methods:
            methods[p_name] = [keywords, send_arguments]


def create_class_attributes(service_xmlns, state_variables, attributes):
    class_doc_templates = []

    for state_variable in state_variables:
        attr_name = state_variable.find('%sname' % service_xmlns).text

        data_type = state_variable.find('%sdataType' % service_xmlns).text

        data_type = DATA_TYPES.get(
            data_type,
            data_type
        )

        attr_docs = ''
        allowed_values = state_variable.find(
            '%sallowedValueList' % service_xmlns
        )
        if allowed_values is not None:
            a_values = []
            for value in allowed_values:
                a_values += [value.text]

            attr_docs += ALLOWED_VALUES_TEMPLATE.format(
                values='\n                '.join(a_values)
            )

        allowed_range = state_variable.find(
            '%sallowedValueRange' % service_xmlns
        )
        if allowed_range is not None:
            a_values = []
            for value in allowed_range:
                a_values += ['%s: %s' % (
                    value.tag.replace(
                        service_xmlns,
                        ''
                    ),
                    value.text
                )]
            attr_docs += ALLOWED_RANGE_TEMPLATE.format(
                values='\n                '.join(a_values)
            )

        second_name = attr_name.replace('.', '')

        if (attr_name, second_name) not in attributes:

            attributes += [(attr_name, second_name)]

            class_doc_templates += [
                ATTR_DOC_TEMPLATE.format(
                    attr_name=second_name,
                    attr_type=data_type,
                    attr_docs=attr_docs
                )
            ]

    return ''.join(class_doc_templates)


def discover():
    if __name__ == "__main__":
        print('Discovering Vera....')
    dest = socket.gethostbyname(SSDP_ADDR)

    def connect_sock(bind=False):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if bind:
            sock.bind((socket.gethostbyname(socket.gethostname()), 0))
        sock.sendto(SSDP_REQUEST, (dest, SSDP_PORT))
        sock.settimeout(7)

        try:
            while True:
                data, address = sock.recvfrom(1024) # buffer size is 1024 bytes
                if 'luaupnp.xml' in data:
                    return address[0]
        except socket.timeout:
            sock.close()

    ip_address = connect_sock()
    if ip_address is None:
        ip_address = connect_sock(bind=True)

    return ip_address


def get_categories(ip_address):
    response = requests.get(
        CATEGORIES.format(ip_address=ip_address),
        timeout=5
    )
    data = response.content
    data = data[data.find('CategoryNameById = {') + 19:]
    categories = eval(data[:data.find('}') + 1])

    response = requests.get(
        CATEGORY_LANG.format(ip_address=ip_address),
        timeout=5
    )

    import json
    category_mapping = json.loads(response.content[15:-1])
    out_categories = dict()

    for category_num in categories.keys()[:]:
        categories[str(category_num)] = categories.pop(category_num)

    for category_num in categories.keys()[:]:
        category_num = category_num.split('_')
        if len(category_num) == 1 or category_num[1] == '0':
            category_type = categories.pop('_'.join(category_num))
            category_name = category_mapping['Tokens'][category_type]
            category_name = category_name.replace('\\', '')
            out_categories[category_num[0]] = {'0': category_name}

    for category_num in categories.keys()[:]:
        category_type = categories.pop(category_num)
        category_num = category_num.split('_')
        category_name = category_mapping['Tokens'][category_type]
        category_name = category_name.replace('\\', '')
        out_categories[category_num[0]][category_num[1]] = category_name

    del category_mapping
    return out_categories


def get_vera_info(ip_address):
    response = requests.get(
        SYS_INFO.format(ip_address=ip_address),
        timeout=5
    )
    data = response.json()
    serial_number = data['installation_number']
    fw_version = data['firmware_version']
    zw_version = data['zwave_version']
    home_id = data['zwave_homeid']

    response = requests.get(
        VERA_INFO.format(ip_address = ip_address),
        timeout=5
    )

    xml_root = ElementTree.fromstring(response.content)

    xml_root = xml_root.find(
        '{urn:schemas-upnp-org:device-1-0}'
        'device'
    )
    manufacturer = xml_root.find(
        '{urn:schemas-upnp-org:device-1-0}'
        'manufacturer'
    ).text
    model_name = xml_root.find(
        '{urn:schemas-upnp-org:device-1-0}'
        'modelName'
    ).text
    model_number = xml_root.find(
        '{urn:schemas-upnp-org:device-1-0}'
        'modelNumber'
    ).text
    model_description = xml_root.find(
        '{urn:schemas-upnp-org:device-1-0}'
        'modelDescription'
    ).text

    return (
        manufacturer,
        model_name,
        model_number,
        model_description,
        serial_number,
        fw_version,
        zw_version,
        home_id
    )


def get_data(url):
    response = requests.get(url, timeout=5)
    response = response.content

    if 'doesn\'t exist' in response:
        return None, None

    if 'xmlns' in response:

        xmlns = (
            '{%s}' %
            response[response.find('xmlns="') + 7:response.find('">')]
        )
    else:
        xmlns = ''

    return response, xmlns


def build_files(ip_address):

    def get_data_file(data_file_name):
        return get_data(
            VIEW_UPNP_FILE.format(
                ip_address=ip_address,
                file=data_file_name
            )
        )

    found_services = invoke(ip_address)
    found_devices = dict()

    response = requests.get(
        GET_UPNP_FILES.format(ip_address=ip_address),
        timeout=5
    )
    device_files = ['vera.xml.lzo']
    service_files = []

    service_ids = dict()

    for f in response.content.split('\n'):
        if f.endswith('.xml.lzo'):
            if f.startswith('D_'):
                device_files += [f]

            elif f.startswith('S_'):
                service_files += [f]

    for device_file in device_files:
        response, root_xmlns = get_data_file(device_file)

        if response is None:
            continue

        xml_root = ElementTree.fromstring(response)
        device_type = xml_root.find('.//%sdeviceType' % root_xmlns).text

        split_type = device_type.split(':')
        split_type[3] = (
            split_type[3][:1].upper() + split_type[3][1:] + split_type[4]
        )

        device_id = ':'.join(split_type[:4])

        if device_id not in found_devices:

            found_devices[device_id] = dict(
                subclasses=[],
                device_type=device_type,
                device_id=device_id
            )

        subclasses = found_devices[device_id]['subclasses']

        services = xml_root.findall('.//*%sserviceList/' % root_xmlns)

        for service in services:
            service_type = service.find('%sserviceType' % root_xmlns).text
            service_id = service.find('%sserviceId' % root_xmlns).text
            scpd_url = service.find('%sSCPDURL' % root_xmlns).text

            if scpd_url not in service_ids:
                service_ids[scpd_url + '.lzo'] = service_type

            if service_type not in subclasses:
                subclasses += [service_type]

        found_devices[device_id]['subclasses'] = subclasses[:]

    for service_file in service_files:
        response, service_xmlns = get_data_file(service_file)

        if response is None:
            continue

        service_xml = ElementTree.fromstring(response)

        for scpd, svc_type in service_ids.items():
            if service_file == scpd:
                service_type = svc_type
                break
        else:
            service_name = service_file.replace('S_', '').replace('.xml.lzo', '')

            service_type = ''
            service_id = 'urn:micasaverde-com:serviceId:' + service_name

            while service_name[-1].isdigit():
                service_type += service_name[-1]
                service_name = service_name[:-1]

            service_type = 'urn:micasaverde-com:serviceId:' + service_name + ':' + service_type


        if service_type in found_services:
            svc = found_services[service_type]
            methods = svc['methods']
            attributes = svc['attributes']
            class_doc = svc['class_doc']
            properties = svc['properties']

        else:
            if __name__ == "__main__":
                print('-Processing ' + service_type + '.....')
            methods = dict()
            attributes = []
            class_doc = ''
            properties = dict()

        actions = service_xml.find('%sactionList' % service_xmlns)

        if actions is not None:
            create_class_methods(
                service_xmlns,
                service_id,
                actions,
                methods,
                attributes
            )

        state_variables = service_xml.find(
            '%sserviceStateTable' % service_xmlns
        )
        if state_variables is not None:
            docs = create_class_attributes(
                service_xmlns,
                state_variables,
                attributes
            )
            class_doc += docs

        found_services[service_id] = dict(
            methods=methods,
            attributes=attributes,
            class_doc=class_doc,
            properties=properties,
        )


    make_templates(found_devices, found_services)


def invoke(ip_address):
    url = 'http://{ip}:3480/data_request'.format(ip=ip_address)

    response = requests.get(url, params=dict(id='invoke'))
    data = response.content
    services = dict()

    for line in data.split('\n'):
        found_device = line.find('<a href=')
        if found_device > -1:
            line = (
                line[found_device + 9:line.find('">')].replace(
                    'lu_invoke',
                    'invoke'
                )
            )
            if 'RunScene' not in line:
                service_type = ''
                response = requests.get(
                    'http://{ip}:3480/{path}'.format(ip=ip_address, path=line)
                )
                device_data = response.content
                methods = dict()
                attributes = []
                properties = dict()
                class_doc = ''
                for device_line in device_data.split('\n'):
                    command_found = device_line.find('<a href=')
                    found_service = device_line.find('<br><i>')
                    if found_service > -1:
                        if service_type:
                            services[service_type] = dict(
                                methods=methods,
                                attributes=attributes,
                                class_doc=class_doc,
                                properties=properties
                            )

                            methods = dict()
                            attributes = []
                            class_doc = ''
                            properties = dict()

                        service_id = (
                            device_line[found_service + 7: device_line.find('</i>')]
                        )

                        service_type = ''
                        while service_id[-1].isdigit():
                            service_type = service_type + service_id[-1]
                            service_id = service_id[:-1]

                        service_type = service_id + ':' + service_type
                        service_id += service_type.split(':')[-1]

                        if service_type in services:
                            svc = services[service_type]
                            methods = svc['methods']
                            attributes = svc['attributes']
                            class_doc = svc['class_doc']
                            properties = svc['properties']
                        else:
                            if __name__ == "__main__":
                                print('-Processing ' + service_type + '.....')
                            services[service_type] = dict()

                    if command_found > -1:
                        send_arguments = []
                        method = []
                        keywords = []

                        command_line = device_line[command_found + 9:]
                        command = command_line[:command_line.find('">')]

                        command = command.replace(
                            'lu_variableset',
                            'variableset'
                        ).replace(
                            'data_request?',
                            ''
                        ).split('&')

                        params = dict(
                            list(
                                tuple(param.split('=', 1))
                                for param in command
                            )
                        )

                        for key in sorted(params.keys()[:]):
                            value = params[key]
                            if not value:
                                value = parse_string(key)
                                if value == 'reload':
                                    value = 'lua_reload'
                                if key == 'Value':
                                    value = 'value'
                                keywords += [value]

                            elif key == 'Value':
                                value = 'value'
                                keywords += [value]
                            elif key == 'DeviceNum':
                                value = 'self.id'
                            else:
                                value = '%r' % value

                            send_arguments += [[key, value]]

                        if params['id'] == 'action':
                            method_name = parse_string(params['action'])
                            if method_name not in methods:
                                methods[method_name] = [
                                    keywords,
                                    send_arguments
                                ]

                        if params['id'] == 'variableset':
                            property_name = params['Variable'].replace('.', '')
                            if property_name not in properties:
                                properties[property_name] = [
                                    params['Variable'],
                                    send_arguments
                                ]

                            if (
                                (params['Variable'], property_name)
                                not in attributes
                            ):
                                attributes += [
                                    (params['Variable'], property_name)
                                ]



                if service_type:
                    svc = services[service_type]
                    svc['methods'] = methods
                    svc['attributes'] = attributes
                    svc['class_doc'] = class_doc
                    svc['properties'] = properties
    return services

def main(ip_address=''):
    if not ip_address:
        ip_address = discover()

    if ip_address is not None:
        (
            manufacturer,
            model_name,
            model_number,
            model_description,
            serial_number,
            fw_version,
            zw_version,
            home_id
        ) = get_vera_info(ip_address)

        print('-' * 13 + ' Vera Located ' + '-' * 13)
        print('')
        print('-Manufacturer: ' + manufacturer)
        print('-Model Name: ' + model_name)
        print('-Model Number: ' + model_number)
        print('-Model Description: ' + model_description)
        print('-Serial Number: ' + serial_number)
        print('-Firmware Version: ' + fw_version)
        print('-ZWave Version: ' + zw_version)
        print('-Home Id: ' + home_id)
        print('-' * 40)
        print('')

        print('Building Categories....')
        categories = get_categories(ip_address)

        print('')
        print('')
        print('Building Classes....')

        build_files(ip_address)

if __name__ == "__main__":
    ip = raw_input(
        'input ip address of vera\n'
        'or leave blank for auto discovery\n'
    )
    main(ip)