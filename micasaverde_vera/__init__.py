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

import threading
import requests
import vera_build
import json
import sys
import os

from scenes import Scenes
from sections import Sections
from ip_requests import IPRequests
from weather_settings import WeatherSettings
from devices import Devices
from rooms import Rooms
from user_settings import UserSettings
from user_geofences import UserGeofences
from upnp_devices import UPNPDevices
from users import Users
from categories import Categories
from installed_plugins import InstalledPlugins
from alerts import Alerts
from vera_connect import VeraConnect
from vera_exception import (
    VeraError,
    VeraNotFoundError,
    VeraBuildError,
    VeraNotImplimentedError
)


BUILD_PATH = vera_build.BUILD_PATH
BUILD_COMPLETE = os.path.exists(BUILD_PATH)
build_files = vera_build.build_files



class Vera(object):
    """
    MicasaVerde Vera control entry point.
    
    This is the class you will use to make the connection to your Vera unit.
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
    Microsoft Windows: %APPDATA%\Micasaverde_Vera
    Linux:             ~/.MicasaVerde_Vera
    
    In the event you have some kind of an issue. I am going to need a copy of 
    the files located in the coorsponding folder above. Do not worry there is 
    no sensitive data stored in these files. I am also going to need a copy of 
    the traceback.
    
    OK so now onto the good stuff.
    
    from micasaverde_vera import Vera
    
    auto discover ip address:
        instance = Vera()
    provide the ip address:
        instance = Vera('192.168.0.0')
    
    
    to discover the Vera and return it's ip address (This is only available 
    before you construct the instance):
        ip_address = Vera.discover()
    
    
    to refresh the generated code files:
        Vera.build_files('192.168.0.0')
        
    You do not have to build the files directly. When you construct the 
    instance it is automatically done if the files do not exist. The files 
    will only be built once (as long as they still exist) so the first time of 
    running this library it will take a while to first load. Upwards of 45 
    seconds on a vera that only has a handful of devices and a plugin or 2.
    
    The whole system is designed to give you access to everything you can do 
    from the UI and more. It exposes all of the variables for all of the 
    different devices/plugins as well as the Vera unit it's self. The variables
    you are allowed to change you can change. I have also exposed any functions
    that are available for devices/plugins. Things like toggling state 
    refreshing the Z-Wave network, polling a specific device, upgrading a 
    plugin. Since this is a dynamic system I am unable to give you a list of 
    what you can and cannot do. So your best bet is to all dir() in a specific
    part of the API. I have modifiec the output of dir() so it will return what
    is available for that specific component. Typiclally functions will be 
    lowercase and any attributes/properties will be camel case. If an attribute
    cannot be set you will get an AttributeError.
    
    to get a device you can use one of the following:
        device = vera.get_device(10)
        device = vera.get_device('10')
        device = vera.get_device('Some Device Name')
        
    if you want to list off all of the device names and device numbers that 
    are attached to the Vera:
        for device in vera.devices:
            print '#{0}   {1}'.format(device.id, device.name)
            
    if you want to change the device name:
        device = vera.get_device('Some Device')
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
        
    The same mechanism used for the devices works for the following:
        vera.categories:
            vera.get_category(category name or category number)
        vera.sections**:
            vera.get_section(section name or section number)
        vera.users:
            vera.get_user(user name or user number)
        vera.rooms:
            vera.get_room(room name or room number)
        vera.scenes:
            vera.get_scene(scene name or scene number)
        vera.installed_plugins:
            vera.get_plugin(plugin name or plugin number)
        vera.user_geofences:
            vera.get_geofences(user name or user number)
            
    The following containers are special use containers:
        vera.ip_requests
        vera.upnp_devices
        vera.alerts
        vera.user_settings
        vera.weather_settings
        
    **Sections are used when multiple vera units are joined together. 
    This is where the id and name of the controller are stored
    
    Remember dir() is your friend for showing you what is available. Reading
    the generated code files will be of little help because not everything that
    is in those files will be available for your specific device.
    
    Things that have yet to be finished up:
        Automatic updating
        Events for changes
        Creating/Altering Scenes (testing)
        
    """

    build_files = build_files
    BUILD_PATH = BUILD_PATH
    BUILD_COMPLETE = BUILD_COMPLETE
    discover = vera_build.discover

    def __init__(self, ip_address=''):
        pass

    def __new__(cls, ip_address=''):

        if not ip_address:
            ip_address = vera_build.discover()

        if not BUILD_COMPLETE:
            print 'MicasaVerde Vera: Building files please wait....'
            build_files(ip_address)
            print 'MicasaVerde Vera: Build complete.'

        package_name = __package__

        if package_name != __name__:
            package_name += '.' + __name__

        module_name = package_name + '.core'

        if module_name not in sys.modules:
            import imp
            core = imp.new_module(module_name)
            core.__name__ = module_name
            core.__path__ = [vera_build.BUILD_PATH]
            core.__package__ = package_name
            sys.modules[module_name] = core

        from micasaverde_vera.core.devices import home_automation_gateway_1


        del home_automation_gateway_1.HomeAutomationGateway1.__setattr__

        class NewVera(_Vera, home_automation_gateway_1.HomeAutomationGateway1):
            def __init__(self, ip):
                _Vera.__init__(self, ip)
                home_automation_gateway_1.HomeAutomationGateway1.__init__(
                    self,
                    self,
                    self.init_data
                )
                del self.init_data

            def __dir__(self):
                """
                Modifies the output when using dir()

                This modifies the output when dir() is used on an instance of this 
                device. The purpose for this is not all devices will use every 
                component of this class.
                """

                dir_list = dir(self.__class__)
                dir_list += self.__dict__.keys()
                dir_list += list(
                    key for (key, value) in self._variables.items()
                        if value is not None
                )

                return sorted(set(dir_list))

        instance = super(Vera, cls).__new__(cls)
        instance.__init__()

        return NewVera(ip_address)


