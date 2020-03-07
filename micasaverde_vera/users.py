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
:synopsis: users

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

import logging
import threading
from .event import Notify
from . import utils

logger = logging.getLogger(__name__)


class Users(object):

    def __init__(self, parent, node):
        self.__lock = threading.RLock()
        self._parent = parent
        self.send = parent.send
        self._users = []

        if node is not None:
            for user in node:
                self._users += [User(self, user)]

    def __iter__(self):
        with self.__lock:
            for user in self._users:
                yield user

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

            for user in self._users:
                name = getattr(user, 'name', None)
                if name is not None and name.replace(' ', '_').lower() == item:
                    return user
                if item in (user.id, user.name):
                    return user

            if isinstance(item, int):
                raise IndexError

            raise KeyError

    @utils.logit
    def update_node(self, node, full=False):
        with self.__lock:
            if node is not None:
                users = []
                for user in node:
                    # noinspection PyShadowingBuiltins
                    id = user['id']
                    for found_user in self._users:
                        if found_user.id == id:
                            found_user.update_node(user)
                            self._users.remove(found_user)
                            break

                    else:
                        found_user = User(self, user)

                    users += [found_user]

                if full:
                    for user in self._users:
                        Notify(user, user.build_event() + '.removed')
                    del self._users[:]

                self._users += users


class User(object):
    def __init__(self, parent, node):
        self.__lock = threading.RLock()
        self._parent = parent

        def get(attr):
            return node.pop(attr, None)

        self.id = get('id')
        self._name = get('Name')

        for key, value in node.items():
            self.__dict__[key] = value

        Notify(self, self.build_event() + '.created')

    def build_event(self):
        return 'users.{0}'.format(self.id)

    @property
    def name(self):
        with self.__lock:
            return self._name

    @name.setter
    def name(self, name):
        with self.__lock:
            self._parent.send(
                id='user',
                action='rename',
                user=self.id,
                name=name
            )

    @property
    def ishome(self):
        with self.__lock:
            return self._parent.user_settings[self.id].ishome

    @property
    def geofences(self):
        with self.__lock:
            return self._parent.user_geofences[self.id]

    @utils.logit
    def update_node(self, node):
        with self.__lock:
            for key, value in node.items():
                if key in ('Name', 'name'):
                    old_value = self._name
                else:
                    old_value = getattr(self, key, None)

                if old_value != value:
                    if key in ('Name', 'name'):
                        self._name = value
                    else:
                        setattr(self, key, value)
                    Notify(
                        self,
                        self.build_event() + '.{0}.changed'.format(key)
                    )
