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

from __future__ import print_function
import os
import socket
import requests
import json
import threading
import random
import xml.etree.cElementTree as ElementTree
import time
from utils import parse_string, create_service_name, CRC32_from_file
from constants import (
    SSDP_MX,
    SSDP_ST,
    SSDP_ADDR,
    SSDP_PORT,
    CORE_PATH,
    DEVICES_PATH,
    SERVICES_PATH,
    DATA_TYPES,
    NUMBER_MAPPING,
    GET_UPNP_FILES,
    VIEW_UPNP_FILE,
    SYS_INFO,
    CATEGORIES,
    CATEGORY_LANG,
    VERA_INFO,
    VERSION
)
from build_templates import (
    SSDP_REQUEST,
    CONTROLLER_INFO_TEMPLATE,
    DEVICE_SUBCLASS_IMPORT,
    DEVICE_SUBCLASS_INIT_TEMPLATE,
    DEVICE_CLASS_TEMPLATE,
    CLASS_TEMPLATE,
    ATTR_DOC_TEMPLATE,
    STATE_TEMPLATE,
    ALLOWED_VALUES_TEMPLATE,
    ALLOWED_RANGE_TEMPLATE,
    ARGUMENT_TEMPLATE,
    METHOD_ARGUMENT_TEMPLATE,
    SERVICE_SEND_TEMPLATE,
    SERVICE_SEND_ARGUMENT_TEMPLATE,
    SEND_TEMPLATE,
    SEND_ARGUMENT_TEMPLATE,
    PROPERTY_TEMPLATE,
    METHOD_TEMPLATE,
    HEADER_TEMPLATE
)


def processing(indent, p_type, name):
    print('{0}-Processing {1} {2}.....'.format(indent, p_type, name))


def create_build_folder(path, file_data):
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, '__init__.py'), 'w') as f:
        f.write(file_data)


def write_file(file_path, template):
    if __name__ == "__main__":
        print('Writing File {0} ....'.format(file_path))

    if os.path.exists(file_path):
        try:
            os.rename(file_path, file_path)
        except OSError:
            return

    with open(file_path, 'w') as f:
        f.write(HEADER_TEMPLATE)
        f.write(template)


def get_data(template, ip_address, **params):
    url = template.format(ip_address=ip_address)
    try:
        response = requests.get(url, params=params, timeout=1)
    except (requests.ConnectionError, requests.Timeout):
        time.sleep(random.randrange(1, 3) / 10)
        return get_data(template, ip_address, **params)

    response = response.content

    if 'doesn\'t exist' in response:
        return None, None

    if 'xmlns' in response:
        xmlns = '{{{0}}}'.format(
            response[response.find('xmlns="') + 7:response.find('">')]
        )

    else:
        xmlns = ''

    return response, xmlns


def convert_id_to_type(in_id):
    in_id[2] = 'service'

    if len(in_id) == 5:
        return ':'.join(in_id)

    out_id = in_id[-1]
    out_type = ''
    while out_id[-1].isdigit():
        out_type = out_id[-1] + out_type
        out_id = out_id[:-1]

    return ':'.join(in_id[:-1] + [out_id, out_type])


def convert_type_to_id(in_type):
    in_type = in_type.replace('schemas-', '')
    in_type = in_type.split(':')

    if len(in_type) == 3:
        in_type.insert(2, 'deviceId')
    else:
        in_type[2] = 'deviceId'

    if len(in_type) == 4:
        return ':'.join(in_type)

    in_type[3] = (
        in_type[3][:1].upper() + in_type[3][1:] + in_type[4]
    )
    return ':'.join(in_type[:4])


