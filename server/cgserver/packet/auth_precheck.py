#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  auth_precheck.py
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
import re

from cg.constants import STATE_AUTH
from cg.packet import CGPacket


USER_PATTERN = re.compile("[a-zA-Z][a-zA-Z0-9_]{2,15}")


class AuthPrecheckPacket(CGPacket):
    state = STATE_AUTH
    required_keys = [
        "username",
    ]
    allowed_keys = [
        "username",
        "valid",
        "exists",
        "key",
    ]

    def receive(self, msg, cid=None):
        user = msg["username"]

        valid = USER_PATTERN.fullmatch(user) is not None and not user.lower().startswith("bot")
        exists = user.lower() in self.cg.server.users

        self.peer.send_message("cg:auth.precheck", {
            "username": user,
            "valid": valid,
            "exists": exists,
            "key": "",  # TODO: implement password encryption
        }, cid)
