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
:synopsis: micasaverde_vera utility decorators and functions

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

# This module contains decorators that enable data path debugging. It also
# contains a decorator for notification of depreciated items. This includes
# classes, functions, methods, properties (set and get separately), and also
# variables. variables only produce a warning when the actual variable is
# accessed.

# noinspection PyDeprecation
import imp
import os
import binascii
import importlib
import warnings
import logging
import inspect
import threading
import traceback
import sys
import time
from functools import update_wrapper

from .constants import CORE_PATH
from .vera_exception import VeraImportError
from .logger import (
    LOGGING_DATA_PATH,
    LOGGING_DATA_PATH_WITH_RETURN,
    LOGGING_TIME_FUNCTION_CALLS
)

logger = logging.getLogger(__name__)

PY3 = sys.version_info[0] > 2

DEPRECATED_LOGGING_TEMPLATE = '''\
[DEPRECATED]\
{thread_name}\
[{thread_id}] - \
{object_type}
src: {calling_obj} [{calling_filename}:{calling_line_no}]
dst: {called_obj} [{called_filename}:{called_line_no}]
'''

# {{0}} - \

LOGGING_TEMPLATE = '''\
[DEBUG-DATA] \
{thread_name}\
[{thread_id}]
                          src: {calling_obj} [{calling_filename}:{calling_line_no}]
                          dst: {called_obj} [{called_filename}:{called_line_no}]
                          {msg}'''


def get_line_and_file(stacklevel=2):
    """
    Gets the filename and also the line number in the file where the code is
    that is making a call and also where it is calling.
    """
    try:
        # noinspection PyProtectedMember
        caller = sys._getframe(stacklevel)
    except ValueError:
        glbs = sys.__dict__
        line_no = 1
    else:
        glbs = caller.f_globals
        line_no = caller.f_lineno
    if '__name__' in glbs:
        module = glbs['__name__']
    else:
        module = "<string>"
    filename = glbs.get('__file__')
    if filename:
        fnl = filename.lower()
        if fnl.endswith((".pyc", ".pyo")):
            filename = filename[:-1]
    else:
        if module == "__main__":
            try:
                filename = sys.argv[0]
            except AttributeError:
                # embedded interpreters don't have sys.argv, see bug #839151
                filename = '__main__'
        if not filename:
            filename = module

    return filename, int(line_no)


def _get_stack(frame):
    frames = []
    while frame:
        frames += [frame]
        frame = frame.f_back
    return frames


def calling_function_logger(func_name):
    func_name = func_name.split('.')

    while func_name:
        if '.'.join(func_name) in sys.modules:
            return logging.getLogger('.'.join(func_name))
        func_name = func_name[:-1]


def caller_name(start=2):
    """
    This function creates a `"."` separated name for where the call is being
    made from. an example would be `"openzwave.node.ZWaveNode.product_id"`

    This function also handles nested functions and classes alike.
    """
    # noinspection PyProtectedMember
    stack = _get_stack(sys._getframe(1))

    def get_name(s):
        if len(stack) < s + 1:
            return []
        parent_frame = stack[s]

        name = []
        module = inspect.getmodule(parent_frame)
        if module:
            name.append(module.__name__)

        codename = parent_frame.f_code.co_name
        if codename not in ('<module>', '__main__'):  # top level usually
            frame = parent_frame
            if 'self' in frame.f_locals:
                name.append(frame.f_locals['self'].__class__.__name__)
                name.append(codename)  # function or a method
            else:
                name.append(codename)  # function or a method
                frame = frame.f_back
                while codename in frame.f_locals:
                    codename = frame.f_code.co_name
                    if codename in ('<module>', '__main__'):
                        break
                    name.append(codename)
                    frame = frame.f_back

        del parent_frame
        return name

    res = get_name(start)

    if not res or 'pydev_run_in_console' in res:
        res = get_name(start - 1)

    if res == ['<module>'] or res == ['__main__']:
        res = get_name(start - 1)
        if 'log_it' in res:
            res = get_name(start)

    if 'wrapper' in res:
        res = get_name(start + 1) + get_name(start - 1)[-1:]

    return ".".join(res)



