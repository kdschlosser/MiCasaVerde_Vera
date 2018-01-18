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


import base64

# noinspection PyUnresolvedReferences
from micasaverde_vera.core.devices.scene_1 import Scene1
# noinspection PyUnresolvedReferences
from micasaverde_vera.core.devices.scene_controller_1 import SceneController1
from event import Notify
from vera_exception import VeraNotImplementedError


class Scenes(SceneController1):

    def __init__(self, ha_gateway, node):
        self.category_num = 14
        self.subcategory_num = 0
        self._scenes = []
        self.ha_gateway = ha_gateway
        self.send = ha_gateway.send

        SceneController1.__init__(self, self, node)
        SceneController1.update_node(self, node, False)

        Notify(
            self,
            'devices.{0}.created'.format(self.id)
        )

    def __iter__(self):
        for scene in self._scenes:
            yield scene

    def get_devices(self):
        return self.ha_gateway.devices

    def get_device(self, device):
        return self.ha_gateway.devices[device]

    def get_room(self, room):
        return self.ha_gateway.rooms[room]

    def get_user(self, user):
        return self.parent.users[user]

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        try:
            return self[item]
        except (KeyError, IndexError):
            return self._get_variable(item)[0]

    def __getitem__(self, item):
        item = str(item)
        if item.isdigit():
            item = int(item)

        for scene in self._scenes:
            name = getattr(scene, 'name', None)
            if name is not None and name.replace(' ', '_').lower() == item:
                return scene
            if item in (scene.name, scene.id):
                return scene

        if isinstance(item, int):
            raise IndexError
        raise KeyError

    def update_node(self, node, full=False):
        if node is not None:
            if isinstance(node, list):
                scenes = []
                for scene in node:
                    # noinspection PyShadowingBuiltins
                    id = scene['id']

                    for found_scene in self._scenes[:]:
                        if found_scene.id == id:
                            found_scene.update_node(scene, full)
                            self._scenes.remove(found_scene)
                            break
                    else:
                        found_scene = Scene(self, **scene)

                    scenes += [found_scene]

                if full:
                    for scene in self._scenes:
                        Notify(scene, scene.build_event() + '.removed')
                    del self._scenes[:]

                self._scenes += scenes

            elif isinstance(node, dict):
                SceneController1.update_node(self, node, full)


