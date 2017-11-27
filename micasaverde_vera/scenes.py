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
from micasaverde_vera.core.services.scene_1 import Scene1
from micasaverde_vera.core.services.scene_controller_1 import SceneController1
from micasaverde_vera.core.services.ha_device_1 import HaDevice1
from event import Notify


class Scenes(SceneController1, HaDevice1):
    _service_id = 'urn:schemas-micasaverde-com:deviceId:SceneController1'
    _service_type = 'urn:schemas-micasaverde-com:device:SceneController:1'

    def __init__(self, parent, node):
        self._scenes = []
        self._parent = parent
        self.send = parent.send
        SceneController1.__init__(self, parent)
        HaDevice1.__init__(self, parent)

        for key, value in node.items():
            setattr(self, key, value)

        Notify(
            self,
            'Device.{0}.Created'.format(self.id)
        )

    def __iter__(self):
        return iter(self._scenes)

    def get_device(self, device):
        return self._parent.get_device(device)

    def get_room(self, room):
        return self._parent.get_room(room)

    def get_user(self, user):
        return self._parent.get_user(user)

    def get_scene(self, scene):
        if isinstance(scene, Scene):
            return scene
        scene = str(scene)
        if scene.isdigit():
            scene = int(scene)
        for s in self._scenes:
            if scene in (s.id, s.name):
                return s

    def update_node(self, node, full=False):
        if node is not None:
            if isinstance(node, list):
                scenes = []
                for scene in node:
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
                        Notify(scene, 'Scene.{0}.Removed'.format(scene.id))
                    del self._scenes[:]

                self._scenes += scenes
            elif isinstance(node, dict):
                for key, value in node.items():
                    old_value = getattr(self, key, None)

                    if old_value != value:
                        Notify(
                            self,
                            'Device.{0}.{1}.Changed'.format(self.id, key)
                        )
                        setattr(self, key, value)