def _func_arg_string(func, args, kwargs):
    """
    This function is used to get the parameter names and also any default
    arguments.
    """

    if PY3:
        # noinspection PyUnresolvedReferences
        arg_names = inspect.getfullargspec(func)[0]
    else:
        # noinspection PyDeprecation
        arg_names = inspect.getargspec(func)[0]

    start = 0
    if arg_names:
        if arg_names[0] == "self":
            start = 1

    res = []
    append = res.append

    for key, value in list(zip(arg_names, args))[start:]:
        append(str(key) + "=" + repr(value).replace('.<locals>.', '.'))

    for key, value in kwargs.items():
        append(str(key) + "=" + repr(value).replace('.<locals>.', '.'))

    return "(" + ", ".join(res) + ")"


def deprecated(version, msg=''):
    """
    deprecated

    This is my crowning jewel of utilities. It is a decorator that is used to
    display deprecated warnings.

    This decorator works like no other you have seen before it. It can handle
    functions, methods, classes, properties and all variables of any data type.

    If used as a decorator a custom message cannot be supplied. if wanting to
    only deprecate the set portion of a property and not the get you cannot
    use this as a decorator. you cannot decorate a variable either. I have
    code examples below of how to use this function.


    Example without any custom messages

    .. code-block:: python

        some_module_level_variable = deprecated('any data type')

        @deprecated('0.5.0')
        def some_function():
            some_function_variable = deprecated(5)

        @deprecated('0.5.0')
        class SomeClass(object):
            some_class_level_variable = deprecated(['list', 1, 2, 3])


            @deprecated('0.5.0')
            def some_method(self):
                some_method_level_variable = (
                    deprecated({'dict key': 'dict value'})
                )

                @deprecated('0.5.0')
                def some_nested_function():
                    some_nested_function_variable = (
                        deprecated(('tuple', 1, 2, 3, 4))
                    )

            @deprecated('0.5.0')
            @property
            def get_set_property(self):
                pass

            @deprecated('0.5.0')
            @get_set_property.setter
            def get_set_property(self, value):
                pass

            @deprecated('0.5.0')
            @property
            def only_get_property(self):
                pass

            @only_get_property.setter
            def only_get_property(self, value):
                pass

            @property
            def __get_only_set_property(self):
                pass

            def __set_only_set_property(self, value):
                pass

            only_set_property = property(fset=__set_only_set_property)
            only_set_property = deprecated(only_set_property)
            only_set_property.fget = __get_only_set_property


    Example with custom messages

    .. code-block:: python

        some_module_level_variable = (
            deprecated('any data type', 'custom message')
        )

        def some_function():
            some_function_variable = deprecated(5, 'custom message')

        some_function = deprecated(some_function, 'custom message')

        class SomeClass(object):
            some_class_level_variable = (
                deprecated(['list', 1, 2, 3], 'custom message')
            )


            @deprecated('0.5.0')
            def some_method(self):
                some_method_level_variable = (
                    deprecated({'dict key': 'dict value'}, 'custom message')
                )

                def some_nested_function():
                    some_nested_function_variable = (
                        deprecated(('tuple', 1, 2, 3, 4), 'custom message')
                    )

                some_nested_function = (
                    deprecated(some_nested_function, 'custom message')
                )

            some_method = deprecated(some_method, 'custom message')

            def get_set_property(self):
                pass

            get_set_property = property(fget=get_set_property)

            get_set_property = (
                deprecated(get_set_property, 'custom get message')
            )

            def __get_set_property(self, value):
                pass

            get_set_property = deprecated(
                get_set_property.setter(__get_set_property),
                'custom set message'
            )

            @property
            def only_get_property(self):
                pass

            only_get_property = deprecated(only_get_property, 'custom message')

            @only_get_property.setter
            def only_get_property(self, value):
                pass

            @property
            def only_set_property(self):
                pass

            @deprecated('0.5.0')
            @only_set_property.setter
            def only_set_property(self, value):
                pass

        SomeClass = deprecated(SomeClass, 'custom message')
    """

    def decorator_wrapper(obj):
        func_name = caller_name(1)

        called_filename, called_line_no = get_line_and_file()
        called_line_no += 1

        doc = ['.. deprecated:: ' + version]

        if msg:
            doc += ['', '    ' + msg, '']
        else:
            doc += ['', '    ', '']

        def update_doc_indent(new_doc, old_doc):
            new_doc += ['', '']
            count = 0
            for char in list(old_doc):
                if char not in (' ', '\t'):
                    break

                if char == '\t':
                    count += 4
                else:
                    count += 1

            if count:
                new_doc = list(' ' * count + line for line in new_doc)

            new_doc += [old_doc]

            return '\n'.join(new_doc)

        if isinstance(obj, property):
            class FSetWrapper(object):

                def __init__(self, fset_object):
                    self._fset_object = fset_object
                    if func_name:
                        self._f_name = func_name + '.' + fset_object.__name__
                    else:
                        self._f_name = (
                            fset_object.__module__ + '.' + fset_object.__name__
                        )

                def __call__(self, *args, **kwargs):
                    # turn off filter
                    warnings.simplefilter('always', DeprecationWarning)

                    message = "deprecated set property [{0}].\n{1}".format(
                        self._f_name,
                        msg
                    )

                    if logger.getEffectiveLevel() == logging.DEBUG:
                        calling_filename, calling_line_no = get_line_and_file()
                        thread = threading.current_thread()
                        calling_obj = caller_name()

                        debug_msg = DEPRECATED_LOGGING_TEMPLATE.format(
                            thread_name=thread.getName(),
                            thread_id=thread.ident,
                            object_type='property (set)',
                            calling_obj=calling_obj,
                            calling_filename=calling_filename,
                            calling_line_no=calling_line_no,
                            called_obj=func_name,
                            called_filename=called_filename,
                            called_line_no=called_line_no
                        )

                        logger.debug(debug_msg)

                    warnings.warn(
                        message,
                        category=DeprecationWarning,
                        stacklevel=2
                    )
                    # reset filter

                    warnings.simplefilter('default', DeprecationWarning)
                    return self._fset_object(*args, **kwargs)


            class FGetWrapper(object):

                def __init__(self, fget_object):
                    self._fget_object = fget_object
                    if func_name:
                        self._f_name = func_name + '.' + fget_object.__name__
                    else:
                        self._f_name = (
                            fget_object.__module__ + '.' + fget_object.__name__
                        )

                def __call__(self, *args, **kwargs):
                    # turn off filter
                    warnings.simplefilter('always', DeprecationWarning)
                    if logger.getEffectiveLevel() == logging.DEBUG:
                        calling_filename, calling_line_no = get_line_and_file()
                        thread = threading.current_thread()
                        calling_obj = caller_name()

                        debug_msg = DEPRECATED_LOGGING_TEMPLATE.format(
                            thread_name=thread.getName(),
                            thread_id=thread.ident,
                            object_type='property (get)',
                            calling_obj=calling_obj,
                            calling_filename=calling_filename,
                            calling_line_no=calling_line_no,
                            called_obj=func_name,
                            called_filename=called_filename,
                            called_line_no=called_line_no
                        )

                        logger.debug(debug_msg)

                    message = "deprecated get property [{0}].\n{1}".format(
                        self._f_name,
                        msg
                    )

                    warnings.warn(
                        message,
                        category=DeprecationWarning,
                        stacklevel=2
                    )
                    # reset filter

                    warnings.simplefilter('default', DeprecationWarning)
                    return self._fget_object(*args, **kwargs)

            try:
                if obj.fset is not None:
                    fset = FSetWrapper(obj.fset)
                    fget = obj.fget

                    if fget is None and fset.__doc__ is not None:
                        if '.. deprecated::' in fset.__doc__:
                            doc = fset.__doc__
                        else:
                            doc = update_doc_indent(doc, fset.__doc__)
                    elif fget is not None and fget.__doc__ is not None:
                        if '.. deprecated::' in fget.__doc__:
                            doc = fget.__doc__
                        else:
                            doc = update_doc_indent(doc, fget.__doc__)
                    else:
                        doc = '\n'.join(doc)

                    return property(fget, fset, doc=doc)

                elif obj.fget is not None:
                    fget = FGetWrapper(obj.fget)
                    fset = obj.fset

                    if fget.__doc__ is not None:
                        doc = update_doc_indent(doc, fget.__doc__)
                    else:
                        doc = '\n'.join(doc)

                    return property(fget, fset, doc=doc)

            except:
                traceback.print_exc()
                return obj

        elif inspect.isfunction(obj) or inspect.ismethod(obj):
            if func_name:
                f_name = func_name + '.' + obj.__name__
            else:
                f_name = obj.__module__ + '.' + obj.__name__

            def wrapper(*args, **kwargs):
                # turn off filter
                warnings.simplefilter('always', DeprecationWarning)

                if PY3:
                    # noinspection PyUnresolvedReferences
                    arg_names = inspect.getfullargspec(obj)[0]
                else:
                    # noinspection PyDeprecation
                    arg_names = inspect.getargspec(obj)[0]

                if arg_names and arg_names[0] == "self":
                    call_type = 'method'
                else:
                    call_type = 'function'

                if logger.getEffectiveLevel() == logging.DEBUG:
                    calling_filename, calling_line_no = get_line_and_file()
                    thread = threading.current_thread()
                    calling_obj = caller_name()

                    debug_msg = DEPRECATED_LOGGING_TEMPLATE.format(
                        thread_name=thread.getName(),
                        thread_id=thread.ident,
                        object_type=call_type,
                        calling_obj=calling_obj,
                        calling_filename=calling_filename,
                        calling_line_no=calling_line_no,
                        called_obj=func_name,
                        called_filename=called_filename,
                        called_line_no=called_line_no
                    )

                    logger.debug(debug_msg)

                message = "deprecated {0} [{1}].\n{2}".format(
                    call_type,
                    f_name,
                    msg
                )

                warnings.warn(
                    message,
                    category=DeprecationWarning,
                    stacklevel=2
                )
                # reset filter

                warnings.simplefilter('default', DeprecationWarning)
                return obj(*args, **kwargs)

            if obj.__doc__ is not None:
                doc = update_doc_indent(doc, obj.__doc__)

            else:
                doc = '\n'.join(doc)

            wrapper = update_wrapper(wrapper, obj)

            wrapper.__doc__ = doc
            return wrapper

        elif inspect.isclass(obj):
            if func_name:
                class_name = func_name + '.' + obj.__name__
            else:
                class_name = obj.__module__ + '.' + obj.__name__

            def wrapper(*args, **kwargs):
                # turn off filter
                warnings.simplefilter('always', DeprecationWarning)

                if logger.getEffectiveLevel() == logging.DEBUG:
                    calling_filename, calling_line_no = get_line_and_file()
                    thread = threading.current_thread()
                    calling_obj = caller_name()

                    debug_msg = DEPRECATED_LOGGING_TEMPLATE.format(
                        thread_name=thread.getName(),
                        thread_id=thread.ident,
                        object_type='class',
                        calling_obj=calling_obj,
                        calling_filename=calling_filename,
                        calling_line_no=calling_line_no,
                        called_obj=func_name,
                        called_filename=called_filename,
                        called_line_no=called_line_no
                    )

                    logger.debug(debug_msg)

                message = "deprecated class [{0}].\n{1}".format(
                    class_name,
                    msg
                )

                warnings.warn(
                    message,
                    category=DeprecationWarning,
                    stacklevel=2
                )
                # reset filter

                warnings.simplefilter('default', DeprecationWarning)
                return obj(*args, **kwargs)

            if obj.__doc__ is not None:
                doc = update_doc_indent(doc, obj.__doc__)

            else:
                doc = '\n'.join(doc)

            wrapper.__doc__ = doc

            return update_wrapper(wrapper, obj)
        else:
            # noinspection PyProtectedMember
            frame = sys._getframe().f_back
            source = inspect.findsource(frame)[0]
            called_line_no -= 1

            if msg:
                while (
                    '=deprecated' not in source[called_line_no] and
                    '= deprecated' not in source[called_line_no] and
                    '=utils.deprecated' not in source[called_line_no] and
                    '= utils.deprecated' not in source[called_line_no]
                ):
                    called_line_no -= 1

            symbol = source[called_line_no].split('=')[0].strip()

            if func_name:
                symbol_name = func_name + '.' + symbol
            else:
                symbol_name = symbol

            def wrapper(*_, **__):
                # turn off filter
                warnings.simplefilter('always', DeprecationWarning)

                if logger.getEffectiveLevel() == logging.DEBUG:
                    object_type = str(type(obj)).split(' ', 1)[-1]
                    object_type = object_type[1:-2]
                    calling_filename, calling_line_no = get_line_and_file()
                    thread = threading.current_thread()
                    calling_obj = caller_name()

                    debug_msg = DEPRECATED_LOGGING_TEMPLATE.format(
                        thread_name=thread.getName(),
                        thread_id=thread.ident,
                        object_type=object_type,
                        calling_obj=calling_obj,
                        calling_filename=calling_filename,
                        calling_line_no=calling_line_no,
                        called_obj=func_name,
                        called_filename=called_filename,
                        called_line_no=called_line_no
                    )

                    logger.debug(debug_msg)

                message = "deprecated symbol [{0}].\n{1}".format(
                    symbol_name,
                    msg
                )

                warnings.warn(
                    message,
                    category=DeprecationWarning,
                    stacklevel=2
                )
                # reset filter

                warnings.simplefilter('default', DeprecationWarning)
                return obj

            doc = '\n'.join(doc)

            return property(wrapper, doc=doc)

    return decorator_wrapper


