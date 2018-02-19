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

from fnmatch import fnmatchcase
import threading


class _NotificationHandler(object):

    def __init__(self):
        self._callbacks = {}
        self.event_callback_threads = True

    def bind(self, event, callback):
        event = event.lower()
        if event not in self._callbacks:
            self._callbacks[event] = []

        event_handler = EventHandler(event, callback)
        self._callbacks[event] += [event_handler]
        return event_handler

    def unbind(self, event_handler):
        event = event_handler.event_name
        if event in self._callbacks:
            if event_handler in self._callbacks[event]:
                self._callbacks[event].remove(event_handler)
                if not self._callbacks[event]:
                    del self._callbacks[event]

    def notify(self, event_object, event):
        for event_name, event_handlers in self._callbacks.items():
            if fnmatchcase(event.lower(), event_name):
                for event_handler in event_handlers:
                    event_handler.event = event
                    event_handler.event_object = event_object


NotificationHandler = _NotificationHandler()
Notify = NotificationHandler.notify


class EventHandler(object):

    def __init__(self, event_name, callback, event_handler=None):
        self.__event = None
        self.event_name = event_name
        self.__callback = callback
        self.__event_object = None

        if event_handler is None:
            event_handler = self
        self.__event_handler = event_handler

    @property
    def event(self):
        return self.event_name if self.__event is None else self.__event

    @event.setter
    def event(self, event):
        self.__event = event

    def _run_in_thread(self, event_object):
        self.__event_object = event_object
        t = threading.Thread(target=self.__callback, args=(self,))
        t.daemon = True
        t.start()

    def event_object(self, event_object):
        if NotificationHandler.event_callback_threads:
            event = self.copy()
            event.event = self.__event
            event._run_in_thread(event_object)
        else:
            self.__event_object = event_object
            self.__callback(self)

    event_object = property(fset=event_object)

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        return getattr(self.__event_object, item)

    def unbind(self):
        NotificationHandler.unbind(self.__event_handler)

    def copy(self):
        return EventHandler(
            self.event_name,
            self.__callback,
            self.__event_handler
        )
