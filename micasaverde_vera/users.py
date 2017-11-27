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


class Users(object):

    def __init__(self, parent, node):
        self._parent = parent
        self.send = parent.send
        self._users = []

        if node is not None:
            for user in node:
                self._users += [User(self, user)]

    def get_user(self, number):

        number = str(number)
        if number.isdigit():
            number = int(number)

        for user in self._users:
            if number in (user.name, user.id):
                return user

    def ishome(self, number):
        return self._parent.ishome(number)

    def get_geofences(self, number):
        return self._parent.get_geofences(number)

    def update_node(self, node, full=False):

        if node is not None:
            users = []
            for user in node:
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
                    Notify(user, 'User.{0}.Removed'.format(user.id))
                del self._users[:]

            self._users += users


class User(object):
    def __init__(self, parent, node):
        self._parent = parent
        self._bindings = []

        def get(attr):
            return node.pop(attr, None)

        self.id = get('id')
        self.Level = get('Level')
        self.IsGuest = get('IsGuest')
        self._name = get('Name')

        for key, value in node.items():
            self.__dict__[key] = value

        Notify(self, 'User.{0}.Created'.format(self.id))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._parent.send(
            id='user',
            action='rename',
            user=self.id,
            name=name
        )

    @property
    def ishome(self):
        return self._parent.ishome(self.id)

    @property
    def geofences(self):
        return self._parent.get_geofences(self.id)

    def update_node(self, node):

        for key, value in node.items():
            if key == 'Name':
                old_value = self._name
            else:
                old_value = getattr(self, key, None)

            if old_value != value:
                Notify(self, 'User.{0}.{1}.Changed'.format(self.id, key))

                if key == 'Name':
                    self._name = value
                else:
                    setattr(self, key, value)
