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
:synopsis: main entry point

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>


This is the module you will use to make the connection to your Vera unit.
I have designed this system to be dynamic. It builds the code necessary to
control any device/plugin that you can attach/add to the Vera. It builds
the code based on information gotten from your Vera. This package is
roughly 3000 lines of code but will generate thousands more. The amount
generated is based on what is installed on your Vera.

When the connection to your vera is first established it will automatically
generate all code form all available information gotten from your Vera.
Some of the code files will not necessarily be used but will be available
in the event you install a device that needs them. As far as plugins are
concerned if the code necessary to interact with that plugin has not been
generated it will be upon discovery of the plugin.

This library uses upnp to attempt discovery of your Vera in the event it is
unable to you will need to pass the IP address of the unit to this class.
The upnp process does take a while to acquire the IP address. The Vera does
not respond very quickly to a upnp discovery packet. My suggestion is to
pass the constructor the IP address.

When the code files are built they are stored in the following locations.
Microsoft Windows: %APPDATA%\\Micasaverde_Vera
Linux:             ~/.MicasaVerde_Vera

In the event you have some kind of an issue. I am going to need a copy of
the files located in the coorsponding folder above. Do not worry there is
no sensitive data stored in these files. I am also going to need a copy of
the traceback.

OK so now onto the good stuff.

from micasaverde_vera import Vera

auto discover ip address:
    instance = micasaverde_vera.connect()
provide the ip address:
    instance = micasaverde_vera.connect('192.168.0.0')


to discover the Vera and return it's ip address (This is only available
before you construct the instance):
    ip_address = micasaverde_vera.discover()


to refresh the generated code files:
    micasaverde_vera.build_files('192.168.0.0')

and if you wanted to complete delete the old files and generate new ones
    micasaverde_vera.rebuild_files('192.168.0.0')

and to update the existing files in the event there are new ones.
    micasaverde_vera.update_files('192.168.0.0')

The file system is designed in a way that if newer version of this library are
installed it will automatically remove all of the old files and build new ones.
It is also designed to check for file corruption/tampering. so if the files
are not originals it will rebuild them.

You do not have to build the files directly. When you call connect the
files are automatically built if the files do not exist. Or updated if needed.
If you install say a new plugin and additional information has been added to
the Vera. The system will automatically build the files that are needed for
this new plugin.
The files will only be built once (as long as they still exist) so the first
time of running this library it will take a while to first load. On a clean
Vera with no devices or plugins. around 15 seconds. This all depends on your
computer speed as well.

The whole system is designed to give you access to everything you can do
from the UI and more. It exposes all of the variables for all of the
different devices/plugins as well as the Vera unit it's self. The variables
you are allowed to change you can change. I have also exposed any functions
that are available for devices/plugins. Things like toggling state
refreshing the Z-Wave network, polling a specific device, upgrading a
plugin. Since this is a dynamic system I am unable to give you a list of
what you can and cannot do. So your best bet is to all dir() in a specific
part of the API. I have modified the output of dir() so it will return what
is available for that specific component. Typically functions will be
lowercase and any attributes/properties will be camel case. If an attribute
cannot be set you will get an AttributeError.

to get a device you can use one of the following:
    device = vera.devices[10]
    device = vera.devices['10']
    device = vera.devices['Some Device Name']

you are also able to directly request a device by it's name as if it is an
attribute. No special characters can be in the name and any spaces have to be
replaced with an _ and the name has to be all lowercase. This is not the name
of the device on the Vera only the name when keyed in to access it.
    device = vera.devices.outside_light

the above holds true for these containers

vera.scenes
vera.installed_plugins
vera.devices
vera.rooms
vera.sections
vera.users


I have also added a nifty feature that will allow you to access a device by its
room. this can only be done at the vera instance level with the room name.

same deal as above for keying in the room name
    device = vera.outside.patio_light

if you are developing using this library you are able to use getattr and will
not have to modify the name.

if you want to list off all of the device names and device numbers that
are attached to the Vera:
    for device in vera.devices:
        print '#{0}   {1}'.format(device.id, device.name)

if you want to change the device name:
    device = vera.devices['Some Device']
    device.name = 'New Device Name'

There are cases when an attribute will have an illegal character and cannot
be called directly. One use case is with the Weather Underground plugin.
It uses variable names like Forecast.0.HighTemperature. In this example you
would use:
    device.Forecast0HighTemperature