def make_class_template(
    class_name,
    methods,
    attributes,
    class_doc,
    properties,
    service_id,
    service_type
):

    cls_methods = ''
    argument_mappings = ''
    for method_name, params in methods.items():
        keywords = params['keywords']
        send_arguments = params['send_arguments']
        method_argument_mapping = params['method_argument_mapping']

        method_argument_mapping['arguments'] = ''.join(
            ARGUMENT_TEMPLATE.format(**argument)
            for argument in method_argument_mapping['arguments']
        )
        argument_mappings += (
            METHOD_ARGUMENT_TEMPLATE.format(**method_argument_mapping)
        )
        send_argument_template = SEND_ARGUMENT_TEMPLATE
        send_template = SEND_TEMPLATE
        use_return = 'return '

        for key, value in send_arguments[:]:
            if key == 'serviceId' and value != 'service_id':
                send_arguments.remove([key, value])
                send_argument_template = SERVICE_SEND_ARGUMENT_TEMPLATE
                send_template = SERVICE_SEND_TEMPLATE.format(
                    second_name=method_argument_mapping['orig_method_name']
                )
                use_return = ''
                break

        send_arguments = ''.join(
            send_argument_template.format(
                keyword=keyword,
                value=value
            )
            for keyword, value in send_arguments
        )

        template = METHOD_TEMPLATE + send_template
        template = template.format(
            keywords=', '.join(keywords),
            method=method_name,
            send_arguments=send_arguments,
            use_return=use_return
        )

        cls_methods += template

    cls_properties = ''

    for property_name, items in properties.items():
        second_name, send_arguments = items

        send_argument_template = SEND_ARGUMENT_TEMPLATE
        send_template = SEND_TEMPLATE

        for key, value in send_arguments[:]:
            if key == 'serviceId':
                send_arguments.remove([key, value])
                send_argument_template = SERVICE_SEND_ARGUMENT_TEMPLATE
                send_template = SERVICE_SEND_TEMPLATE.format(
                    second_name=second_name
                )
                break

        send_arguments = ''.join(
            send_argument_template.format(keyword=keyword, value=value)
            for keyword, value in send_arguments
        )
        template = PROPERTY_TEMPLATE + send_template
        template = template.format(
            method=property_name,
            second_name=second_name,
            send_arguments=send_arguments,
            use_return=''
        )

        cls_properties += template

    cls_attributes = ''.join(
        STATE_TEMPLATE.format(
            attr_name=attr_name,
            orig_attr_name=orig_attr_name
        )
        for attr_name, orig_attr_name in attributes
    )

    template = CLASS_TEMPLATE.format(
        argument_mappings=argument_mappings,
        class_name=class_name,
        methods=cls_methods,
        properties=cls_properties,
        attributes=cls_attributes,
        class_doc=class_doc,
        service_id=service_id,
        service_type=service_type

    )

    return template


def make_templates(devices, services):
    if __name__ == "__main__":
        print()
        print()
        print('Building Templates....')

    create_build_folder(
        CORE_PATH,
        'VERSION = {0}\n'.format(VERSION)
    )
    create_build_folder(DEVICES_PATH, '')
    create_build_folder(SERVICES_PATH, '')

    for params in devices.values():
        device_type = params['device_type']
        device_id = params['device_id']
        class_name = params['device_class_name']
        file_path = params['device_gen_file']

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

        write_file(file_path, template)

    for service_name, params in services.items():
        class_name = params.pop('service_class_name')
        file_path = params.pop('service_gen_file')

        template = make_class_template(class_name, **params)
        template = template.replace(
            'self, ):',
            'self):'
        ).replace(
            ',\n        )',
            '\n        )'
        )

        write_file(file_path, template)

    with open(os.path.join(CORE_PATH, '__init__.py'), 'a') as f:
        f.write('\n\nclass Devices(object):\n')
        for module_file in os.listdir(DEVICES_PATH):
            if module_file.endswith('.pyc'):
                continue
            if module_file == '__init__.py':
                continue
            file_path = os.path.join(DEVICES_PATH, module_file)
            crc_data = CRC32_from_file(file_path)
            f.write(
                '    {0} = \'{1}\'\n'.format(
                    module_file.replace('.py', ''),
                    crc_data
                )
            )

        f.write('\n\nclass Services(object):\n')
        for module_file in os.listdir(SERVICES_PATH):
            if module_file.endswith('.pyc'):
                continue
            if module_file == '__init__.py':
                continue
            file_path = os.path.join(SERVICES_PATH, module_file)
            crc_data = CRC32_from_file(file_path)
            f.write(
                '    {0} = \'{1}\'\n'.format(
                    module_file.replace('.py', ''),
                    crc_data
                )
            )


