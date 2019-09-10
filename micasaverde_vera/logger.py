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
