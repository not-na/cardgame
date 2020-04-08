#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  status_user.py
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

from cg.constants import STATE_ACTIVE, STATE_GAME_DK, STATE_LOBBY, STATE_AUTH
from cg.packet import CGPacket
from cg.util import uuidify


class StatusUserPacket(CGPacket):
    state = [STATE_AUTH, STATE_ACTIVE, STATE_LOBBY, STATE_GAME_DK]
    required_keys = [
    ]
    allowed_keys = [
        "username",
        "uuid",
        "status",
    ]

    def receive(self, msg, cid=None):
        if "uuid" in msg:
            self.cg.server.send_user_data(uuidify(msg["uuid"]), cid)
        elif "username" in msg:
            self.cg.server.send_user_data(msg["username"], cid)
        else:
            self.cg.error("Received cg:status.user packet with neither username nor uuid, ignoring")
            return
