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
:synopsis: ip requests

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""


import threading
import logging
from .event import Notify
from . import utils

logger = logging.getLogger(__name__)


class IPRequests(object):

    def __init__(self, ha_gateway, node):
        self.__lock = threading.RLock()
        self.ha_gateway = ha_gateway
        self._ip_requests = dict()

        if node is not None:
            for request in node:
                request = IPRequest(self, request)
                if request.ip not in self._ip_requests:
                    self._ip_requests[request.ip] = []
                self._ip_requests[request.ip] += [request]

    def __iter__(self):
        with self.__lock:
            for request in self._ip_requests.values():
                yield request

    def __getattr__(self, item):
        with self.__lock:
            if item in self.__dict__:
                return self.__dict__[item]

            try:
                return self._ip_requests[item.replace('-', '.')]
            except KeyError:
                raise AttributeError

    def __getitem__(self, item):
        with self.__lock:
            return self._ip_requests[item.replace('-', '.')]

    @utils.logit
    def update_node(self, node, _=False):
        with self.__lock:
            if node is not None:
                requests = dict()
                for request in node:
                    ip = request['ip']
                    date = request['date']
                    if ip not in requests:
                        requests[ip] = []

                    sub_requests = self._ip_requests.get(ip, [])
                    for found_request in sub_requests:
                        if found_request.date == date:
                            sub_requests.remove(found_request)
                            break
                    else:
                        found_request = IPRequest(self, request)
                    requests[ip] += [found_request]

                self._ip_requests.clear()

                for ip, requests in requests.items():
                    self._ip_requests[ip] = list(
                        request for request in requests
                    )


class IPRequest(object):

    def __init__(self, parent, node):
        self._parent = parent
        self.ip = node.pop('ip', None)

        for key, value in node.items():
            self.__dict__[key] = value

        Notify(self, self.build_event() + '.created')

    def build_event(self):
        return 'ip_requests.{0}'.format(self.ip.replace('.', '-'))
