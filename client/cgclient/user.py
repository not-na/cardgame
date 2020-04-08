#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  user.py
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
from typing import Dict, Any

import cg


class User(object):
    def __init__(self, c: cg.CardGame, dat: dict):
        self.cg = c

        self.username: str = "<unknown>"
        self.uuid: uuid.UUID = uuid.UUID(int=0)
        self.status: str = "unknown"

        self.update(dat)

    def update(self, dat: Dict[str, Any]):
        self.username = dat["username"]
        self.uuid = cg.util.uuidify(dat["uuid"])

        self.status = dat["status"]