class Scene(Scene1):

    # noinspection PyShadowingBuiltins,PyPep8Naming
    def __init__(
        self,
        parent,
        id,
        last_run=0,
        room=0,
        active_on_any=0,
        modeStatus=0,
        notification_only=0,
        encoded_lua=0,
        lua='',
        name='',
        users='',
        Timestamp='',
        triggers_operator='',
        triggers=[],
        timers=[],
        groups=[],
        **kwargs
    ):
        if not name:
            name = 'NO NAME ASSIGNED'

        self.parent = parent
        self.id = id
        self._room = room
        self._name = name
        self._triggers_operator = triggers_operator
        self._users = users
        self._modeStatus = modeStatus
        self._active_on_any = active_on_any
        self.Timestamp = Timestamp
        self.last_run = last_run
        self._notification_only = notification_only
        self._encoded_lua = encoded_lua
        self._lua = lua

        Notify(self, self.build_event() + '.created')
        self.groups = Groups(self, groups)
        self.triggers = Triggers(self, triggers)
        self.timers = Timers(self, timers)
        self.category_num = 9999
        self.subcategory_num = 0
        Scene1.__init__(self, parent, {})

    def build_event(self):
        return 'scenes.{0}'.format(self.id)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self.parent.send(
            id='scene',
            action='rename',
            scene=self.id,
            name=name,
            room=self.room.id
        )

    @property
    def room(self):
        return self.parent.ha_gateway.rooms[self._room]

    @room.setter
    def room(self, room):
        from rooms import Room

        if not isinstance(room, Room):
            room = self.parent.ha_gateway.rooms[room]

        self._parent.send(
            id='scene',
            action='rename',
            scene=self.id,
            name=self.name,
            room=room.id
        )

    @property
    def encoded_lua(self):
        return self._encoded_lua

    @encoded_lua.setter
    def encoded_lua(self, encoded_lua):
        if int(encoded_lua) and not int(self._encoded_lua):
            self._lua = base64.b64encode(self._lua)

        elif not int(encoded_lua) and int(self._encoded_lua):
            self._lua = base64.b64decode(self._lua)

        self._encoded_lua = encoded_lua

    @property
    def lua(self):
        if int(self._encoded_lua):
            return base64.b64decode(self._lua)
        return self._lua

    @lua.setter
    def lua(self, lua):
        if int(self._encoded_lua):
            self._lua = base64.b64encode(lua)
        else:
            self._lua = lua

    @property
    def triggers_operator(self):
        return self._triggers_operator

    @triggers_operator.setter
    def triggers_operator(self, triggers_operator):
        self._triggers_operator = triggers_operator

    @property
    def users(self):
        return self._users

    @users.setter
    def users(self, users):
        self._users = users

    @property
    def modeStatus(self):
        return self._modeStatus

    @modeStatus.setter
    def modeStatus(self, mode_status):
        self._modeStatus = mode_status

    @property
    def active_on_any(self):
        return self._active_on_any

    @active_on_any.setter
    def active_on_any(self, active_on_any):
        self._active_on_any = active_on_any

    @property
    def notification_only(self):
        return self._notification_only

    @notification_only.setter
    def notification_only(self, notification_only):
        self._notification_only = notification_only

    def add_action_group(self, delay=0):
        self.groups += [Group(self, delay=delay)]
        return self.groups[-1]

    def stop_scene(self):
        self.parent.send(
            id='action',
            serviceId='urn:micasaverde-com:serviceId:HomeAutomationGateway1',
            action='SceneOff',
            SceneNum=self.id
        )

    def delete(self):
        self.parent.send(
            id='scene',
            action='delete',
            scene=self.id
        )

    # noinspection PyUnboundLocalVariable
    def update_node(self, node, full=False):

        _triggers = node.pop('triggers', [])
        _groups = node.pop('groups', [])
        _timers = node.pop('timers', [])

        for key, value in node.items():
            if key == 'name':
                old_value = self._name
            elif key == 'notification_only':
                old_value = self._notification_only
            elif key == 'modeStatus':
                old_value = self._modeStatus
            elif key == 'users':
                old_value = self._users
            elif key == 'room':
                old_value = self._room
            elif key == 'triggers_operator':
                old_value = self._triggers_operator
            elif key == 'active_on_any':
                old_value = self._active_on_any
            elif key == 'lua':
                old_value = self._lua
            elif key == 'encoded_lua':
                old_value = self._encoded_lua
            else:
                old_value = getattr(self, key, None)

            if old_value != value:
                if key == 'name':
                    self._name = value
                elif key == 'notification_only':
                    self._notification_only = value
                elif key == 'modeStatus':
                    self._modeStatus = value
                elif key == 'users':
                    self._users = value
                elif key == 'room':
                    self._room = value
                elif key == 'triggers_operator':
                    self._triggers_operator = value
                elif key == 'active_on_any':
                    self._active_on_any = value
                elif key == 'lua':
                    self._lua = value
                elif key == 'encoded_lua':
                    self._encoded_lua = value
                else:
                    setattr(self, key, value)

                Notify(self, self.build_event() + '.{0}.changed'.format(key))

        self.triggers.update_node(_triggers, full=full)
        self.groups.update_node(_groups, full=full)
        self.timers.update_node(_timers, full=full)


class Actions(object):
    def __init__(self, parent, scene, actions=[]):
        self.parent = parent
        self.scene = scene
        self.actions = list(
            Action(self, scene, **action) for action in actions
        )
        self.available_devices = AvailableDevices(self, scene)

    def build_event(self):
        return self.parent.build_event()

    def __iter__(self):
        return iter(self.actions)

    def new_action(self):
        self.actions += [Action(self, self.scene)]
        return self.actions[-1]

    def remove(self, action):
        if action in self.actions:
            self.actions.remove(action)

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
            return self.actions[int(item)]

        for action in self.actions:
            if item == action.action:
                return action

        raise KeyError

    def update_node(self, node, full):
        actions = []

        while node and self.actions:
            action = node.pop(0)
            found_action = self.actions.pop(0)
            found_action.update_node(action, full)
            actions += [found_action]

        for action in node:
            actions += [Action(self, self.scene, **action)]

        if full:
            for action in self.actions:
                Notify(action, action.build_event() + '.removed')
            del self.actions[:]

        self.actions += actions