def create_class_methods(
    service_xmlns,
    service_id,
    actions,
    methods,
    attributes
):
    gateway = True if service_id.find('HomeAutomationGateway') > -1 else False
    for action in actions:
        orig_method_name = action.find('%sname' % service_xmlns).text
        method_name = parse_string(orig_method_name)

        if method_name in ('get_name', 'set_name'):
            continue

        if method_name == 'continue':
            method_name = 'Continue'

        if method_name == 'poll':
            method_name = 'poll_device'

        method_name = method_name.replace('/', '')

        for number, replacement in NUMBER_MAPPING.items():
            if method_name.startswith(number):
                method_name = replacement + method_name[len(number):]

        if __name__ == '__main__':
            processing('    ', 'method', method_name)

        if gateway:
            send_arguments = [
                ['id', "'action'"],
                ['serviceId', '%r' % service_id],
                ['action', '%r' % orig_method_name],
            ]

        else:
            send_arguments = [
                ['id', "'action'"],
                ['serviceId', '%r' % service_id],
                ['action', '%r' % orig_method_name],
                ['DeviceNum', 'self.id']
            ]
        keywords = []
        method_argument_mapping = dict(
            method_name=method_name,
            orig_method_name=orig_method_name
        )
        argument_mapping = []

        arguments = action.find('%sargumentList' % service_xmlns)

        if arguments is not None:

            for argument in arguments:
                direction = argument.find('%sdirection' % service_xmlns)

                if direction is not None:
                    if direction.text == 'out':
                        related_variable = argument.find(
                            '%srelatedStateVariable' % service_xmlns
                        )
                        if related_variable is not None:
                            attr_name = related_variable.text
                            orig_attr_name = related_variable.text
                            if (attr_name, orig_attr_name) not in attributes:
                                attributes += [(attr_name, orig_attr_name)]

                    if direction.text == 'in':
                        orig_variable_name = (
                            argument.find('%sname' % service_xmlns).text
                        )

                        if orig_variable_name == 'DataFormat':
                            continue

                        if not gateway and orig_variable_name == 'DeviceNum':
                            continue

                        if orig_variable_name == 'serviceId' and gateway:
                            send_arguments.remove(
                                ['serviceId', '%r' % service_id]
                            )

                        variable_name = parse_string(orig_variable_name)
                        if variable_name == 'reload':
                            variable_name = 'lua_reload'

                        send_arguments += [[orig_variable_name, variable_name]]
                        keywords += [variable_name]
                        argument_mapping += [
                            dict(
                                argument_name=variable_name,
                                orig_argument_name=orig_variable_name
                            )
                        ]

        method_argument_mapping['arguments'] = argument_mapping
        if method_name not in methods:
            methods[method_name] = dict(
                keywords=keywords,
                send_arguments=send_arguments,
                method_argument_mapping=method_argument_mapping
            )


def create_class_attributes(
    service_xmlns,
    service_id,
    state_variables,
    attributes,
    properties
):
    class_doc_templates = []

    for state_variable in state_variables:
        attr_name = state_variable.find('%sname' % service_xmlns).text

        if __name__ == '__main__':
            processing('    ', 'attribute', attr_name)

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

        orig_attr_name = attr_name

        attr_name = attr_name.replace('.', '')

        if attr_name != 'Name' and attr_name not in properties:

            send_arguments = [
                ['DeviceNum', 'self.id'],
                ['Value', 'value'],
                ['Variable', repr(str(orig_attr_name))],
                ['id', "'variableset'"],
                ['serviceId', repr(str(service_id))]
            ]

            properties[attr_name] = [
                orig_attr_name,
                send_arguments
            ]

        if (attr_name, orig_attr_name) not in attributes:

            attributes += [(attr_name, orig_attr_name)]

            class_doc_templates += [
                ATTR_DOC_TEMPLATE.format(
                    attr_name=attr_name,
                    attr_type=data_type,
                    attr_docs=attr_docs
                )
            ]

    return ''.join(class_doc_templates)


def discover():
    if __name__ == "__main__":
        print('Discovering Vera....')

    ssdp_request = SSDP_REQUEST.format(SSDP_MX, SSDP_ST, SSDP_ADDR, SSDP_PORT)
    dest = socket.gethostbyname(SSDP_ADDR)

    def connect_sock(bind=False):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if bind:
            sock.bind((socket.gethostbyname(socket.gethostname()), 0))
        sock.sendto(ssdp_request, (dest, SSDP_PORT))
        sock.settimeout(7)

        try:
            while True:
                data, address = sock.recvfrom(1024)
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
    if __name__ == '__main__':

        print(
            ' Category |'
            ' Category Name               |'
            ' Subcategory |'
            ' Subcategory Name'
        )
        print('=' * 88)

        for key in sorted(out_categories.keys(), key=int):
            value = out_categories[key]
            print(' ' + str(key) + ' ' * (11 - len(str(key))) + value['0'])
            for k in sorted(value.keys(), key=int)[1:]:
                print(' ' * 42 + str(k) + ' ' * (14 - len(str(k))) + value[k])
    return out_categories