I know of only '.'being used thus far but just in case I made the system
in such a way that in the event there are other characters used you can
still gain access to the variable by use of getattr():
    getattr(device, 'Forecast.0.HighTemperature')

The following containers are special use containers:
    vera.ip_requests
    vera.upnp_devices
    vera.alerts
    vera.user_settings
    vera.weather_settings

**Sections are used when multiple vera units are joined together.
This is where the id and name of the controller are stored


I have created 2 methods for discovering what a vera object can do.

    get_functions() - this is able to be globally used on any vera continer
    object. It will list all of the functions that are available for that
    object.

    get_variables() - Globally available. Lists off all of the available
    variables for that object.
"""

from . import logger
LOGGING_DATA_PATH = logger.LOGGING_DATA_PATH
"""
Displays the data path.
"""
LOGGING_DATA_PATH_WITH_RETURN = logger.LOGGING_DATA_PATH_WITH_RETURN
"""
Displays the data path with returned values
"""
LOGGING_TIME_FUNCTION_CALLS = logger.LOGGING_TIME_FUNCTION_CALLS
"""
Displays code execution times.
"""

logger = logger.Logger()
"""
Instance of :py:class:`micasaverde_vera.logger.Logging`
"""

import sys # NOQA
import threading # NOQA
import json # NOQA
import requests # NOQA
from copy import deepcopy # NOQA

if 'micasaverde_vera' not in sys.modules:
    sys.modules['micasaverde_vera'] = sys.modules[__name__]

from . import vera_build # NOQA
from . import utils # NOQA
from .utils import init_core  # NOQA
from .import_override import ImportOverride # NOQA
from .constants import (
    VERSION as _VERSION,
    UNWANTED_ITEMS as _UNWANTED_ITEMS,
    BUILD_PATH as _BUILD_PATH
) # NOQA
from .vera_exception import (
    VeraError,
    VeraNotFoundError,
    VeraBuildError,
    VeraNotImplementedError,
    VeraImportError,
    VeraUnsupportedByDevice
) # NOQA

__version__ = _VERSION

build_files = vera_build.build_files
discover = vera_build.discover


@utils.logit
def rebuild_files(ip_address=None, log=False):
    if not ip_address:
        ip_address = vera_build.discover()

    if ip_address:
        import shutil
        shutil.rmtree(_BUILD_PATH, ignore_errors=True)
        vera_build.build_files(ip_address, log=log)


@utils.logit
def update_files(ip_address, log=False):
    """
    Updates the vera gen files.

    It builds any missing files.

    :param ip_address: IP of the Vera
    :type ip_address: str
    :param log: Output build status to sys.stdout
    :type log: bool
    :return: None
    :rtype: None
    """
    vera_build.build_files(ip_address, log, True)


@utils.logit
def get_units(username=None, password=None):

    from .auth import Auth, Unit

    auth = Auth(username, password)

    url = 'https://{server}/info/session/token'.format(
        server=auth.server_account
    )
    header = dict(
        MMSAuth=auth.token,
        MMSAuthSig=auth.sig_token
    )
    response = requests.get(
        url,
        headers=header
    )

    session = response.content

    url = (
        'https://{server}/account/account/account/{pk_account}/devices'.format(
            server=auth.server_account,
            pk_account=auth.pk_account
        )
    )

    response = requests.get(
        url,
        headers=dict(MMSSession=session)
    )

    remote_data = json.loads(response.content)

    for device in remote_data['Devices']:
        unit = Unit()
        unit.set_remote_relay(
            auth,
            device['PK_Device'],
            device['Server_Device'],
            device['Server_Device_Alt']
        )
        yield unit


@utils.logit
def connect(ip_address=None):

    """
    MiCasaVerde Vera control entry point.

    :param ip_address: optional
    :return: micasaverde_vera.Vera
    """
    from .auth import Unit

    if ip_address is None:
        ip_address = vera_build.discover()
        print(ip_address)

        if ip_address:
            unit = Unit()
            unit.set_local_relay(ip_address)
            ip_address = unit

    def start_vera():
        if 'micasaverde_vera.core' in sys.modules:
            return sys.modules['micasaverde_vera.core']
        __path__.append(_BUILD_PATH)
        return init_core()

    def build():
        logger.info('MicasaVerde Vera: Building files please wait....')
        build_files(ip_address, log=False)
        logger.info('MicasaVerde Vera: Build complete.')

    try:
        logger.info('startin vera')
        core = start_vera()
        logger.info('core loaded')
        if (
            not hasattr(core, 'VERSION') or
            core.VERSION != __version__
        ):
            logger.info('MiCasaVerde Vera: Generated files version mismatch.')
            logger.info('                  Rebuilding files please wait....')
            rebuild_files(ip_address)
            logger.info('MiCasaVerde Vera: Build complete.')

        # noinspection PyUnresolvedReferences
        from micasaverde_vera.core.devices.home_automation_gateway_1 import (
            HomeAutomationGateway1,
        )

    except (ImportError, IOError):
        build()
        try:
            start_vera()
            # noinspection PyUnresolvedReferences
            from micasaverde_vera.core.devices.home_automation_gateway_1 \
                import HomeAutomationGateway1
        except Exception:
            import traceback

            raise VeraImportError(
                'Error Importing generated file.\n' +
                traceback.format_exc()
            )

    class __Vera(_VeraBase, HomeAutomationGateway1):

        def __init__(self, ip):
            self.__name__ = 'Vera'
            _VeraBase.__init__(self, ip)
            HomeAutomationGateway1.__init__(
                self,
                self,
                self.init_data
            )
            del self.init_data

        def __getattr__(self, item):
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
                            # noinspection PyArgumentList
                            return attr.fget(self)

                        return attr

                for room in self.rooms:
                    if room.name.replace(' ', '_').lower() == item:
                        return room

                raise VeraNotImplementedError(
                    'Attribute {0} is not supported.'.format(item)
                )
            return value

    return __Vera(ip_address)


class _VeraBase:
    """
    This is one of the 2 base classes that make up the main Vera object.

    The second class is dynamically created hence the reason why the
    voodoo magic code. I had to be crafty to be able to subclass a class that
    technically speaking doesn't exist.
    """

    VeraError = VeraError
    VeraNotFoundError = VeraNotFoundError
    VeraBuildError = VeraBuildError
    VeraNotImplementedError = VeraNotImplementedError
    VeraImportError = VeraImportError
    VeraUnsupportedByDevice = VeraUnsupportedByDevice

    _import_override = None
    id = 0

    _DataVersion = 0
    _LuaUPnPAlive = 0

    # noinspection PyUnresolvedReferences
    def __init__(self, ip_address):
        if self._import_override is None:
            self._import_override = ImportOverride(self)
            self._import_override.start()

        # noinspection PyUnresolvedReferences
        from micasaverde_vera.core.devices import home_automation_gateway_1
        from .event import NotificationHandler
        from .sections import Sections
        from .ip_requests import IPRequests
        from .weather_settings import WeatherSettings
        from .devices import Devices
        from .rooms import Rooms
        from .user_settings import UserSettings
        from .user_geofences import UserGeofences
        from .upnp_devices import UPNPDevices
        from .users import Users
        from .categories import Categories
        from .installed_plugins import InstalledPlugins
        from .alerts import Alerts
        from .vera_connect import VeraConnect

        self.ip_address = ip_address
        self._data_event = None
        self._data_wait = None
        self._data_thread = None
        self._lock = threading.Lock()
        self._queue = []

        self.vera_connection = VeraConnect(self, ip_address)
        data = self.vera_connection.send(id='user_data')

        for item in _UNWANTED_ITEMS:
            if item in data:
                del data[item]

        self.categories = Categories(
            self,
            vera_build.get_categories(ip_address)
        )

        self.scenes = None
        self.sections = self.__build(Sections, 'sections', data)
        self.users = self.__build(Users, 'users', data)
        self.devices = self.__build(Devices, 'devices', data)
        self.rooms = self.__build(Rooms, 'rooms', data)
        self.ip_requests = self.__build(IPRequests, 'ip_requests', data)
        self.upnp_devices = self.__build(UPNPDevices, 'upnp_devices', data)
        self.alerts = self.__build(Alerts, 'alerts', data)
        self.user_settings = self.__build(UserSettings, 'users_settings', data)
        self.user_geofences = self.__build(
            UserGeofences,
            'usergeofences',
            data
        )
        self.installed_plugins = self.__build(
            InstalledPlugins,
            'InstalledPlugins2',
            data
        )
        self.weather_settings = self.__build(
            WeatherSettings,
            'weatherSettings',
            data
        )

        if self.scenes is not None:
            self.__update(self.scenes, 'scenes', data)

        self.bind = NotificationHandler.bind
        self.unbind = NotificationHandler.unbind
        self.__event_handler = NotificationHandler
        self.init_data = data

    @property
    def event_callback_threads(self):
        return self.__event_handler.event_callback_threads

    @event_callback_threads.setter
    def event_callback_threads(self, flag=True):
        self.__event_handler.event_callback_threads = flag

    def update_files(self, log=False):
        """
        Updates the vera gen files.

        This is used internally but can also be used by the user. It builds
        any missing files.

        :param log: Output build status to sys.stdout
        :type log: bool
        :return: None
        :rtype: None
        """
        update_files(self.ip_address, log)

    def __build(self, obj, key, data):
        return obj(
            self,
            data.pop(key, None)
        )

    def rebuild_files(self, log=False):
        """
        Rebuilds the gen files.

        :param log: Output build status to sys.stdout
        :type log: bool
        :return: None
        :rtype: None
        """
        rebuild_files(self.ip_address, log)

    def disconnect(self):
        self.stop_polling()
        self._import_override.stop()

    # noinspection PyMethodMayBeStatic
    def __update(self, obj, key, data):
        obj.update_node(data.pop(key, None), True)

    def send(self, **kwargs):
        """
        Sends a command or query to the Vera.

        This method will send a data_request to the Vera. you simply have to
        pass the parameters that you want to send.

        example to set the dimming level of a light:
            vera.send(
                serviceId='urn:upnp-org:serviceId:Dimming1',
                id='action',
                action='SetLoadLevelTarget',
                DeviceNum=10,
                newLoadlevelTarget=25
            )

        :param kwargs: parameters to be sent
        :return: response from the Vera
        :rtype: str, json
        """

        return self.vera_connection.send(**kwargs)

    def queue_data(self, data):
        """
        Internal use.

        :param data:
        :return:
        """
        self._lock.acquire()
        self._queue += [data]
        self._lock.release()
        self._data_wait.set()

    def stop_polling(self):
        """
        Stops polling the vera for updates.

        :return:
        """
        if self._data_thread is not None:
            self._data_event.set()
            self._data_wait.set()
            self._data_thread.join(3.0)

        if self.vera_connection.is_running:
            self.vera_connection.stop_poll()

    def start_polling(self, interval=0.1):
        """
        Starts polling the vera for updates.

        :param interval: time between polling cycles in seconds.
        :type interval: float
        :return: None
        :rtype: None
        """

        if not self.vera_connection.is_running:
            del self._queue[:]
            self._data_event = threading.Event()
            self._data_wait = threading.Event()
            self._data_thread = threading.Thread(target=self._data_handler)
            self._data_thread.daemon = True
            self._data_thread.start()
            self.vera_connection.start_poll(interval)

    def get_variables(self):
        return list(
            key for key in self.__dict__.keys()
            if not key.startswith('_')
        )

    # noinspection PyMethodMayBeStatic
    def build_event(self):
        """
        Builds the event string

        Internal use.

        :return:
        """
        return 'vera'

    # noinspection PyUnresolvedReferences
    def _data_handler(self):
        """
        Internal use.

        :return:
        """
        last_data = dict()
        while not self._data_event.isSet():
            self._data_wait.clear()
            self._lock.acquire()
            while self._queue:
                data = self._queue.pop(0)

                for item in _UNWANTED_ITEMS:
                    if item in data:
                        del data[item]

                data_version = data.pop('DataVersion', self.DataVersion)
                lua_upnp_alive = data.pop('LuaUPnPAlive', self.LuaUPnPAlive)

                if data == last_data:
                    continue

                last_data = deepcopy(data)

                data['DataVersion'] = data_version
                data['LuaUPnPAlive'] = lua_upnp_alive

                self.__update(self.sections, 'sections', data)
                self.__update(self.users, 'users', data)
                self.__update(self.rooms, 'rooms', data)
                self.__update(self.devices, 'devices', data)
                self.__update(self.ip_requests, 'ip_requests', data)
                self.__update(self.upnp_devices, 'upnp_devices', data)
                self.__update(self.weather_settings, 'weatherSettings', data)
                self.__update(self.user_settings, 'users_settings', data)
                self.__update(self.user_geofences, 'usergeofences', data)
                self.__update(self.alerts, 'alerts', data)
                self.__update(
                    self.installed_plugins,
                    'InstalledPlugins2',
                    data
                )
                if self.scenes is not None:
                    self.__update(self.scenes, 'scenes', data)

                self.update_node(data, full=True)

            self._lock.release()
            self._data_wait.wait()

