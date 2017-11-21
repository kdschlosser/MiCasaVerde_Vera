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


class EventHandler(object):

    def __init__(self, parent, callback, attribute):
        self._parent = parent
        self._callback = callback
        self._attribute = attribute
        self._last_event = dict()

    def __call__(self, event_type, **kwargs):
        if self._attribute is None:
            self._last_event.clear()
            self._last_event['event_type'] = event_type
            for key, value in kwargs.items():
                self._last_event[key] = value

            self._callback(self)

        else:
            if (
                'attribute' in kwargs and
                kwargs['attribute'] == self._attribute
            ):
                self._last_event.clear()
                self._last_event['event_type'] = event_type
                for key, value in kwargs.items():
                    self._last_event[key] = value

                self._callback(self)
                
    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        if item in self._last_event:
            return self._last_event[item]

        if item.startswith('_'):
            raise AttributeError

        return None

    def unregister(self):
        self._parent.unregister_event(self)
