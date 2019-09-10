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
:synopsis: categories

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""

import logging
from . import utils

logger = logging.getLogger(__name__)


class Categories(object):

    def __init__(self, ha_gateway, node):
        self.ha_gateway = ha_gateway
        self._categories = node

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]

        try:
            return self[item]
        except KeyError:
            raise AttributeError

    def __getitem__(self, item):
        item = str(item)
        item = item.split('.')
        if len(item) == 1:
            item += ['0']

        return self._categories[item[0]][item[1]]