# This is rather odd to see.
# I am using sys.excepthook to alter the displayed traceback data.
# The reason why I am doing this is to remove any lines that are generated
# from any of the code in this file. It adds a lot of complexity to the
# output traceback when any lines generated from this file do not really need
# to be displayed.

def trace_back_hook(tb_type, tb_value, tb):
    tb = "".join(
        traceback.format_exception(
            tb_type,
            tb_value,
            tb,
        )
    )
    if tb_type == DeprecationWarning:
        sys.stderr.write(tb)
    else:
        new_tb = []
        skip = False
        for line in tb.split('\n'):
            if line.strip().startswith('File'):
                if __file__ in line:
                    skip = True
                else:
                    skip = False
            if skip:
                continue

            new_tb += [line]

        sys.stderr.write('\n'.join(new_tb))


sys.excepthook = trace_back_hook


def logit(func):
    """
    log_it

    This function is a decorator. It's sole purpose is to be able to track
    the data path. It is a very useful tool during the debugging process.

    It creates a debugging log entry containing where the call is made from.
    the location of the function/method/property. that has been wrapped by
    this decorator. As well as the parameter names and data that was passed
    including any defaulted parameters.
    """
    if PY3:
        if func.__code__.co_flags & 0x20:
            return func
    else:
        if func.func_code.co_flags & 0x20:
            return func

    lgr = logging.getLogger(func.__module__)
    func_name = func.__name__
    func_location = caller_name(1)
    func_module = func.__module__

    called_filename, called_line_no = get_line_and_file()
    called_line_no += 1

    def wrapper(*args, **kwargs):

        if lgr.getEffectiveLevel() in (
            LOGGING_DATA_PATH,
            LOGGING_DATA_PATH_WITH_RETURN,
            LOGGING_TIME_FUNCTION_CALLS,
            logging.DEBUG
        ):

            if 'self' in kwargs:
                self = kwargs['self']
                f_name = [
                    self.__class__.__module__,
                    self.__class__.__name__,
                    func_name
                ]
            elif hasattr(func, '__class__') and len(args):
                self = args[0]
                f_name = [
                    self.__class__.__module__,
                    self.__class__.__name__,
                    func_name
                ]
            else:
                if func_location:
                    f_name = [func_location, func_name]
                else:
                    f_name = [func_module, func_name]

            f_name = '.'.join(f_name)

            if func_location:
                real_func_name = func_location + '.' + func_name
            else:
                real_func_name = func_module + '.' + func_name

            calling_filename, calling_line_no = get_line_and_file()
            thread = threading.current_thread()
            arg_string = _func_arg_string(func, args, kwargs)

            msg = 'function called: {0}{1}\n'.format(f_name, arg_string)

            if real_func_name != f_name:
                called_obj = real_func_name
            else:
                called_obj = f_name
            calling_obj = caller_name()
            msg = LOGGING_TEMPLATE.format(
                thread_name=thread.getName(),
                thread_id=thread.ident,
                calling_obj=calling_obj,
                calling_filename=calling_filename,
                calling_line_no=calling_line_no,
                called_obj=called_obj,
                called_filename=called_filename,
                called_line_no=called_line_no,
                msg=msg
            )

            if lgr.getEffectiveLevel() in (
                LOGGING_TIME_FUNCTION_CALLS,
                logging.DEBUG
            ):
                start = time.time()
                result = func(*args, **kwargs)
                stop = time.time()

                divider = 1
                suffix = 'sec'
                suffixes = [
                    'ms',
                    'us',
                    'ns',
                    'ps',
                    'fs',
                    'as',
                    'zs',
                    'ys'
                ]

                while suffixes:
                    duration = int(round((stop - start) * divider))
                    if duration > 0:
                        break

                    divider *= 1000
                    suffix = suffixes.pop(0)

                duration = int(round((stop - start) * divider))
                if duration == 0:
                    duration = stop - start
                    suffix = ''
                    duration = '                          duration: to fast to measure\n'
                else:
                    duration = (stop - start) * divider
                    duration = '                          duration: {0} {1}\n'.format(duration, suffix)

                msg += duration

            else:
                result = func(*args, **kwargs)

            if lgr.getEffectiveLevel() in (
                LOGGING_DATA_PATH_WITH_RETURN,
                logging.DEBUG
            ):
                msg += '                          {0} => {1}\n'.format(f_name, repr(result))

            lgr.log(lgr.getEffectiveLevel(), msg + '\n')
        else:
            result = func(*args, **kwargs)

        return result

    wrapper.__doc__ = func.__doc__
    return update_wrapper(wrapper, func)