class Scene(Scene1):
    _service_id = 'urn:schemas-micasaverde-com:deviceId:Scene1'
    _service_type = 'urn:schemas-micasaverde-com:device:Scene:1'

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
        groups=[]
    ):
        if not name:
            name = 'NO NAME ASSIGNED'

        self.devices = parent._parent.devices
        self._parent = parent
        self.id = id
        Notify(self, 'Scene.{0}.Created'.format(self.id))

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

        self.groups = Groups(self, groups)
        self.triggers = Triggers(self, triggers)
        self.timers = Timers(self, timers)

        Scene1.__init__(self, parent)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._parent.send(
            id='scene',
            action='rename',
            scene=self.id,
            name=name,
            room=self.room.name
        )

    @property
    def room(self):
        return self._parent.get_room(self._room)

    @room.setter
    def room(self, room):
        if isinstance(room, (int, unicode, str)):
            room = self._parent.get_room(str(room))

        self._parent.send(
            id='scene',
            action='rename',
            scene=self.id,
            name=self.name,
            room=room.name
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
    def modeStatus(self, modeStatus):
        self._modeStatus = modeStatus

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
        self._parent.send(
            id='action',
            serviceId='urn:micasaverde-com:serviceId:HomeAutomationGateway1',
            action='SceneOff',
            SceneNum=self.id
        )

    def delete(self):
        self._parent.send(
            id='scene',
            action='delete',
            scene=self.id
        )

    def update_node(self, node, full=False):
        triggers = []

        self.triggers.update_node(node.pop('triggers', []), full=full)
        self.groups.update_node(node.pop('groups', []), full=full)
        self.timers.update_node(node.pop('timers', []), full=full)

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
                Notify(self, 'Scene.{0}.{1}.Changed'.format(self.id, key))

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


class Actions(object):
    def __init__(self, parent, actions=[]):
        self._parent = parent
        self.actions = list(Action(self, **action) for action in actions)
        self.available_devices = AvailableDevices(self, parent.devices)

    def __iter__(self):
        return iter(self.actions)

    def new_action(self):
        self.actions += [Action(self)]
        return self.actions[-1]

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        for action in self.actions:
            if item == action.action:
                return action

        raise AttributeError(
            'Action {0} is not added.'.format(item)
        )

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.actions[item]

        for action in self.actions:
            if item == action.action:
                return action

        raise KeyError(
            'Action {0} is not added.'.format(item)
        )

    def update_node(self, node, full):
        actions = []


        while node and self.actions:
            action = node.pop(0)
            found_action = self.actions.pop(0)
            found_action.update_node(action, full)
            actions += [found_action]

        for action in node:
            actions += [Action(self, **action)]

        if full:
            for action in self.actions:
                Notify(
                    action,
                    'Scene.{0}.Action.{1}.Removed'.format(
                        self._parent.id,
                        action.action
                    )
                )
            del self.actions[:]

        self.actions += actions


class Action(object):
    def __init__(
        self,
        parent,
        device=None,
        service='',
        action='',
        arguments=[]
    ):

        Notify(
            self,
            'Scene.{0}.Action.{1}.Created'.format(
                parent._parent._parent.id,
                action
            )
        )

        self._parent = parent
        self.device = device
        self.service = service
        self._action = action
        self.arguments = list(
            Argument(self, **argument) for argument in arguments
        )

    @property
    def action(self):
        if not self._action:
            return 'NO NAME ASSIGNED'
        return self._action


    def new_argument(self):
        self.arguments += [
            Argument(self, name='', value=None)
        ]
        return self.arguments[-1]

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        for argument in self.arguments:
            if item == argument.name:
                return argument

        raise AttributeError(
            'No agrument named {0} for action {1}'.format(item, self.action)
        )

    def delete(self):
        Notify(
            self,
            'Scene.{0}.Action.{1}.Removed'.format(
                self._parent._parent.id,
                self.action
            )
        )
        self._parent.actions.remove(self)

    def update_node(self, node, full):
        arguments = []

        for argument in node.pop('arguments', []):
            name = argument['name']

            for found_argument in self.arguments[:]:
                if found_argument.name == name:
                    self.arguments.remove(found_argument)
                    break
            else:
                found_argument = Argument(self, **argument)

            arguments += [found_argument]

            if argument['value'] != found_argument.value:
                found_argument.value = argument['value']
                Notify(
                    found_argument,
                    'Scene.{0}.Action.{1}.Argument.{2}.Value.Changed'.format(
                        self._parent._parent.id,
                        self.action,
                        found_argument.name
                    )
                )
        if full:
            for argument in self.arguments:
                Notify(
                    argument,
                    'Scene.{0}.Action.{1}.Argument.{2}.Removed'.format(
                        self._parent._parent.id,
                        self.action,
                        argument.name
                    )
                )
            del self.arguments[:]

        self.arguments += arguments

        for key, value in node.items():
            old_value = getattr(self, key, None)
            if old_value != value:
                Notify(
                    self,
                    'Scene.{0}.Action.{1}.{2}.Changed'.format(
                        self._parent._parent.id,
                        self.action,
                        key
                    )
                )

                setattr(self, key, value)


class AvailableDevices(object):

    def __init__(self, parent, devices):
        self._parent = parent
        self._devices = devices

    def __iter__(self):
        for device in self._devices:
            yield AvailableDevice(self._parent, device)

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        for device in self._devices:
            if device.name == item:
                return AvailableDevice(self._parent, device)

        raise AttributeError

    def __getitem__(self, item):
        item = str(item)
        if item.isdigit():
            item = int(item)

        for device in self._devices:
            if item in (device.id, device.name):
                return AvailableDevice(self._parent, device)

        if isinstance(item, int):
            raise IndexError

        raise KeyError


class AvailableDevice(object):

    def __init__(self, parent, device):
        self._parent = parent
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

            self._actions += [
                Action(
                    parent=parent,
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
    def __init__(self, parent, groups):
        self._parent = parent
        self.devices = parent._parent._parent.devices
        self.groups = list(
            Group(parent, **group) for group in groups
        )

    def __iter__(self):
        return iter(self.groups)

    def new_group(self, name):
        self.groups += [Group(self)]
        return self.groups[-1]

    def update_node(self, node, full):
        groups = []

        while node and self.groups:
            group = node.pop(0)
            found_group = self.groups.pop(0)
            found_group.update_node(group, full)
            groups += [found_group]

        for group in node:
            groups += [Group(self, **group)]

        if full:
            for group in self.groups:
                Notify(
                    group,
                    'Scene.{0}.Group.Removed'.format(
                        self._parent.id
                    )
                )
            del self.groups[:]

        self.groups += groups


class Group(object):

    def __init__(self, parent, delay=0, actions=[]):
        Notify(
            self,
            'Scene.{0}.Group.Created'.format(
                parent._parent.id
            )
        )

        self._parent = parent
        self.devices = parent.devices
        self._delay = delay
        self.actions = Actions(parent, actions)

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, delay):
        self._delay = delay

    def delete(self):
        Notify(
            self,
            'Scene.{0}.Group.Removed'.format(
                self._parent._parent.id
            )
        )
        self._parent.groups.remove(self)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.actions[item]

        return self.actions[item]

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        for action in self.actions:
            if action.action == item:
                return action

        raise AttributeError(
            'Scene {0} does not have action {1}'.format(self._parent.id, item)
        )

    def update_node(self, node, full):
        if self._delay != node['delay']:
            self._delay = node['delay']
            Notify(
                self,
                'Scene.{0}.Group.Delay.Changed'.format(
                    self._parent._parent.id
                )
            )
        self.actions.update_node(node['actions'], full)


class Triggers(object):

    def __init__(self, parent, triggers):
        self._parent = parent
        self.triggers = list(
            Trigger(self, **trigger) for trigger in triggers
        )

    def __iter__(self):
        return iter(self.triggers)

    def new_trigger(self):
        self.triggers += [Trigger(self, '')]
        return self.triggers[-1]

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        for trigger in self.triggers:
            if trigger.name == item:
                return trigger

        raise AttributeError

    def update_node(self, node, full):
        triggers = []

        while node and self.triggers:
            trigger = node.pop(0)
            found_trigger = self.triggers.pop(0)

            found_trigger.update_node(trigger, full)
            triggers += [found_trigger]

        for trigger in node:
            triggers += [Trigger(self, **trigger)]

        if full:
            for trigger in self.triggers:
                Notify(
                    trigger,
                    'Scene.{0}.Trigger.{1}.Removed'.format(
                        self._parent.id,
                        trigger.name
                    )
                )
            del self.triggers[:]

        self.triggers += triggers

class Trigger(object):
    def __init__(self,
        parent,
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
        self._parent = parent
        self._name = name

        Notify(
            self,
            'Scene.{0}.Trigger.{1}.Created'.format(
                parent._parent.id,
                self.name
            )
        )

        self._device = device
        self._template = template
        self._enabled = enabled
        self._lua = lua
        self._encoded_lua = encoded_lua
        self.arguments = list(
            Argument(self, **argument) for argument in arguments
        )
        self.last_run = last_run
        self.last_eval = last_eval

    @property
    def name(self):
        if not self._name:
            return  'NO NAME ASSIGNED'

        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def device(self):
        return self._parent.get_device(self._device)

    @device.setter
    def device(self, device):
        device = self._parent.get_device(device)
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
        self.arguments += [
            Argument(self, id=len(self.arguments), value=None)
        ]
        return self.arguments[-1]

    def delete(self):
        Notify(
            self,
            'Scene.{0}.Trigger.{1}.Removed'.format(
                self._parent._parent.id,
                self.name
            )
        )
        self._parent.triggers.remove(self)

    def update_node(self, node, full=False):

        arguments = []
        for argument in node.pop('arguments', []):
            id = argument['id']
            for found_argument in self.arguments[:]:
                if found_argument.id == id:
                    self.arguments.remove(found_argument)
                    break
            else:
                found_argument = Argument(self, **argument)

            if found_argument.value != argument['value']:
                found_argument.value = argument['value']
                Notify(
                    found_argument,
                    'Scene.{0}.Trigger.{1}.Argument.{2}.Value.Changed'.format(
                        self._parent._parent.id,
                        self.name,
                        found_argument.id
                    )
                )

            arguments += [found_argument]

        if full:
            for argument in self.arguments:
                Notify(
                    argument,
                    'Scene.{0}.Trigger.{1}.Argument.{2}.Removed'.format(
                        self._parent._parent.id,
                        self.name,
                        argument.id
                    )
                )
            del self.arguments[:]

        self.arguments += arguments

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
                Notify(
                    self,
                    'Scene.{0}.Trigger.{1}.{2}.Changed'.format(
                        self._parent._parent.id,
                        self.name,
                        key
                    )
                )

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


class Timers(object):

    def __init__(self, parent, timers):
        self._parent = parent
        self.timers = list(Timer(self, **timer) for timer in timers)


    def new_timer(self, name):
        self.timers += [Timer(self, len(self.timers), name)]
        return self.timers[-1]

    def __iter__(self):
        return iter(self.timers)

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        for timer in self.timers:
            if timer.name == item:
                return timer

        raise AttributeError

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.timers[item - 1]

        for timer in self.timers:
            if timer.name == item:
                return timer

        raise KeyError

    def update_node(self, node, full):
        timers = []

        for timer in node:
            id = timer['id']

            for found_timer in self.timers[:]:
                if found_timer.id == id:
                    found_timer.update_node(timer, full)
                    self.timers.remove(found_timer)
                    break
            else:
                found_timer = Timer(self, **timer)

            timers += [found_timer]

        if full:
            for timer in self.timers:
                Notify(
                    timer,
                    'Scene.{0}.Timer.{1}.Removed'.format(
                        self._parent.id,
                        timer.name
                    )
                )
            del self.timers[:]

        self.timers += timers


class Timer(object):

    def __init__(
        self,
        parent,
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
        self._parent = parent
        self.id = id

        Notify(
            self,
            'Scene.{0}.Timer.{1}.Created'.format(
                parent._parent.id,
                self.id
            )
        )

        self._name = name
        self._type = type
        self._enabled = enabled
        self._days_of_week = days_of_week
        self._time = time
        self.next_run = next_run
        self.last_run = last_run



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

    @name.setter
    def days_of_week(self, days_of_week):
        self._days_of_week = days_of_week

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, name):
        self._time = time

    def delete(self):
        Notify(
            self,
            'Scene.{0}.Timer.{1}.Removed'.format(
                self._parent._parent.id,
                self.name
            )
        )
        self._parent.timers.remove(self)

    def update_node(self, node, full):

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
                Notify(
                    self,
                    'Scene.{0}.Timer.{1}.{2}.Changed'.format(
                        self._parent._parent.id,
                        self.name,
                        key
                    )
                )

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


class Argument(object):
    def __init__(self, parent, value, name=None, id=None):
        self._parent = parent
        if name is not None:
            if not name:
                name = 'NO NAME ASSIGNED'
            self.name = name
        if id is not None:
            self.id = id

        self._value = value

        if isinstance(parent, Action):
            event = 'Action.{0}.Argument.{1}'.format(parent.action, name)
        elif isinstance(parent, Trigger):
            event = 'Trigger.{0}.Argument.{1}'.format(parent.name, id)
        else:
            event = ''

        if event:
            Notify(
                self,
                'Scene.{0}.{1}.Created'.format(
                    parent._parent._parent._parent.id,
                    event
                )
            )

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def delete(self):
        if isinstance(self._parent, Action):
            event = 'Action.{0}.Argument.{1}'.format(
                self._parent.action,
                self.name
            )
        elif isinstance(self._parent, Trigger):
            event = 'Trigger.{0}.Argument.{1}'.format(
                self._parent.name,
                self.id
            )
        else:
            event = ''

        if event:
            Notify(
                self,
                'Scene.{0}.{1}.Removed'.format(
                    self._parent._parent._parent.id,
                    event
                )
            )
        if self in self._parent.arguments:
            self._parent.arguments.remove(self)

