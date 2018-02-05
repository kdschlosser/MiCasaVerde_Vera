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
from event import Notify


class IPRequests(object):

    def __init__(self, ha_gateway, node):
        self.__lock = threading.RLock()
        self.ha_gateway = ha_gateway
        self._ip_requests = dict()

        if node is not None:
            for request in node:
                request = IPRequest(self, request)
                if request.ip not in self._ip_requests:
                    self._ip_requests[request.ip.replace('.', '-')] = []
                self._ip_requests[request.ip.replace('.', '-')] += [request]

    def __iter__(self):
        with self.__lock:
            for request in self._ip_requests.values():
                yield request

    def __getattr__(self, item):
        with self.__lock:
            if item in self.__dict__:
                return self.__dict__[item]

            try:
                return self._ip_requests[item.replace('.', '-')]
            except KeyError:
                raise AttributeError

    def __getitem__(self, item):
        with self.__lock:
            return self._ip_requests[item]

    def update_node(self, node, full=False):
        with self.__lock:
            if node is not None:
                requests = dict()
                for request in node:
                    ip = request['ip'].replace('.', '-')
                    if ip not in requests:
                        requests[ip] = []

                    date = request['date']

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
