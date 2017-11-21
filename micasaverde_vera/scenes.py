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

"""
<scenes>
    <scene name="Freezing" notification_only="111" modeStatus="0" id="17" users="1880772" Timestamp="1494221451" last_run="1509100826" room="0">
        <triggers>
            <trigger device="111" name="Freezing" enabled="1" template="2" lua="" encoded_lua="1" last_run="1509100826" last_eval="0">
                <arguments>
                    <argument id="1" value="0"></argument>
                </arguments>
            </trigger>
        </triggers>
    </scene>
</scenes>
"""


import base64
from event import EventHandler


class Scenes(object):
    

    def __init__(self, parent, node):
        self._scenes = []
        self._parent = parent
        self.send = parent.send
        self._bindings = []

        if node is not None:
            for scene in node:
                self._scenes += [Scene(self, scene)]

    def get_device(self, number):
        return self._parent.get_device(number)

    def get_room(self, number):
        return self._parent.get_room(number)

    def get_user(self, number):
        return self._parent.get_user(number)

    def get_scene(self, number):
        for scene in self._scenes:
            if number in (scene.id, scene.name):
                return scene
            
    def register_event(self, callback, attribute=None):
        self._bindings += [EventHandler(self, callback, None)]
        return self._bindings[-1]

    def unregister_event(self, event_handler):
        if event_handler in self._bindings:
            self._bindings.remove(event_handler)

    def update_node(self, node, full=False):
        if node is not None:
            scenes = []
            for scene in node:
                id = scene['id']
                
                for found_scene in self._scenes[:]:
                    if found_scene.id == id:
                        found_scene.update_node(scene)
                        self._scenes.remove(found_scene)
                        break
                else:
                    found_scene = Scene(self, scene)
                    for event_handler in self._bindings:
                        event_handler('new', scene=found_scene)
                   
                scenes += [found_scene]
                    
            if full:
                for scene in self._scenes:
                    for event_handler in self._bindings:
                        event_handler('remove', scene=scene)
                        
                del self._scenes[:]
                
            self._scenes += scenes
    

class Scene(object):
    
    
    def __init__(self, parent, node):
        self._parent = parent
        self._triggers = []
        self._bindings = []

        def get(attr):
            return node.pop(attr, None)

        self._name = get('name')
        self._notification_only = get('notification_only')
        self._modeStatus = get('modeStatus')
        self.id = get('id')
        self._users = get('users')
        self.Timestamp = get('Timestamp')
        self.last_run = get('last_run')
        self._room = get('room')
        
        for trigger in node.pop('triggers', []):
            self._triggers += [Trigger(self, trigger)]
        
        self.__dict__.update(node)
        
    def register_event(self, callback, attribute=None):
        self._bindings += [EventHandler(self, callback, attribute)]
        return self._bindings[-1]

    def unregister_event(self, event_handler):
        if event_handler in self._bindings:
            self._bindings.remove(event_handler)

    def get_device(self, number):
        return self._parent.get_device(number)
    
    def get_trigger(self, number):
        number = str(number)
        
        if number.isdigit():
            number = int(number)
                
        for trigger in self._triggers:
            if number in (trigger.id, trigger.name):
                return trigger

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
    def users(self):
        return self._parent.get_user(self._users)

    @users.setter
    def users(self, users):
        pass

    @property
    def modeStatus(self):
        return self._modeStatus

    @modeStatus.setter
    def modeStatus(self, modeStatus):
        pass

    @property
    def notification_only(self):
        return self._parent.get_device(self._notification_only)

    @notification_only.setter
    def notification_only(self, notification_only):
        pass

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

    def delete(self):
        self._parent.send(
            id='scene',
            action='delete',
            scene=self.id
        )

    def off(self):
        self._parent.send(
            id='action',
            serviceId='urn:micasaverde-com:serviceId:HomeAutomationGateway1',
            action='SceneOff',
            SceneNum=self.id
        )

    def run(self):
        self._parent.send(
            id='action',
            serviceId='urn:micasaverde-com:serviceId:HomeAutomationGateway1',
            action='RunScene',
            SceneNum=self.id
        )
        
    def update_node(self, node, full=False):
        triggers = []
        
        for trigger in node.pop('triggers', []):
            name = trigger['name']
            for found_trigger in self._triggers[:]:
                if found_trigger.name == name:
                    found_trigger.update_node(trigger, full)
                    self._triggers.remove(found_trigger)
                    break
            else:
                found_trigger = Trigger(self, trigger)

                for event_handler in self._bindings:
                    event_handler(
                        'new',
                        scene=self,
                        trigger=found_trigger,
                        attribute='triggers'
                    )
                    
                
            triggers += [found_trigger]
            
        if full:
            for trigger in self._triggers:
                for event_handler in self._bindings:
                    event_handler(
                        'remove',
                        scene=self,
                        trigger=found_trigger,
                        attribute='triggers'
                    )
            
            del self._triggers[:]
        
        self._triggers += triggers

        for key, value in node.items():
            old_value = getattr(self, key, None)

            if old_value is None:

                for event_handler in self._bindings:
                    event_handler(
                        'new',
                        scene=self,
                        attribute=key,
                        value=value
                    )
                    
                setattr(self, key, value)

            elif old_value != value:

                for event_handler in self._bindings:
                    event_handler(
                        'changed',
                        scene=self,
                        attribute=key,
                        value=value
                    )
                setattr(self, key, value)
        

