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
