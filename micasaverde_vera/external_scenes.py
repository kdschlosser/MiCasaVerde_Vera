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
:synopsis: external scenes (not finished)

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

#
# import cPickle
# import os
#
#
# class ExternalScenes(object):
#
#     def __init__(self, parent):
#         self._parent = parent
#         self._scenes = []
#
#     def __getattr__(self, name):
#         if item in self.__dict__:
#             return self.__dict__[item]
#         if item in self._scenes:
#             return self._scenes[item]
#
#         raise AttributeError(
#             'There is no External Scene with the name {0}'.format(item)
#         )
#
#     def load(self, path):
#
#         for scene_file in os.listdir(path):
#             if scene_file.endswith('.scene'):
#                 scene = cPickle.load(os.path.join(path, scene_file))
#                 self._scenes[scene.name] = scene
#
#     def save(self, path):
#         for scene_name, scene in self._scenes.items():
#             cPickle.dump(scene, os.path.join(path, scene_name + '.scene'))
#
#     def new_scene(self, name):
#         id = len(self._scenes.keys())
#         self._scenes[name] = scene = ExternalScene(self, name, id)
#         return scene
#
#
# class ExternalScene(object):
#
#     def __init__(self, parent, name, id):
#         self.id = id
#         self._parent = parent
#         self._name = name
#         self.triggers = Triggers(parent)
#         self.actions = Actions(parent)
#
#         self.__next_trigger_id = 1
#         self.__next_action_id = 1
#
#     @property
#     def _next_trigger_id(self):
#         try:
#             return self.__next_trigger_id
#         finally:
#             self.__next_trigger_id += 1
#
#     @property
#     def _next_action_id(self):
#         try:
#             return self.__next_action_id
#         finally:
#             self.__next_action_id += 1
#
#
# class AvailableVariables(object):
#
#     def __init__(self, scene, device):
#         self._scene = scene
#         self._device = device
#         self.device_num = device.id
#
#     def __getattr__(self, item):
#         if item in self.__dict__:
#             return self.__dict__[item]
#
#         for keys in self._device.variables.keys():
#             if item in keys:
#                 return Trigger(
#                     parent=self._scene,
#                     name=getattr(self._device, 'name', None),
#                     id=0,
#                     device_num=self.device_num,
#                     variable=item,
#                     value=None
#                 )
#
#     def __iter__(self):
#         res = []
#         for keys in self._device.variables.keys():
#             res += [
#                 Trigger(
#                     parent=self._scene,
#                     name=getattr(self._device, 'name', None),
#                     id=0,
#                     device_num=self.device_num,
#                     variable=keys[0],
#                     value=None
#                 )
#             ]
#         return iter(res)
#
#
# class AvailableTriggers(object):
#
#     def __init__(self, scene):
#         self._scene = scene
#
#     def __getattr__(self, item):
#         if item in self.__dict__:
#             return self.__dict__[item]
#
#         for device in self._scene._parent._parent.devices:
#             if item == getattr(device, 'name', None):
#                 return AvailableVariables(self._scene, device)
#
#     def __getitem__(self, item):
#         item = str(item)
#
#         if item.isdigit():
#             item = int(item)
#             for device in self._scene._parent._parent.devices:
#                 if item == device.id:
#                     return AvailableVariables(self._scene, device)
#
#             raise IndexError(
#                 'Device {0} does not exist.'.format(item)
#             )
#
#         attr = getattr(self, item, None)
#         if attr is None:
#             raise KeyError(
#                 'Device {0} does not exist.'.format('item')
#             )
#
#         return attr
#
#
# class Triggers(object):
#
#     def __init__(self, scene):
#         self._scene = scene
#         self.available_triggers = AvailableTriggers(scene)
#         self._triggers = []
#
#     def __radd__(self, trigger):
#         if trigger not in self._triggers:
#             self._triggers += [trigger]
#             event_handler = self._scene._parent._parent.bind(
#                 'Device.{0}.{1}.Changed'.format(
#                     trigger.device_num,
#                     trigger.variable
#                 ),
#                 self._scene
#             )
#             trigger.event_handler = event_handler
#
#     def remove(self, trigger):
#         if trigger in self._triggers:
#             trigger.event_handler.unbind()
#             trigger.event_handler = None
#             self._triggers.remove(trigger)
#
#     def __getattr__(self, item):
#         if item in self.__dict__:
#             return self.__dict__[item]
#
#         for trigger in self._triggers:
#             if trigger.name == item:
#                 return trigger
#
#         raise AttributeError('Trigger {0} not found.'.format(item))
#
#     def __getitem__(self, item):
#         item = str(item)
#         if item.isdigit():
#             item = int(item)
#             for trigger in self._triggers:
#                 if item  == trigger.id:
#                     return trigger
#             raise IndexError(
#                 'Trigger with id {0} not found'.format(item)
#             )
#
#         attr = getattr(self, item, None)
#         if attr is None:
#
#             raise KeyError(
#                 'Trigger with the name {0} not found'.format(item)
#             )
#         return attr
#
#     def new(self, name, device_num, variable, value):
#         trigger = Trigger(self._scene, name, 0, device_num, variable, value)
#         trigger.add()
#         return trigger
#
#
# class Trigger(object):
#     def __init__(self, scene, name, id, device_num, variable, value):
#         self._scene = scene
#         self._name = name
#         self.id = id
#         self._device_num = device_num
#         self._variable = variable
#         self._value = value
#         self.event_handler = None
#
#     @property
#     def name(self):
#         return self._name
#
#     @name.setter
#     def name(self, name):
#         self._name = name
#
#     @property
#     def device_num(self):
#         return self._device_num
#
#     @device_num.setter
#     def device_num(self, device_num):
#         self._device_num = device_num
#
#     @property
#     def variable(self):
#         return self._variable
#
#     @variable.setter
#     def variable(self, variable):
#         self._variable = variable
#
#     @property
#     def value(self):
#         return self._value
#
#     @value.setter
#     def value(self, value):
#         self._value = value
#
#     def add(self):
#         if not self.id:
#             err_msg = []
#             if self.device_num is None:
#                 err_msg += ['Device number (device_num) is not set.']
#             if self.variable is None:
#                 err_msg += ['Variable (variable) is not set.']
#             if self.value is None:
#                 err_msg += ['Value (value) is not set.']
#
#             if err_msg:
#                 print 'Scene Trigger {0} cannot be added'.format(
#                     self.name if self.name else self.device_num
#                 )
#                 print '\n'.join(err_msg)
#
#             else:
#                 self.id = self._scene._next_trigger_id
#                 self._scene.triggers += self
#
#     def remove(self):
#         if self.id:
#             self._scene.triggers.remove(self)
#             self.id = 0
#
#
# class AvailableVariables(object):
#     def __init__(self, scene, device):
#         self._scene = scene
#         self._device = device
#         self.device_num = device.id
#
#     def __getattr__(self, item):
#         if item in self.__dict__:
#             return self.__dict__[item]
#
#         for keys in self._device.variables.keys():
#             if item in keys:
#                 return Trigger(
#                     parent=self._scene,
#                     name=getattr(self._device, 'name', None),
#                     id=0,
#                     device_num=self.device_num,
#                     variable=item,
#                     value=None
#                 )
#
#     def __iter__(self):
#         res = []
#         for keys in self._device.variables.keys():
#             res += [
#                 Trigger(
#                     parent=self._scene,
#                     name=getattr(self._device, 'name', None),
#                     id=0,
#                     device_num=self.device_num,
#                     variable=keys[0],
#                     value=None
#                 )
#             ]
#         return iter(res)
#
#
# class AvailableTriggers(object):
#     def __init__(self, scene):
#         self._scene = scene
#
#     def __getattr__(self, item):
#         if item in self.__dict__:
#             return self.__dict__[item]
#
#         for device in self._scene._parent._parent.devices:
#             if item == getattr(device, 'name', None):
#                 return AvailableVariables(self._scene, device)
#
#     def __getitem__(self, item):
#         item = str(item)
#
#         if item.isdigit():
#             item = int(item)
#             for device in self._scene._parent._parent.devices:
#                 if item == device.id:
#                     return AvailableVariables(self._scene, device)
#
#             raise IndexError(
#                 'Device {0} does not exist.'.format(item)
#             )
#
#         attr = getattr(self, item, None)
#         if attr is None:
#             raise KeyError(
#                 'Device {0} does not exist.'.format('item')
#             )
#
#         return attr
# class Trigger(object):
#
#     def __init__(self, scene, name, id, device_num, variable, value):
#         self._scene = scene
#         self._name = name
#         self.id = id
#         self._device_num = device_num
#         self._variable = variable
#         self._value = value
#         self.event_handler = None
#
#     @property
#     def name(self):
#         return self._name
#
#     @name.setter
#     def name(self, name):
#         self._name = name
#
#     @property
#     def device_num(self):
#         return self._device_num
#
#     @device_num.setter
#     def device_num(self, device_num):
#         self._device_num = device_num
#
#     @property
#     def variable(self):
#         return self._variable
#
#     @variable.setter
#     def variable(self, variable):
#         self._variable = variable
#
#     @property
#     def value(self):
#         return self._value
#
#     @value.setter
#     def value(self, value):
#         self._value = value
#
#     def add(self):
#         if not self.id:
#             err_msg = []
#             if self.device_num is None:
#                 err_msg += ['Device number (device_num) is not set.']
#             if self.variable is None:
#                 err_msg += ['Variable (variable) is not set.']
#             if self.value is None:
#                 err_msg += ['Value (value) is not set.']
#
#             if err_msg:
#                 print 'Scene Trigger {0} cannot be added'.format(
#                     self.name if self.name else self.device_num
#                 )
#                 print '\n'.join(err_msg)
#
#             else:
#                 self.id = self._scene._next_trigger_id
#                 self._scene.triggers += self
#
#     def remove(self):
#         if self.id:
#             self._scene.triggers.remove(self)
#             self.id = 0
#
# class Actions(object):
#     def __init__(self, scene):
#         self._scene = scene
#         self.available_actions = AvailableActions(scene)
#         self._actions = []
#
#     def __radd__(self, action):
#         if action not in self._actions:
#             self._actions += [action]
#
#     def remove(self, action):
#         if action in self._actions:
#             self._actions.remove(action)
#
#
#     def __getattr__(self, item):
#         if item in self.__dict__:
#             return self.__dict__[item]
#
#         for action in self._actions:
#             if action.name == item:
#                 return action
#
#         raise AttributeError('Action with name {0} not found.'.format(item))
#
#     def __getitem__(self, item):
#         item = str(item)
#         if item.isdigit():
#             item = int(item)
#             for action in self._actions:
#                 if item == action.id:
#                     return action
#             raise IndexError(
#                 'Action with id {0} not found'.format(item)
#             )
#
#         attr = getattr(self, item, None)
#         if attr is None:
#
#             raise KeyError(
#                 'Action with the name {0} not found'.format(item)
#             )
#         return attr
#
#     def new(self, name, device_num, variable, value):
#         action = Action(self._scene, name, 0, device_num, variable, value)
#         action.add()
#         return action
#
#
#
#
#
#
#
