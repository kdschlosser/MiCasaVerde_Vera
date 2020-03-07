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
:synopsis: events

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

from fnmatch import fnmatchcase
import threading
import logging

from . import utils

logger = logging.getLogger(__name__)


class _NotificationHandler(object):

    def __init__(self):
        self._callbacks = {}
        self.event_callback_threads = True

    @utils.logit
    def bind(self, event, callback):
        event = event.lower()
        if event not in self._callbacks:
            self._callbacks[event] = []

        event_handler = EventHandler(event, callback)
        self._callbacks[event] += [event_handler]
        return event_handler

    @utils.logit
    def unbind(self, event_handler):
        event = event_handler.event_name
        if event in self._callbacks:
            if event_handler in self._callbacks[event]:
                self._callbacks[event].remove(event_handler)
                if not self._callbacks[event]:
                    del self._callbacks[event]

    @utils.logit
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

    @utils.logit
    def unbind(self):
        NotificationHandler.unbind(self.__event_handler)

    @utils.logit
    def copy(self):
        return EventHandler(
            self.event_name,
            self.__callback,
            self.__event_handler
        )
