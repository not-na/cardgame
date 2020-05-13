#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
#  
#  Copyright 2020 contributors of cardgame
#  
#  This file is part of cardgame.
#
#  cardgame is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  cardgame is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with cardgame.  If not, see <http://www.gnu.org/licenses/>.
#
import uuid
from math import floor
from typing import Union, Dict, Tuple, List

from . import cache
from . import serializer
from . import time


def uuidify(uuid_in: Union[str, uuid.UUID]):
    if isinstance(uuid_in, str):
        return uuid.UUID(uuid_in)
    elif isinstance(uuid_in, uuid.UUID):
        return uuid_in
    else:
        raise TypeError(f"Unsupported UUID representation of type {type(uuid_in)}")


def validate(data: Union[float, bool, str, List], validator: Dict) -> Tuple[bool, Union[float, bool, str, List]]:
    if data is None:
        return False, validator["default"]
    elif validator["type"] == "bool":
        if data not in [True, False]:
            return False, validator["default"]
        return True, data
    elif validator["type"] == "str":
        if not isinstance(data, str):
            return False, validator["default"]
        elif len(data) < validator["minlen"]:
            # Cannot stretch data - use default
            return False, validator["default"]
        elif len(data) > validator["maxlen"]:
            # Cut off data
            return False, data[:validator["maxlen"]]
        else:
            # Valid
            return True, data
    elif validator["type"] == "select":
        if data not in validator["options"]:
            return False, validator["default"]
        else:
            return True, data
    elif validator["type"] == "number":
        if not (isinstance(data, float) or isinstance(data, int)):
            return False, validator["default"]
        else:
            mn = validator["min"]
            mx = validator["max"]
            st = validator["step"]

            out = floor((data-mn)/st)*st+mn
            if out > mx:
                return False, mx
            elif out < mn:
                return False, mn
            elif out != data:
                return False, out
            return True, data
    elif validator["type"] == "active":
        out = []
        valid = True
        for k in data:
            if k in validator["options"]:
                out.append(k)
            else:
                valid = False
        return valid, out
    else:
        raise NotImplementedError(f"Validator type {validator['type']} is unknown")


def check_requirements(name: str, value: Union[float, bool, str], gamerules: Dict, validator: Dict):
    for req, valid in validator[name]["requirements"].items():
        value = gamerules.get(req, validator[req]["default"])
        if value not in valid:
            return False
    return True