def parse_string(word):
    next_to_last_char = ''
    last_char = ''
    new_word = ''
    for char in word:
        if last_char and (char.isupper() or char.isdigit()):
            if last_char == '_':
                new_word = new_word[:-1]
            elif (
                last_char.isupper() and
                next_to_last_char and
                next_to_last_char.isupper()
            ):
                new_word = new_word[:-2] + last_char.lower()
            new_word += '_'

        elif char == '_' and last_char.isupper():
            new_word = new_word[:-2] + last_char.lower()
        new_word += char.lower()
        next_to_last_char = last_char
        last_char = char
    if last_char.isupper():
        new_word = new_word[:-2] + last_char.lower()
    return new_word


def service_id_to_service_type(service_id):
    service = service_id.replace('serviceId', 'service')
    service = service.replace('urn:', 'urn:schemas-')

    char = service[-1]
    service = service[:-1]
    while char.isdigit():
        char = service[-1] + char
        service = service[:-1]

    service += char[0]
    char = char[1:]
    return service + ':' + char


def create_service_name(service_type):
    service_type = service_type.split(':')

    if len(service_type) == 5:
        return ''.join(service_type[-2:]).replace('-', '_')
    else:
        return service_type[-1].replace('-', '')


def print_list(l, indent):
    output = ''
    for item in l:
        if isinstance(item, list):
            if len(item) > 2:
                output += indent + '[\n'
                output += print_list(item, indent + '    ')
                output += indent + ']\n'
            else:
                output += indent + repr(item) + '\n'
        else:
            output += indent + repr(item) + '\n'
    return output