class Action(object):
    def __init__(
        self,
        parent,
        scene,
        device=None,
        service='',
        action='',
        arguments=[]
    ):
        self.scene = scene
        self.parent = parent
        self.device = device
        self.service = service
        self._action = action
        Notify(self, self.build_event() + '.created')
        self.arguments = Arguments(self, arguments)

    def build_event(self):
        return self.parent.build_event() + '.actions.{0}'.format(self._action)

    @property
    def action(self):
        if not self._action:
            return 'NO NAME ASSIGNED'
        return self._action

    def new_argument(self):
        return self.arguments.new()

    def delete(self):
        Notify(self, self.build_event() + '.removed')
        self.parent.remove(self)

    def update_node(self, node, full):
        self.arguments.update_node(node.pop('arguments', []), full)

        for key, value in node.items():
            old_value = getattr(self, key, None)
            if old_value != value:
                setattr(self, key, value)
                Notify(self, self.build_event() + '.{0}.changed'.format(key))


class AvailableDevices(object):

    def __init__(self, parent, scene):
        self.parent = parent
        self.scene = scene

    def __iter__(self):
        for device in self.scene.get_devices():
            yield AvailableDevice(self.scene, device)

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        for device in self.scene.get_devices():
            if device.name == item:
                return AvailableDevice(self.scene, device)

        raise AttributeError

    def __getitem__(self, item):
        item = str(item)
        if item.isdigit():
            item = int(item)

        for device in self.scene.get_devices():
            if item in (device.id, device.name):
                return AvailableDevice(self.scene, device)

        if isinstance(item, int):
            raise IndexError

        raise KeyError


class AvailableDevice(object):

    def __init__(self, scene, device):
        self.scene = scene
        self.name = device.name
        self.id = device.id
        self._actions = []

        for params in device.argument_mapping.values():
            arguments = []
            for key, argument in params.items():
                if key == 'orig_name':
                    continue
                arguments += [
                    dict(
                        name=argument,
                        value=None
                    )
                ]

            # noinspection PyProtectedMember
            self._actions += [
                Action(
                    parent=self,
                    scene=scene,
                    action=params['orig_name'],
                    service=device._serviceId,
                    device=device.id,
                    arguments=arguments
                )
            ]

    def __iter__(self):
        return iter(self._actions)

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        for action in self._actions:
            if item == action.action:
                return action

        raise AttributeError('Action {0} not found.'.format(item))


class Groups(object):
    def __init__(self, scene, groups):
        self.scene = scene
        self.groups = []

        for group in groups:
            self.groups += [Group(self, scene, len(self.groups) + 1, **group)]

    def build_event(self):
        return self.scene.build_event()

    def __iter__(self):
        return iter(self.groups)

    def new_group(self):
        self.groups += [Group(self, self.scene, len(self.groups) + 1)]
        return self.groups[-1]

    def update_node(self, node, full):
        groups = []

        while node and self.groups:
            group = node.pop(0)
            found_group = self.groups.pop(0)
            found_group.update_node(group, full)
            groups += [found_group]

        for group in node:
            groups += [Group(self.scene, **group)]

        if full:
            for group in self.groups:
                Notify(group, group.build_event() + '.removed')
            del self.groups[:]

        self.groups += groups

    def remove(self, group):
        if group in self.groups:
            self.groups.remove(group)

    def __getitem__(self, item):
        return self.groups[item]


class Group(object):

    def __init__(self, parent, scene, id, delay=0, actions=[]):
        self.parent = parent
        self.scene = scene
        self.id = id
        self._delay = delay
        Notify(self, self.build_event() + '.created')
        self.actions = Actions(self, scene, actions)

    def build_event(self):
        return self.parent.build_event() + '.groups.{0}'.format(self.id)

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, delay):
        self._delay = delay

    def delete(self):
        Notify(
            self,
            self.build_event() + '.removed'
        )
        self.scene.groups.remove(self)

    def update_node(self, node, full):
        if self._delay != node['delay']:
            self._delay = node['delay']
            Notify(self, self.build_event() + '.delay.changed')
        self.actions.update_node(node['actions'], full)


