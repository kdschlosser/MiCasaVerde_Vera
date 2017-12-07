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

    def __init__(self, ha_gateway, node):
        self.ha_gateway = ha_gateway
        self._alerts = []

        if node is not None:
            for alert in node:
                self._alerts += [Alert(self, alert)]

    def __iter__(self):
        alerts = sorted(self._alerts, key=lambda x: x.LocalTimestamp)
        for alert in alerts:
            yield alert

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        try:
            return self[item]
        except IndexError:
            raise AttributeError

    def __getitem__(self, item):
        item = str(item)
        if item.isdigit():
            item = int(item)

            for alert in self._alerts:
                if item == alert.LocalTimestamp:
                    return alert
            raise IndexError
        raise KeyError

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

    def __init__(self, parent, node):
        self._parent = parent
        self.PK_Alert = node.pop('PK_Alert', None)
        self.Room = node.pop('Room', None)
        self.PK_Device = node.pop('PK_Device', None)
        self.LocalTimestamp = node.pop('LocalTimestamp', None)

        for k, v in node.items():
            self.__dict__[k] = v

        Notify(self, self.build_event() + '.created')

    def build_event(self):
        return 'alerts.{0}'.format(self.PK_Alert)

    @property
    def device(self):
        return self._parent.ha_gateway.devices[self.PK_Device]

    @property
    def room(self):
        return self._parent.ha_gateway.rooms[self.Room]
