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


class UserGeofences(object):

    def __init__(self, parent, node):
        self._parent = parent
        self.send = parent.send
        self._geofences = []

        if node is not None:
            for geofence in node:
                self._geofences += [UserGeoFence(self, geofence)]

    def __iter__(self):
        for geofence in self._geofences:
            yield geofence

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        try:
            return self[item]
        except (KeyError, IndexError):
            raise AttributeError

    def __getitem__(self, item):
        item = str(item)
        if item.isdigit():
            item = int(item)

        for geofence in self._geofences:
            if item == geofence.iduser:
                return geofence

        if isinstance(item, int):
            raise IndexError

        raise KeyError

    def update_node(self, node, full=False):
        if node is not None:
            geofences = []

            for geofence in node:
                iduser = geofence['iduser']
                for found_geofence in self._geofences[:]:
                    if found_geofence.iduser == iduser:
                        found_geofence.update_node(geofence, full)
                        self._geofences.remove(found_geofence)
                        break
                else:
                    found_geofence = UserGeoFence(self, geofence)

                geofences += [found_geofence]
            if full:
                for geofence in self._geofences:
                    Notify(geofence, geofence.build_event() + '.removed')
                del self._geofences[:]

            self._geofences += geofences


class GeoTag(object):
    def __init__(self, parent, node):
        self._parent = parent
        self.id = node.pop('id', None)
        self.name = node.pop('name', None)

        for key, value in node.items():
            self.__dict__[key] = value

        Notify(self, self.build_event() + '.created')

    @property
    def user(self):
        return self._parent.user

    def update_node(self, node):

        for key, value in node.items():
            old_value = getattr(self, key, None)

            if old_value != value:
                setattr(self, key, value)
                Notify(self, self.build_event() + '.{0}.changed'.format(key))

    def build_event(self):
        return self._parent.build_event() + '.geotags.{0}'.format(self.id)


class GeoTags(object):

    def __init__(self, parent, node):

        self.geotags = []

        for geotag in node.pop('geotags', []):
            self.geotags += [GeoTag(parent, geotag)]

    def __iter__(self):
        for geotag in self.geotags:
            yield geotag

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        try:
            return self[item]
        except (KeyError, IndexError):
            raise AttributeError

    def __getitem__(self, item):
        item = str(item)
        if item.isdigit():
            item = int(item)

        for geotag in self.geotags:
            if item in (geotag.name, geotag.id):
                return geotag

        if isinstance(item, int):
            raise IndexError

        raise KeyError

    def update_node(self, node, full):
        geotags = []

        for geotag in node.pop('geotags', []):
            # noinspection PyShadowingBuiltins
            id = geotag['id']

            for found_geotag in self.geotags[:]:
                if found_geotag.id == id:
                    found_geotag.update_node(geotag)
                    self.geotags.remove(found_geotag)
                    break
            else:
                found_geotag = GeoTag(self, geotag)
            geotags += [found_geotag]

        if full:
            for geotag in self.geotags:
                Notify(geotag, geotag.build_event() + '.removed')
            del self.geotags[:]

        self.geotags += geotags


class UserGeoFence(object):

    def __init__(self, parent, node):
        self._parent = parent
        self.iduser = node.pop('iduser', None)
        self.geotags = GeoTags(self, node.pop('geotags', []))

        for key, value in node.items:
            self.__dict__[key] = value

        Notify(self, self.build_event() + '.created')

    def build_event(self):
        return 'user_geofence.{0}'.format(self.iduser)

    def update_node(self, node, full):
        self.geotags.update_node(node.pop('geotags', []), full)
        for key, value in node.items():
            old_value = getattr(self, key, None)
            if old_value != value:
                setattr(self, key, value)
                Notify(self, self.build_event() + '.{0}.changed'.format(key))

    @property
    def user(self):
        return self._parent.users[self.iduser]
