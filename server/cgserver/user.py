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
from typing import Union

import cg


class User(object):
    def __init__(self, server, c: cg.CardGame, user: str, udat: dict):
        self.server = server
        self.cg = c

        self.username: str = user
        self.pwd: str = udat.get("pwd", "")
        self.uuid: uuid.UUID = cg.util.uuidify(udat.get("uuid", uuid.uuid4()))

        self.cid: Union[None, int] = None
        self.lobby: Union[None, uuid.UUID] = None

        # TODO: add more user data here

    def serialize(self):
        return {
            "pwd": self.pwd,
            "uuid": self.uuid.hex,
        }