def get_vera_info(ip_address):
    import json

    response, _ = get_data(SYS_INFO, ip_address)
    data = json.loads(response)

    response, xmlns = get_data(VERA_INFO, ip_address)
    xml = ElementTree.fromstring(response)

    def find(tag):
        return xml.find('{0}{1}'.format(xmlns, tag))
    xml = find('device')

    return (
        ip_address,
        find('manufacturer').text,
        find('modelName').text,
        find('modelNumber').text,
        find('modelDescription').text,
        data['installation_number'],
        data['firmware_version'],
        data['zwave_version'],
        data['zwave_homeid']
    )


def get_files(ip_address):
    device_files = {}
    service_files = {}
    downloaded_files = {}

    threads = []
    lock = threading.Lock()

    def get_thread(xml_file_name):
        if xml_file_name.startswith('I_'):
            threads.remove(threading.currentThread())
            return

        if __name__ == '__main__':
            print('-Retreiving File', xml_file_name)

        response, xmlns = get_data(
            VIEW_UPNP_FILE,
            ip_address,
            file=xml_file_name
        )
        if response is None:
            downloaded_files[xml_file_name] = None
        else:
            xml = ElementTree.fromstring(response)

            dev_type = xml.find(
                './/%sdeviceType' % xmlns
            )

            lock.acquire()

            if dev_type is not None:
                device_files[xml_file_name] = dict(
                    device_type=dev_type.text,
                    device_xml=xml,
                    device_xmlns=xmlns
                )
            else:
                service_files[xml_file_name] = dict(
                    service_xml=xml,
                    service_xmlns=xmlns
                )
            lock.release()

        threads.remove(threading.currentThread())

    for f in get_data(GET_UPNP_FILES, ip_address)[0].split('\n'):
        if f.endswith('.xml.lzo'):
            while len(threads) > 9:
                pass

            t = threading.Thread(target=get_thread, args=(f,))
            threads += [t]
            t.start()

    while threads:
        pass

    for device_params in device_files.values():
        device_xml = device_params['device_xml']
        device_xmlns = device_params['device_xmlns']
        device_type = device_params['device_type']
        device_id = convert_type_to_id(device_type)
        device_name = create_service_name(device_type)
        device_class_name = device_name.replace('_', '')
        device_class_name = (
            device_class_name[0].upper() + device_class_name[1:]
        )
        device_file_name = parse_string(device_class_name) + '.py'

        device_params.update(
            dict(
                device_id=device_id,
                device_name=device_name,
                device_class_name=device_class_name,
                device_file_name=device_file_name,
                services=[]
            )
        )

        services = device_xml.findall('.//*%sserviceList/' % device_xmlns)

        implementations = device_xml.findall(
            './/*%simplementationList/' % device_xmlns
        )

        for implementation in implementations:
            implementation = implementation.text + '.lzo'
            if implementation in service_files:
                device_params['services'] += [implementation]

        for service in services:
            service_type = service.find(
                '%sserviceType' % device_xmlns
            ).text
            service_id = service.find('%sserviceId' % device_xmlns).text

            if service_type.endswith(':'):
                service_type += '1'
                if not service_id.endswith('1'):
                    service_id += '1'

            service_name = create_service_name(service_id)
            service_class_name = service_name.replace('_', '')
            service_file_name = parse_string(service_class_name) + '.py'

            scpd_url = (
                service.find('%sSCPDURL' % device_xmlns).text + '.lzo'
            )

            scpd_url = scpd_url.replace('/dri/', '')

            if scpd_url in service_files:
                device_params['services'] += [scpd_url]

                if 'service_type' not in service_files[scpd_url]:
                    service_params = service_files[scpd_url]
                    service_params.update(
                        dict(
                            service_type=service_type,
                            service_id=service_id,
                            service_name=service_name,
                            service_class_name=service_class_name,
                            service_file_name=service_file_name
                        )
                    )

    return device_files, service_files


