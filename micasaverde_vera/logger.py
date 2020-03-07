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
:synopsis: logging

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

import os
import logging
from logging import NullHandler

FORMAT = '%(asctime)-15s - %(message)s'

logging.basicConfig(level=None, format=FORMAT)

micasaverde_vera_logger = logging.getLogger(__name__.split('.')[0])
micasaverde_vera_logger.addHandler(NullHandler())
micasaverde_vera_logger.setLevel(logging.INFO)

LOGGING_DATA_PATH = 60
LOGGING_DATA_PATH_WITH_RETURN = 70
LOGGING_TIME_FUNCTION_CALLS = 80

logging.addLevelName(
    LOGGING_DATA_PATH,
    'LOGGING_DATA_PATH'
)
logging.addLevelName(
    LOGGING_DATA_PATH_WITH_RETURN,
    'LOGGING_DATA_PATH_WITH_RETURN'
)
logging.addLevelName(
    LOGGING_TIME_FUNCTION_CALLS,
    'LOGGING_TIME_FUNCTION_CALLS'
)


class Logger(object):
    """
    Wrapper class for logging
    """

    LOGGING_DATA_PATH = LOGGING_DATA_PATH
    LOGGING_DATA_PATH_WITH_RETURN = LOGGING_DATA_PATH_WITH_RETURN
    LOGGING_TIME_FUNCTION_CALLS = LOGGING_TIME_FUNCTION_CALLS

    def __init__(self):
        pass

    def __getattr__(self, item):

        try:
            logger_attr = getattr(micasaverde_vera_logger, item)
        except AttributeError:
            try:
                return getattr(logging, item)
            except AttributeError:
                raise AttributeError(item)

        if hasattr(logger_attr, '__call__'):
            class Wrapper(object):

                def __init__(self, func):
                    self._func = func

                def __call__(self, *args, **kwargs):
                    return self._func(*args, **kwargs)

            return Wrapper(logger_attr)

        return logger_attr

    def __setattr__(self, key, value):
        setattr(micasaverde_vera_logger, key, value)

    def set_output_file(self, file_path, level, write_mode='w'):
        handler = logging.FileHandler(file_path, mode=write_mode)
        handler.setLevel(level)
        # create a logging format
        formatter = logging.Formatter(FORMAT)
        handler.setFormatter(formatter)
        micasaverde_vera_logger.addHandler(handler)