class SceneArgument(object):
    
    def __init__(self, parent, node):
        self._parent = parent
        for key, value in node.items():
            self.__dict__[key] = value


class SceneTrigger(object):
    
    def __init__(self, parent, node):
        self._parent = parent
        self._arguments = []
        self._bindings = []

        def get(attr):
            return node.pop(attr, None)

        self._device = get('device')
        self._name = get('name')
        self._enabled = get('enabled')
        self._template = get('template')
        self._lua = get('lua')
        self._encoded_lua = get('encoded_lua')
        self.last_run = get('last_run')
        self.last_eval = get('last_eval')

        for argument in node.pop('arguments', []):
            self._arguments += [SceneArgument(self, argument)]
            
        for key, value in node.items():
            self.__dict__[key] = value
            
    def register_event(self, callback, attribute=None):
        self._bindings += [EventHandler(self, callback, attribute)]
        return self._bindings[-1]

    def unregister_event(self, event_handler):
        if event_handler in self._bindings:
            self._bindings.remove(event_handler)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        pass

    @property
    def encoded_lua(self):
        return self._encoded_lua

    @encoded_lua.setter
    def encoded_lua(self, encoded_lua):
        pass

    @property
    def device(self):
        return self._parent.get_device(self._device)

    @device.setter
    def device(self, device):
        pass

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        pass

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, template):
        pass

    @property
    def lua(self):
        if self._encoded_lua == '1':
            return base64.b64decode(self._lua)

    @lua.setter
    def lua(self, lua):
        if self._encoded_lua == '1':
            base64.b64encode(lua)
            
    
    def update_node(self, node, full=False):
        
        arguments = []
        for argument in node.pop('arguments', []):
            id = argument['id']
            for found_argument in self._arguments[:]:
                if found_argument.id == id:
                    self._arguments.remove(argument)
            else:
                found_argument = SceneArgument(self, argument)
                
                for event_handler in self._bindings:
                    event_handler(
                        'new',
                        scene=self._parent,
                        trigger=self,
                        argument=found_argument,
                        attribute='arguments'
                    )
                
            if found_argument.value != argument['value']:
                event_handler(
                    'changed',
                    scene=self._parent,
                    trigger=self,
                    argument=found_argument,
                    attribute='arguments'
                )
                
            arguments += [found_argument]
        
        if full:
            for argument in self._arguments:
                event_handler(
                    'remove',
                    scene=self._parent,
                    trigger=self,
                    argument=argument,
                    attribute='arguments'
                )
                
            del self._arguments[:]
        
        self._arguments += arguments
            
        
        for key, value in node:
            old_value = getattr(self, key, None)
            
            if old_value is None:
                event_handler(
                    'new',
                    scene=self._parent,
                    trigger=self,
                    attribute=key,
                    value=value
                )
                
                setattr(self, key, value)
                
            elif old_value != value:
                event_handler(
                    'changed',
                    scene=self._parent,
                    trigger=self,
                    attribute=key,
                    value=value
                )
                setattr(self, key, value)
