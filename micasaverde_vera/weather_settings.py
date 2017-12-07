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


from event import Notify


class WeatherSettings(object):
    def __init__(self, parent, node):
        self._parent = parent
        self.send = parent.send

        if node is not None:
            def get(attr):
                return node.pop(attr, None)

            self.name = 'Weather Setting'
            self._tempFormat = get('tempFormat')
            self._weatherCity = get('weatherCity')
            self._weatherCountry = get('weatherCountry')

            for key, value in node.items():
                self.__dict__[key] = value

    @property
    def tempFormat(self):
        return self._tempFormat

    @tempFormat.setter
    def tempFormat(self, temp_format):
        self._parent.send(
            serviceId='urn:micasaverde-com:serviceId:HomeAutomationGateway1',
            Value=temp_format,
            Variable='tempFormat',
            id='variableset',
        )

    @property
    def weatherCity(self):
        return self._weatherCity

    @weatherCity.setter
    def weatherCity(self, weather_city):
        self._parent.send(
            serviceId='urn:micasaverde-com:serviceId:HomeAutomationGateway1',
            Value=weather_city,
            Variable='weatherCity',
            id='variableset',
        )

    @property
    def weatherCountry(self):
        return self._weatherCountry

    @weatherCountry.setter
    def weatherCountry(self, weather_country):
        self._parent.send(
            serviceId='urn:micasaverde-com:serviceId:HomeAutomationGateway1',
            Value=weather_country,
            Variable='weatherCountry',
            id='variableset',
        )

    def update_node(self, node, _):
        if node is not None:
            for key, value in node.items():

                if key == 'weatherCountry':
                    old_value = self._weatherCountry
                elif key == 'weatherCity':
                    old_value = self._weatherCity
                elif key == 'tempFormat':
                    old_value = self._tempFormat
                else:
                    old_value = getattr(self, key, None)

                if old_value != value:
                    if key == 'weatherCountry':
                        self._weatherCountry = value
                    elif key == 'weatherCity':
                        self._weatherCity = value
                    elif key == 'tempFormat':
                        self._tempFormat = value
                    else:
                        setattr(self, key, value)
                    Notify(self, 'weather_setting.{0}.changed'.format(key))
