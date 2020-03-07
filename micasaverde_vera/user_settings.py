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
:synopsis: user settings

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

import logging
import threading
from .event import Notify
from . import utils

logger = logging.getLogger(__name__)


class UserSettings(object):

    def __init__(self, parent, node):
        self.__lock = threading.RLock()
        self._parent = parent
        self.send = parent.send
        self._settings = []

        if node is not None:

            for setting in node:
                self._settings += [UserSetting(self, setting)]

    def __iter__(self):
        with self.__lock:
            for setting in self._settings:
                yield setting

    def __getattr__(self, item):
        with self.__lock:
            if item in self.__dict__:
                return self.__dict__[item]

            try:
                return self[item]
            except (KeyError, IndexError):
                raise AttributeError

    def __getitem__(self, item):
        with self.__lock:
            item = str(item)
            if item.isdigit():
                item = int(item)
                for setting in self._settings:
                    if setting.id == item:
                        return setting
                raise IndexError

            raise KeyError

    @utils.logit
    def ishome(self, number):
        with self.__lock:
            number = str(number)

            if number.isdigit():
                number = int(number)

                for setting in self._settings:
                    if number == setting.id:
                        return setting.ishome

    @utils.logit
    def get_user(self, number):
        return self._parent.user[number]

    @utils.logit
    def update_node(self, node, full=False):
        with self.__lock:
            if node is not None:
                settings = []

                for setting in node:
                    # noinspection PyShadowingBuiltins
                    id = setting['id']
                    for found_setting in self._settings[:]:
                        if found_setting.id == id:
                            found_setting.update_node(setting, full)
                            self._settings.remove(found_setting)
                            break
                    else:
                        found_setting = UserSetting(self, setting)

                    settings += [found_setting]

                if full:
                    for setting in self._settings:
                        Notify(
                            setting,
                            setting.build_event() + '.removed'
                        )
                    del self._settings[:]

                self._settings += settings


class UserSetting(object):
    def __init__(self, parent, node):
        self.__lock = threading.RLock()
        self._parent = parent

        self.id = node.pop('id', None)

        for key, value in node.items():
            self.__dict__[key] = value

        Notify(self, self.build_event() + '.created')

    @property
    def user(self):
        return self._parent.get_user(self.id)

    def build_event(self):
        return 'user_settings.{0}'.format(self.id)

    @utils.logit
    def update_node(self, node, _):
        with self.__lock:
            for key, value in node.items():
                old_value = getattr(self, key, None)
                if old_value != value:
                    setattr(self, key, value)
                    Notify(
                        self,
                        self.build_event() + '.{0}.changed'.format(key)
                    )
