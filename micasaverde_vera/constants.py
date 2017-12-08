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

VERSION = (0, 5, 4)

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

URL = 'http://{ip_address}/cgi-bin/cmh/'
GET_UPNP_FILES = URL + 'get_upnp_files.sh'
VIEW_UPNP_FILE = URL + 'view_upnp_file.sh'
SYS_INFO = URL + 'sysinfo.sh'
CATEGORIES = 'http://{ip_address}/cmh/js/config/constants.js'
CATEGORY_LANG = 'http://{ip_address}/cmh/js/config/lang.js'
VERA_INFO = 'http://{ip_address}/upnp/vera.xml'

