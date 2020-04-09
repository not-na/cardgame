#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  join.py
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
import cgclient
from peng3dnet import SIDE_CLIENT

from cg.constants import STATE_ACTIVE, STATE_LOBBY
from cg.packet import CGPacket
from cg.util import uuidify


class JoinPacket(CGPacket):
    state = STATE_ACTIVE
    required_keys = [
        "lobby",
    ]
    allowed_keys = [
        "lobby"
    ]
    side = SIDE_CLIENT

    def receive(self, msg, cid=None):
        self.peer.remote_state = STATE_LOBBY

        self.cg.client.lobby = cgclient.lobby.Lobby(self.cg, uuidify(msg["lobby"]))

        self.cg.send_event("cg:lobby.join", {"lobby": self.cg.client.lobby})
        self.cg.info(f"Joined lobby {self.cg.client.lobby.uuid}")

