# -*- coding: utf-8 -*-

# **micasaverde_vera** is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# **micasaverde_vera** is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-openzwave. If not, see http://www.gnu.org/licenses.

"""
This file is part of the **micasaverde_vera**
project https://github.com/kdschlosser/MiCasaVerde_Vera.

:platform: Unix, Windows, OSX
:license: GPL(v3)
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
