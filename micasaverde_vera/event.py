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


from fnmatch import fnmatch


class _NotificationHandler(object):

    def __init__(self):
        self._callbacks = {}

    def bind(self, event, callback):
        if event not in self._callbacks:
            self._callbacks[event] = []

        event_handler = EventHandler(event, callback)
        self._callbacks[event] += [event_handler]
        return event_handler

    def unbind(self, event_handler):
        event = event_handler.event
        if event in self._callbacks:
            if event_handler in self._callbacks[event]:
                self._callbacks[event].remove(event_handler)
                if not self._callbacks[event]:
                    del self._callbacks[event]

    def notify(self, event_object, event):
        for event_name, event_handlers in self._callbacks.items():
            if '*' in event_name or '?' in event_name:
                if fnmatch(event, event_name):
                    for event_handler in event_handlers:
                        event_handler.event = event
                        event_handler.event_object = event_object
            elif event_name == event:
                for event_handler in event_handlers:
                    event_handler.event = event
                    event_handler.event_object = event_object

NotificationHandler = _NotificationHandler()
Notify = NotificationHandler.notify


class EventHandler(object):

    def __init__(self, event, callback):
        self.__event = event
        self.__event_name = None
        self.__callback = callback
        self.__event_object = None

    @property
    def event(self):
        return self.__event if self.__event_name is None else self.__event_name

    @event.setter
    def event(self, event):
        self.__event_name = event

    def event_object(self, event_object):
        self.__event_object = event_object
        self.__callback(self)

    event_object = property(fset=event_object)

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        return getattr(self.__event_object, item)

    def unbind(self):
        NotificationHandler.unbind(self)