class Triggers(object):

    def __init__(self, scene, triggers):
        self.scene = scene
        self.triggers = list(
            Trigger(self, scene, **trigger) for trigger in triggers
        )

    def build_event(self):
        return self.scene.build_event()

    def __iter__(self):
        return iter(self.triggers)

    def new_trigger(self):
        self.triggers += [Trigger(self, self.scene, '')]
        return self.triggers[-1]

    def remove(self, trigger):
        if trigger in self.triggers:
            self.triggers.remove(trigger)

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
            return self.triggers[int(item)]

        for trigger in self.triggers:
            if item == trigger.name:
                return trigger

        raise KeyError

    def update_node(self, node, full):
        triggers = []

        while node and self.triggers:
            trigger = node.pop(0)
            found_trigger = self.triggers.pop(0)

            found_trigger.update_node(trigger, full)
            triggers += [found_trigger]

        for trigger in node:
            triggers += [Trigger(self.scene, **trigger)]

        if full:
            for trigger in self.triggers:
                Notify(trigger, trigger.build_event() + '.removed')
            del self.triggers[:]

        self.triggers += triggers


class Trigger(object):
    def __init__(
        self,
        parent,
        scene,
        name,
        device=None,
        template=None,
        enabled=1,
        lua='',
        encoded_lua=0,
        arguments=[],
        last_run=0,
        last_eval=0
    ):
        if not name:
            name = 'NO NAME ASSIGNED'
        self.parent = parent
        self.scene = scene
        self._name = name
        self._device = device
        self._template = template
        self._enabled = enabled
        self._lua = lua
        self._encoded_lua = encoded_lua
        self.last_run = last_run
        self.last_eval = last_eval
        Notify(self, self.build_event() + '.created')
        self.arguments = Arguments(self, arguments)

    def build_event(self):
        return self.parent.build_event() + '.triggers.{0}'.format(self.name)

    @property
    def name(self):
        if not self._name:
            return 'NO NAME ASSIGNED'

        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def device(self):
        return self.scene.parent.get_device(self._device)

    @device.setter
    def device(self, device):
        device = self.scene.parent.get_device(device)
        if device is not None:
            self._device = device.id

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, template):
        self._template = template

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled

    @property
    def encoded_lua(self):
        return self._encoded_lua

    @encoded_lua.setter
    def encoded_lua(self, encoded_lua):
        if int(encoded_lua) and not int(self._encoded_lua):
            self._lua = base64.b64encode(self._lua)

        elif not int(encoded_lua) and int(self._encoded_lua):
            self._lua = base64.b64decode(self._lua)

        self._encoded_lua = encoded_lua

    @property
    def lua(self):
        if int(self._encoded_lua):
            return base64.b64decode(self._lua)
        return self._lua

    @lua.setter
    def lua(self, lua):
        if int(self._encoded_lua):
            self._lua = base64.b64encode(lua)
        else:
            self._lua = lua

    def new_argument(self):
        return self.arguments.new()

    def delete(self):
        Notify(self, self.build_event() + '.removed')
        self.scene.triggers.remove(self)

    def update_node(self, node, full=False):
        self.arguments.update_node(node.pop('arguments', []), full)

        for key, value in node.items():
            if key == 'device':
                old_value = self._device
            elif key == 'name':
                old_value = self._name
            elif key == 'enabled':
                old_value = self._enabled
            elif key == 'template':
                old_value = self._template
            elif key == 'lua':
                old_value = self._lua
            elif key == 'encoded_lua':
                old_value = self._encoded_lua
            else:
                old_value = getattr(self, key, None)

            if old_value != value:
                if key == 'device':
                    self._device = value
                elif key == 'name':
                    self._name = value
                elif key == 'enabled':
                    self._enabled = value
                elif key == 'template':
                    self._template = value
                elif key == 'lua':
                    self._lua = value
                elif key == 'encoded_lua':
                    self._encoded_lua = value
                else:
                    setattr(self, key, value)

                Notify(self, self.build_event() + '.{0}.changed'.format(key))


class Timers(object):

    def __init__(self, scene, timers):
        self.scene = scene
        self.timers = list(Timer(self, scene, **timer) for timer in timers)

    def new_timer(self, name):
        self.timers += [Timer(self, self.scene, len(self.timers), name)]
        return self.timers[-1]

    def build_event(self):
        return self.scene.build_event()

    def __iter__(self):
        return iter(self.timers)

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
            return self.timers[int(item)]

        for timer in self.timers:
            if timer.name == item:
                return timer

        raise KeyError

    def remove(self, timer):
        if timer in self.timers:
            self.timers.remove(timer)

    def update_node(self, node, full):
        timers = []

        for timer in node:
            # noinspection PyShadowingBuiltins
            id = timer['id']

            for found_timer in self.timers[:]:
                if found_timer.id == id:
                    found_timer.update_node(timer, full)
                    self.timers.remove(found_timer)
                    break
            else:
                found_timer = Timer(self.scene, **timer)

            timers += [found_timer]

        if full:
            for timer in self.timers:
                Notify(timer, timer.build_event() + '.removed')
            del self.timers[:]

        self.timers += timers


