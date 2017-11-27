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

def create_service_name(service_type):
    service_type = service_type.split(':')

    if len(service_type) == 5:
        return ''.join(service_type[-2:]).replace('-', '_')
    else:
        return service_type[-1].replace('-', '')

