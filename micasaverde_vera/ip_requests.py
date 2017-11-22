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


"""
<ip_requests>
    <ip_request mac="44:74:6C:B8:0D:F2" ip="192.168.1.65" date="1507633407"></ip_request>
</ip_requests>
"""

from event import EventHandler


class IPRequests(object):
    _ip_requests = dict()

    def __init__(self, parent, node):
        self._parent = parent
        self._bindings = []

        if node is not None:
            for request in node:
                request = IPRequest(self, request)
                if request.ip not in self._ip_requests:
                    self._ip_requests[request.ip] = []
                self._ip_requests[request.ip] += [request]

    def __iter__(self):
        for request in self._ip_requests.values():
            yield request

    def register_event(self, callback, attribute=None):
        self._bindings += [EventHandler(self, callback, None)]
        return self._bindings[-1]

    def unregister_event(self, event_handler):
        if event_handler in self._bindings:
            self._bindings.remove(event_handler)


    def update_node(self, node, full=False):
        if node is not None:
            requests = dict()
            for request in node:
                ip = request['ip']
                date = request['date']
                found_request = self._ip_requests.get(ip, None)
                if found_request is None:
                    found_request = IPRequest(self, request)

                    for event_handler in self._bindings:
                        event_handler('new', ip_request=found_request)

                    found_request = [found_request]

                else:
                    found_date = date
                    for sub_request in found_request:
                        found_date = max([found_date, sub_request.date])

                    if found_date == date:
                        found_request += [IPRequest(self, request)]

                        for event_handler in self._bindings:
                            event_handler('new', ip_request=found_request[-1])

                requests[ip] = found_request

            if full:
                self._ip_requests.clear()

            for ip, request in requests.items():
                self._ip_requests[ip] = request

class IPRequest(object):
    def __init__(self, parent, node):
        self._parent = parent
        for key, value in node.items():
            self.__dict__[key] = value

    def register_event(self, callback, attribute=None):
        return self._parent.register_event(callback)

    def unregister_event(self, event_handler):
        self._parent.unregister_event(event_handler)
