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

"""<weatherSettings tempFormat="C" weatherCity="kingston upon hull england Region:" weatherCountry="united kingdom"></weatherSettings>"""

from event import EventHandler


class WeatherSettings(object):
    def __init__(self, parent, node):
        self._parent = parent
        self.send = parent.send
        self._bindings = []

        if node is not None:

            def get(attr):
                return node.pop(attr, None)

            self.name = 'Weather Setting'
            self._tempFormat = get('tempFormat')
            self._weatherCity = get('weatherCity')
            self._weatherCountry = get('weatherCountry')

            for key, value in node.items():
                self.__dict__[key] = value
                
    def register_event(self, callback, attribute=None):
        self._bindings += [EventHandler(self, callback, attribute)]
        return self._bindings[-1]

    def unregister_event(self, event_handler):
        if event_handler in self._bindings:
            self._bindings.remove(event_handler)

    @property
    def tempFormat(self):
        return self._tempFormat

    @tempFormat.setter
    def tempFormat(self, tempFormat):
        pass

    @property
    def weatherCity(self):
        return self._weatherCity

    @weatherCity.setter
    def weatherCity(self, weatherCity):
        pass

    @property
    def weatherCountry(self):
        return self._weatherCountry

    @weatherCountry.setter
    def weatherCountry(self, weatherCountry):
        pass

    def update_node(self, node, full=False):
        if node is not None:
            for key, value in node.items():
                old_value = getattr(self, key, None)
                if old_value is None:
                    for event_handler in self._bindings:
                        event_handler(
                            'new',
                            weather_setting=self,
                            attribute=key,
                            value=value
                        )
                    
                    setattr(self, key, value)
                elif old_value != value:
                    for event_handler in self._bindings:
                        event_handler(
                            'change',
                            weather_setting=self,
                            attribute=key,
                            value=value
                        )
                        
                    setattr(self, key, value)