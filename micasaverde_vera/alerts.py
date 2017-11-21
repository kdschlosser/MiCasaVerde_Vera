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

from event import EventHandler


class Alerts(object):
    _alerts = []

    def __init__(self, parent, node):
        self._parent = parent
        self._bindings = []

        if node is not None:
            for alert in node:
                self._alerts += [Alert(self, alert)]
                
    def register_event(self, callback, attribute=None):
        self._bindings += [EventHandler(self, callback, None)]
        return self._bindings[-1]

    def unregister_event(self, event_handler):
        if event_handler in self._bindings:
            self._bindings.remove(event_handler)

    def get_room(self, room):
        return self._parent.get_room(room)

    def get_device(self, device):
        return self._parent.get_device(device)

    def __iter__(self):
        alerts = sorted(self._alerts, key=lambda x: x.LocalTimestamp)
        for alert in alerts:
            yield alert

    def update_node(self, node, full=False):
        if node is not None:
            alerts = []
            for alert in node:
                timestamp = alert['LocalTimestamp']
                for found_alert in self._alerts[:]:
                    if found_alert.LocalTimestamp == timestamp:
                        self._alerts.remove(found_alert)
                        break
                else:
                    found_alert = Alert(self, alert)
                    for event_handler in self._bindings:
                        event_handler('new', alert=found_alert)
                    
                alerts += [found_alert]

            if full:
                del self._alerts[:]

            self._alerts += alerts[:]

class Alert(object):
    PK_Alert = ""
    DeviceName = ""
    Code = ""
    Room = 10
    Server_Storage = ""
    EventType = 16
    Users = ""
    Severity = 5
    PK_Device = 0
    Argument = 0
    PK_Store = ""
    DeviceType = ""
    Filesize = 0
    Key = ""
    LocalTimestamp = 0
    Description = ""
    Icon = ""
    LocalDate = ""
    NewValue = ""
    SourceType = 0

    def __init__(self, parent, node):
        self._parent = parent
        
        self._room = node.pop('Room', None)
        
        for key, value in node.items():
            self.__dict__[key] = value

    @property
    def Device(self):
        return self._parent.get_device(self.PK_Device)

    @property
    def Room(self):
        return self._parent.get_room(self._room)
    
    def __setattr__(self, key, value):
        if key.startswith('_'):
            object.__setattr__(self, key, value)
        
        raise AttributeError('The attribute {0} cannot be set.'.format(key))