class _Vera(object):
    """
    This is the actual instance of Vera that gets returned.
    
    The reason this is set up this way is because there is a generated code 
    file for the Vera. and we have to generate the files before we can 
    construct the instance. 
    """

    BUILD_PATH = BUILD_PATH
    BUILD_COMPLETE = BUILD_COMPLETE
    build_files = build_files
    VeraError = VeraError
    VeraNotFoundError = VeraNotFoundError
    VeraBuildError = VeraBuildError
    VeraNotImplimentedError = VeraNotImplimentedError

    _lock = threading.Lock()
    _queue = []
    id = 0


    def __init__(self, ip_address=''):
        self._data_event = None
        self._data_wait = None
        self._data_thread = None
        self._lock = threading.Lock()

        self.vera_connection = VeraConnect(self, ip_address)
        data = self.vera_connection.send(id='user_data')

        if 'static_data' in data:
            del data['static_data']
        if 'InstalledPlugins' in data:
            del data['InstalledPlugins']
        if 'SetupDevices' in data:
            del data['SetupDevices']
        if 'category_filter' in data:
            del data['category_filter']

        self.categories = Categories(self, vera_build.get_categories(ip_address))
        self.sections = self.__build(Sections, 'sections', data)
        self.users = self.__build(Users, 'users', data)
        self.rooms = self.__build(Rooms, 'rooms', data)
        self.scenes = self.__build(Scenes, 'scenes', data)
        self.devices = self.__build(Devices, 'devices', data)
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

        self.get_section = self.sections.get_section
        self.get_category = self.categories.get_category
        self.get_user = self.users.get_user
        self.ishome = self.user_settings.ishome
        self.get_geofences = self.user_geofences.get_geofences
        self.get_room = self.rooms.get_room
        self.get_scene = self.scenes.get_scene
        self.get_device = self.devices.get_device
        self.get_plugin = self.installed_plugins.get_plugin

        self.init_data = data


    def __build(self, obj, key, data):
        return obj(
            self,
            data.pop(key, None)
        )

    def __update(self, obj, key, data):
        obj.update_node(data.pop(key, None))

    def send(self, **kwargs):
        return self.vera_connection.send(**kwargs)

    def queue_data(self, data):
        self._lock.acquire()
        self._queue += [data]
        self._lock.release()
        self._data_wait.set()

    def stop_polling(self):
        if self._data_thread is not None:
            self._data_event.set()
            self._data_wait.set()
            self._data_thread.join(3.0)

        if self.vera_connection.is_running:
            self.vera_connection.stop_poll()

    def start_polling(self, interval=0.1):
        if not self.vera_connection.is_running:
            del self._queue[:]
            self._data_event = threading.Event()
            self._data_wait = threading.Event()
            self._data_thread = threading.Thread(target=self._data_handler)
            self._data_thread.start()
            self.vera_connection.start_poll(interval)

    def _data_handler(self):
        while not self._data_event.isSet():
            self._data_wait.clear()
            self._lock.acquire()
            while self._queue:
                data = self._queue.pop(0)

                if 'static_data' in data:
                    del data['static_data']
                if 'InstalledPlugins' in data:
                    del data['InstalledPlugins']
                if 'SetupDevices' in data:
                    del data['SetupDevices']
                if 'category_filter' in data:
                    del data['category_filter']

                self.__update(self.sections, 'sections', data)
                self.__update(self.users, 'users', data)
                self.__update(self.rooms, 'rooms', data)
                self.__update(self.scenes, 'scenes', data)
                self.__update(self.devices, 'devices', data)
                self.__update(self.ip_requests, 'ip_requests', data)
                self.__update(self.upnp_devices, 'upnp_devices', data)
                self.__update(self.weather_settings, 'weatherSettings', data)
                self.__update(self.user_settings, 'users_settings', data)
                self.__update(self.user_geofences, 'usergeofences', data)
                self.__update(self.alerts, 'alerts', data)
                self.__update(self.installed_plugins, 'InstalledPlugins2', data)

            self._lock.release()
            self._data_wait.wait()



