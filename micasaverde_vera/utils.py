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
import imp
import os
import sys
import binascii
from constants import CORE_PATH


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
