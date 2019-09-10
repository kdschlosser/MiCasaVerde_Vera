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
# noinspection PyDeprecation
import imp
import os
import binascii
import importlib
from .constants import CORE_PATH
from .vera_exception import VeraImportError


def parse_string(word):
    next_to_last_char = ''
    last_char = ''
    new_word = ''
    for char in word:
        if last_char and (char.isupper() or char.isdigit()):
            if last_char == '_':
                new_word = new_word[:-1]
            elif (
                last_char.isupper() and
                next_to_last_char and
                next_to_last_char.isupper()
            ):
                new_word = new_word[:-2] + last_char.lower()
            new_word += '_'

        elif char == '_' and last_char.isupper():
            new_word = new_word[:-2] + last_char.lower()
        new_word += char.lower()
        next_to_last_char = last_char
        last_char = char
    if last_char.isupper():
        new_word = new_word[:-2] + last_char.lower()
    return new_word


def service_id_to_service_type(service_id):
    service = service_id.replace('serviceId', 'service')
    service = service.replace('urn:', 'urn:schemas-')

    char = service[-1]
    service = service[:-1]
    while char.isdigit():
        char = service[-1] + char
        service = service[:-1]

    service += char[0]
    char = char[1:]
    return service + ':' + char


def create_service_name(service_type):
    service_type = service_type.split(':')

    if len(service_type) == 5:
        return ''.join(service_type[-2:]).replace('-', '_')
    else:
        return service_type[-1].replace('-', '')


def print_list(l, indent):
    for item in l:
        if isinstance(item, list):
            if len(item) > 2:
                print(indent + '[')
                print_list(item, indent + '    ')
                print(indent + ']')
            else:
                print(indent + repr(item))
        else:
            print(indent + repr(item))


def print_dict(d, indent=''):
    for key in sorted(d.keys()):
        value = d[key]
        if isinstance(value, dict):
            print(indent + key + ':')
            print_dict(value, indent + '    ')
        elif isinstance(value, list):
            print(indent + key + ':')
            print_list(value, indent + '    ')
        else:
            print(indent + key + ':', value)


# noinspection PyPep8Naming
def CRC32_from_file(file_path):
    with open(file_path, 'rb') as f:
        crc = (binascii.crc32(f.read()) & 0xFFFFFFFF)
    return "%08X" % crc


def init_core():
    core = imp.load_source(
        'micasaverde_vera.core',
        os.path.join(CORE_PATH, '__init__.py')
    )
    core.__name__ = 'micasaverde_vera.core'
    core.__path__ = [CORE_PATH]
    core.__package__ = 'micasaverde_vera'
    return core


def import_device(device_type):
    try:
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

        return device_cls
    except VeraImportError:
        return None


def import_service(service_id):
    service_type = service_id_to_service_type(service_id)
    cls_name = create_service_name(service_type)
    mod_name = parse_string(cls_name)

    try:
        service_mod = importlib.import_module(
            'micasaverde_vera.core.services.' + mod_name
        )
        service_cls_name = cls_name[:1].upper() + cls_name[1:]
        service_cls = getattr(
            service_mod,
            service_cls_name.replace('_', '')
        )
        return service_cls

    except VeraImportError:
        return None


def copy_dict(mapping, storage):
    for key, value in mapping.items():
        if isinstance(value, dict):
            storage[key] = dict()
            copy_dict(value, storage[key])
        else:
            storage[key] = value
