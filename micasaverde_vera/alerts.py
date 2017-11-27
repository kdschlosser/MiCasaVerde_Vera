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


class Alerts(object):

    def __init__(self, parent, node):
        self._parent = parent
        self._alerts = []

        if node is not None:
            for alert in node:
                self._alerts += [Alert(self, alert)]

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

                alerts += [found_alert]

            if full:
                del self._alerts[:]

            self._alerts += alerts[:]

class Alert(object):

    """
    Attributes:
        PK_Alert (str):
        DeviceName (str):
        Code (str):
        Room (int):
        Server_Storage (str):
        EventType (int):
        Users (str):
        Severity (int):
        PK_Device (int):
        Argument (int):
        PK_Store (str):
        DeviceType (str):
        Filesize (int):
        Key (str):
        LocalTimestamp (int):
        Description (str):
        Icon (str):
        LocalDate (str):
        NewValue (str):
        SourceType (int):
    """

    def __init__(self, parent, node):
        self._parent = parent

        self._room = node.pop('Room', None)

        for key, value in node.items():
            self.__dict__[key] = value

        Notify(self, 'Alert.{0}.Created'.format(self.PK_Alert))

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