def print_dict(d, indent=''):
    output = ''

    for key in sorted(d.keys()):
        value = d[key]
        if isinstance(value, dict):
            output += indent + key + ':\n'
            output += print_dict(value, indent + '    ')
        elif isinstance(value, list):
            output += indent + key + ':\n'
            output += print_list(value, indent + '    ')
        else:
            output += indent + key + ': ' + repr(value) + '\n'
    return output


# noinspection PyPep8Naming
def CRC32_from_file(file_path):
    with open(file_path, 'rb') as f:
        crc = (binascii.crc32(f.read()) & 0xFFFFFFFF)
    return "%08X" % crc


def init_core():
    core = imp.load_source(
        'micasaverde_vera.core',
        os.path.join(CORE_PATH, '__init__.py')
    )
    core.__name__ = 'micasaverde_vera.core'
    core.__path__ = [CORE_PATH]
    core.__package__ = 'micasaverde_vera'
    return core


def import_device(device_type):
    try:
        cls_name = create_service_name(device_type)
        mod_name = parse_string(cls_name)

        device_mod = importlib.import_module(
            'micasaverde_vera.core.devices.' + mod_name
        )
        device_cls_name = cls_name[:1].upper() + cls_name[1:]
        device_cls = getattr(
            device_mod,
            device_cls_name.replace('_', '')

        )

        return device_cls
    except VeraImportError:
        return None


def import_service(service_id):
    service_type = service_id_to_service_type(service_id)
    cls_name = create_service_name(service_type)
    mod_name = parse_string(cls_name)

    try:
        service_mod = importlib.import_module(
            'micasaverde_vera.core.services.' + mod_name
        )
        service_cls_name = cls_name[:1].upper() + cls_name[1:]
        service_cls = getattr(
            service_mod,
            service_cls_name.replace('_', '')
        )
        return service_cls

    except VeraImportError:
        return None


def copy_dict(mapping, storage):
    for key, value in mapping.items():
        if isinstance(value, dict):
            storage[key] = dict()
            copy_dict(value, storage[key])
        else:
            storage[key] = value