def build_files(ip_address, log=False, update=False):

    if log:
        # noinspection PyGlobalUndefined
        global __name__
        __name__ = '__main__'

    if __name__ == '__main__':
        print(CONTROLLER_INFO_TEMPLATE.format(*get_vera_info(ip_address)))
        print('Building Device and Service Files....')

    device_files, service_files = get_files(ip_address)

    found_services = dict()
    found_devices = dict()

    def build_service(
        service_type,
        service_id,
        service_name,
        service_xml,
        service_xmlns,
        service_class_name,
        service_gen_file
    ):

        if service_name in found_services:
            svc = found_services[service_name]
            methods = svc['methods']
            attributes = svc['attributes']
            class_doc = svc['class_doc']
            properties = svc['properties']

        else:
            if __name__ == "__main__":
                processing('', 'service', service_id)
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
                service_id,
                state_variables,
                attributes,
                properties
            )
            class_doc += docs

        found_services[service_name] = dict(
            service_type=service_type,
            service_id=service_id,
            service_class_name=service_class_name,
            service_gen_file=service_gen_file,
            methods=methods,
            attributes=attributes,
            class_doc=class_doc,
            properties=properties,

        )

    for scpd_url, service_params in service_files.items():

        if 'service_type' not in service_params:
            svc_name = scpd_url.replace('S_', '').replace('.xml.lzo', '')
            svc_id = 'urn:micasaverde-com:serviceId:' + svc_name
            svc_type = convert_id_to_type(svc_id.split(':'))
            svc_class_name = svc_name.replace('_', '')
            svc_file_name = parse_string(svc_class_name) + '.py'
            svc_xml = service_params['service_xml']
            svc_xmlns = service_params['service_xmlns']

            svc_gen_file = os.path.join(
                SERVICES_PATH,
                svc_file_name
            )

            service_params.update(
                dict(
                    service_type=svc_type,
                    service_id=svc_id,
                    service_name=svc_name,
                    service_class_name=svc_class_name,
                    service_gen_file=svc_gen_file
                )
            )

            save_service = (
                not update or
                (update and not os.path.exists(svc_gen_file))
            )

            if not save_service and update and __name__ == "__main__":
                print('-File Exists', svc_gen_file)

            if save_service:
                build_service(
                    service_type=svc_type,
                    service_id=svc_id,
                    service_name=svc_name,
                    service_xml=svc_xml,
                    service_xmlns=svc_xmlns,
                    service_class_name=svc_class_name,
                    service_gen_file=svc_gen_file
                )

    for device_file in device_files.keys()[:]:
        device_data = device_files[device_file]
        if not device_data:
            del device_files[device_file]
            continue
        device_type = device_data['device_type']
        device_id = device_data['device_id']
        device_name = device_data['device_name']
        device_class_name = device_data['device_class_name']
        device_file_name = device_data['device_file_name']
        services = device_data['services']

        device_gen_file = os.path.join(
            DEVICES_PATH,
            device_file_name
        )

        save_device = (
            not update or (update and not os.path.exists(device_gen_file))
        )

        if not save_device and update and __name__ == "__main__":
            print('-File Exists', device_gen_file)

        if save_device:
            if device_type not in found_devices:
                if __name__ == '__main__':
                    processing('', 'device', device_type)

                found_devices[device_type] = dict(
                    subclasses=[],
                    device_type=device_type,
                    device_id=device_id,
                    device_name=device_name,
                    device_class_name=device_class_name,
                    device_gen_file=device_gen_file
                )

            subclasses = found_devices[device_type]['subclasses']
        else:
            subclasses = []

        for scpd_url in services:
            service_data = service_files[scpd_url]
            if 'service_gen_file' in service_data:
                svc_type = service_data['service_type']
            else:
                svc_type = service_data['service_type']
                svc_id = service_data['service_id']
                svc_name = service_data['service_name']
                svc_class_name = service_data['service_class_name']
                svc_file_name = service_data['service_file_name']
                svc_xml = service_data['service_xml']
                svc_xmlns = service_data['service_xmlns']

                svc_gen_file = os.path.join(
                    SERVICES_PATH,
                    svc_file_name
                )

                save_service = (
                    not update or
                    (update and not os.path.exists(svc_gen_file))
                )

                if not save_service and update and __name__ == "__main__":
                    print('-File Exists', svc_gen_file)

                if save_service:
                    build_service(
                        service_type=svc_type,
                        service_id=svc_id,
                        service_name=svc_name,
                        service_xml=svc_xml,
                        service_xmlns=svc_xmlns,
                        service_class_name=svc_class_name,
                        service_gen_file=svc_gen_file
                    )

            if save_device:
                if svc_type not in subclasses:
                    subclasses += [svc_type]

        if save_device:
            found_devices[device_type]['subclasses'] = subclasses[:]

    make_templates(found_devices, found_services)


def main(ip_address=''):
    if not ip_address:
        ip_address = discover()

    if ip_address is not None:
        build_files(ip_address)
        print('Building Categories....')
        get_categories(ip_address)


if __name__ == "__main__":
    ip = raw_input(
        'input ip address of vera\n'
        'or leave blank for auto discovery\n'
    )
    main(ip)