# noinspection PyShadowingBuiltins
class Timer(object):

    def __init__(
        self,
        parent,
        scene,
        id,
        name='',
        type='',
        enabled=1,
        days_of_week='',
        time='',
        next_run=0,
        last_run=0
    ):

        if not name:
            name = 'NO NAME ASSIGNED'
        self.parent = parent
        self.scene = scene
        self.id = id
        self._name = name
        self._type = type
        self._enabled = enabled
        self._days_of_week = days_of_week
        self._time = time
        self.next_run = next_run
        self.last_run = last_run

        Notify(self, self.build_event() + '.created')

    def build_event(self):
        return self.parent.build_event() + '.timers.{0}'.format(self.id)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled

    @property
    def days_of_week(self):
        return self._days_of_week

    @days_of_week.setter
    def days_of_week(self, days_of_week):
        self._days_of_week = days_of_week

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, time):
        self._time = time

    def delete(self):
        Notify(self, self.build_event() + '.removed')
        self.scene.timers.remove(self)

    def update_node(self, node, _):

        for key, value in node.items():
            if key == 'type':
                old_value = self._type
            elif key == 'enabled':
                old_value = self._enabled
            elif key == 'days_of_week':
                old_value = self._days_of_week
            elif key == 'time':
                old_value = self._time
            else:
                old_value = getattr(self, key, None)

            if old_value != value:
                if key == 'type':
                    self._type = value
                elif key == 'enabled':
                    self._enabled = value
                elif key == 'days_of_week':
                    self._days_of_week = value
                elif key == 'time':
                    self._time = value
                else:
                    setattr(self, key, value)

                Notify(self, self.build_event() + '.{0}.changed'.format(key))


class Arguments(object):
    def __init__(self, parent, arguments):
        self.parent = parent
        self.arguments = list(
            Argument(self, **argument) for argument in arguments
        )

    def build_event(self):
        return self.parent.build_event()

    def new(self):
        if isinstance(self.parent, Action):
            self.arguments += [
                Argument(self, name='', value=None)
            ]
        else:
            self.arguments += [
                Argument(self, id=0, value=None)
            ]
        return self.arguments[-1]

    def update_node(self, node, full):
        arguments = []
        for argument in node:
            for found_argument in self.arguments[:]:
                if isinstance(self.parent, Action):
                    if found_argument.name == argument['name']:
                        found_argument.update_node(argument, full)
                        self.arguments.remove(found_argument)
                        break

                elif found_argument.id == argument['id']:
                    found_argument.update_node(argument, full)
                    self.arguments.remove(found_argument)
                    break
            else:
                found_argument = Argument(self, **argument)
            arguments += [found_argument]

        for argument in self.arguments:
            Notify(argument, argument.build_event() + '.removed')

        del self.arguments[:]

        self.arguments += arguments

    def __instancecheck__(self, instance):
        return isinstance(self.parent, instance)

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
            for argument in self.arguments:
                if argument.id == int(item):
                    return argument
            raise IndexError

        for argument in self.arguments:
            if argument.name == item:
                return argument

        raise KeyError

    def remove(self, argument):
        if argument in self.arguments:
            self.arguments.remove(argument)


# noinspection PyShadowingBuiltins, PyUnresolvedReferences
class Argument(object):

    def __init__(self, parent, value, name=None, id=None):
        self.parent = parent
        if isinstance(self.parent.parent, Action):
            if not name:
                name = 'NO NAME ASSIGNED'
            self.name = name
        else:
            if id is None:
                id = 'NO ID ASSIGNED'
            self.id = id

        self._value = value
        Notify(self, self.build_event() + '.created')

    def build_event(self):
        if isinstance(self.parent.parent, Action):
            event = self.name
        else:
            event = self.id
        return self.parent.build_event() + '.arguments.{0}'.format(event)

    def update_node(self, node, _):
        for key, value in node.items():
            if key == 'value':
                old_value = self._value
            else:
                old_value = getattr(self, key, None)

            if old_value != value:
                Notify(self, self.build_event() + '.{0}.changed'.format(key))

            if key == 'value':
                self._value = value
            else:
                setattr(self, key, value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def delete(self):
        Notify(self, self.build_event() + '.removed')
        self.parent.remove(self)
