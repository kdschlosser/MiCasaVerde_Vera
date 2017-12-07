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


class IPRequests(object):

    def __init__(self, ha_gateway, node):
        self.ha_gateway = ha_gateway
        self._ip_requests = dict()

        if node is not None:
            for request in node:
                request = IPRequest(self, request)
                if request.ip not in self._ip_requests:
                    self._ip_requests[request.ip] = []
                self._ip_requests[request.ip] += [request]

    def __iter__(self):
        for request in self._ip_requests.values():
            yield request

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        try:
            return self[item]
        except KeyError:
            raise AttributeError

    def __getitem__(self, item):
        return self._ip_requests[item]

    def update_node(self, node, full=False):
        if node is not None:
            requests = dict()
            for request in node:
                ip = request['ip']
                date = request['date']
                found_request = self._ip_requests.get(ip, [])
                found_date = date
                for sub_request in found_request:
                    found_date = max([found_date, sub_request.date])

                if found_date == date:
                    found_request += [IPRequest(self, request)]

                requests[ip] = found_request

            if full:
                self._ip_requests.clear()

            for ip, request in requests.items():
                self._ip_requests[ip] = request


class IPRequest(object):

    def __init__(self, parent, node):
        self._parent = parent
        self.ip = node.pop('ip', None)

        for key, value in node.items():
            self.__dict__[key] = value

        Notify(self, self.build_event() + '.created')

    def build_event(self):
        return 'ip_requests.{0}'.format(self.ip.replace('.', '-'))
