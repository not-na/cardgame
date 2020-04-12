#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  lobby.py
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
from typing import Dict, List, Union, Any

import cg
from cg.constants import ROLE_NONE


class Lobby(object):
    def __init__(self, c: cg.CardGame, u: uuid.UUID):
        self.cg = c

        self.uuid: uuid.UUID = u
        self.game: Union[None, str] = None

        self.users: List[uuid.UUID] = []
        self.user_roles: Dict[uuid.UUID, int] = {}
        self.user_ready: Dict[uuid.UUID, bool] = {}

        self.gamerules: Dict[str, Any] = {}

        self.gamerule_validators: Dict[str, Dict] = {}

    def add_user(self, uid: uuid.UUID, udat: dict):
        if uid in self.users:
            self.cg.error(f"User {uid} already in lobby, ignoring")
            return

        self.users.append(uid)
        self.user_roles[uid] = udat.get("role", ROLE_NONE)
        self.user_ready[uid] = udat.get("ready", False)

    def remove_user(self, uid: uuid.UUID):
        if uid not in self.users:
            self.cg.crash(f"Tried to remove {uid} from lobby, but they are not a member")

        self.cg.send_event("cg:lobby.user.remove", {"user": uid})

        del self.users[self.users.index(uid)]
        del self.user_roles[uid]
        del self.user_ready[uid]

        self.cg.info(f"Removed user {uid} from lobby")
