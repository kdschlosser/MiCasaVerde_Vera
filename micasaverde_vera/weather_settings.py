# -*- coding: utf-8 -*-

# **micasaverde_vera** is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# **micasaverde_vera** is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-openzwave. If not, see http://www.gnu.org/licenses.

"""
This file is part of the **micasaverde_vera**
project https://github.com/kdschlosser/MiCasaVerde_Vera.

:platform: Unix, Windows, OSX
:license: GPL(v3)
:synopsis: weather

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

import logging
import threading
from .event import Notify
from . import utils


logger = logging.getLogger(__name__)


# noinspection PyPep8Naming
class WeatherSettings(object):
    def __init__(self, parent, node):
        self.__lock = threading.RLock()
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
        with self.__lock:
            return self._tempFormat

    @tempFormat.setter
    def tempFormat(self, temp_format):
        with self.__lock:
            self._parent.send(
                serviceId=(
                    'urn:micasaverde-com:serviceId:HomeAutomationGateway1'
                ),
                Value=temp_format,
                Variable='tempFormat',
                id='variableset',
            )

    @property
    def weatherCity(self):
        with self.__lock:
            return self._weatherCity

    @weatherCity.setter
    def weatherCity(self, weather_city):
        with self.__lock:
            self._parent.send(
                serviceId=(
                    'urn:micasaverde-com:serviceId:HomeAutomationGateway1'
                ),
                Value=weather_city,
                Variable='weatherCity',
                id='variableset',
            )

    @property
    def weatherCountry(self):
        with self.__lock:
            return self._weatherCountry

    @weatherCountry.setter
    def weatherCountry(self, weather_country):
        with self.__lock:
            self._parent.send(
                serviceId=(
                    'urn:micasaverde-com:serviceId:HomeAutomationGateway1'
                ),
                Value=weather_country,
                Variable='weatherCountry',
                id='variableset',
            )

    @utils.logit
    def update_node(self, node, _):
        with self.__lock:
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
