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


class UserSettings(object):
    def __init__(self, parent, node):
        self._parent = parent
        self.send = parent.send
        self._settings = []

        if node is not None:

            for setting in node:
                self._settings += [UserSetting(self, setting)]

    def ishome(self, number):
        number = str(number)

        if number.isdigit():
            number = int(number)

        for setting in self._settings:
            if number in (setting.id, setting.name):
                return setting.ishome

    def get_user(self, number):
        return self._parent.get_user(number)

    def update_node(self, node, full=False):
        if node is not None:
            settings = []

            for setting in node:
                # noinspection PyShadowingBuiltins
                id = setting['id']

                for found_setting in self._settings[:]:
                    if found_setting.id == id:
                        self._settings.remove(found_setting)
                        break
                else:
                    found_setting = UserSetting(self, setting)

                ishome = setting.get('ishome', None)

                if ishome is not None and ishome != found_setting.ishome:
                    found_setting.ishome = ishome
                    Notify(
                        self,
                        'UserSetting.{0}.ishome.Changed'.format(
                            found_setting.id
                        )
                    )

                settings += [found_setting]

            if full:
                for setting in self._settings:
                    Notify(
                        setting,
                        'UserSetting.{0}.Removed'.format(setting.id)
                    )
                del self._settings[:]

            self._settings += settings


class UserSetting(object):
    def __init__(self, parent, node):
        self._parent = parent

        self.id = node.pop('id', None)

        for key, value in node.items():
            self.__dict__[key] = value

        Notify(self, 'UserSetting.{0}.Created'.format(self.id))

    @property
    def user(self):
        return self._parent.get_user(self.id)
