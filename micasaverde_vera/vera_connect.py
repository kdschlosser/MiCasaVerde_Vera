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
:synopsis: vera connection handler

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""


import logging
import threading
import requests
import json
import random
import time
from .event import Notify
from .vera_exception import VeraNotImplementedError, VeraUnsupportedByDevice
from . import utils
from requests import ConnectionError, Timeout, ReadTimeout, ConnectTimeout


logger = logging.getLogger(__name__)


class VeraConnect(object):
    """
    Connection handler

    I have a connection handler to the Vera so that way it manages the flow of
    information to and from the Vera as not to overload it. I am still
    tinkering with how many connections the Vera can handle at one time.
    I think I am going to have to make it so that it dynamically changes the
    number based on response time. This is because the load on the Vera is not
    going to be the same on a per user basis.
    """
    def __init__(
        self,
        parent,
        ip_address=None,
        _=None
    ):

        self._parent = parent
        self._event = threading.Event()
        self._event.set()
        self._lock = threading.Lock()
        self._thread = None
        self._data_version = 0
        self._load_time = 0
        self._connected = None
        self.URL = 'http://{0}:3480/data_request'.format(ip_address)

    @utils.logit
    def start_poll(self, interval):
        while not self._event.isSet():
            pass

        self._thread = threading.Thread(
            target=self.run_poll,
            args=(interval,)
        )
        self._thread.daemon = True
        self._thread.start()

    @utils.logit
    def stop_poll(self):
        self._event.set()
        self._thread.join(3.0)

    @utils.logit
    def run_poll(self, interval):
        self._event.clear()

        while not self._event.isSet():
            self._event.wait(interval)
            self._lock.acquire()
            try:
                response = requests.get(
                    self.URL,
                    params={'id': 'user_data'},
                    timeout=1
                )
                if not self._connected:
                    self._connected = True
                    Notify('vera.connected', self)
            except (ConnectionError, Timeout, ReadTimeout, ConnectTimeout):
                if self._connected is None:
                    self._connected = False
                elif self._connected is True:
                    self._connected = False
                    Notify('vera.disconnected', self)
                self._event.wait(random.randrange(1, 5) / 10)
            else:
                data = json.loads(response.content)
                self._parent.queue_data(data)
            finally:
                self._lock.release()

    @property
    def is_running(self):
        return not self._event.isSet()

    @utils.logit
    def send(self, **params):
        if 'output_format' not in params:
            params['output_format'] = 'json'

        self._lock.acquire()

        try:
            response = requests.get(self.URL, params=params)

            if self._connected in (None, False):
                self._connected = True
                Notify('vera.connected', self)
        except (ConnectionError, Timeout, ReadTimeout, ConnectTimeout):
            if self._connected in (True, None):
                self._connected = False
                Notify('vera.disconnected', self)
            time.sleep(random.randrange(1, 5) / 10)
        else:
            try:
                return json.loads(response.content)
            except ValueError:
                if 'ERROR' in response.content:
                    if 'No implementation' in response.content:
                        raise VeraNotImplementedError
                    if (
                        'Device does not handle service/action' in
                        response.content
                    ):
                        raise VeraUnsupportedByDevice
        finally:
            self._lock.release()
