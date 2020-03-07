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
:synopsis: constants

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

import os
import sys

VERSION = (0, 5, 9)
PY3 = sys.version_info[0] > 2

if os.name == 'nt':
    BUILD_PATH = os.path.join(
        os.path.expandvars('%APPDATA%'),
        'MiCasaVerde_Vera'
    )

else:
    BUILD_PATH = os.path.join(os.path.expanduser('~'), '.MiCasaVerde_Vera')

CORE_PATH = os.path.join(BUILD_PATH, 'core')
DEVICES_PATH = os.path.join(CORE_PATH, 'devices')
SERVICES_PATH = os.path.join(CORE_PATH, 'services')

SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900
SSDP_MX = 10
SSDP_ST = "upnp:rootdevice"

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

UNWANTED_ITEMS = (
    'static_data',
    'InstalledPlugins',
    'SetupDevices',
    'SetupDevices',
    'category_filter',
    'categories',
    'startup'
)

URL = '/cgi-bin/cmh/'
GET_UPNP_FILES = URL + 'get_upnp_files.sh'
VIEW_UPNP_FILE = URL + 'view_upnp_file.sh'
SYS_INFO = URL + 'sysinfo.sh'
CATEGORIES = '/cmh/js/config/constants.js'
CATEGORY_LANG = '/cmh/js/config/lang.js'
VERA_INFO = '/upnp/vera.xml'

