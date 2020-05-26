#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  leave.py
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

from cg.constants import STATE_LOBBY, STATE_ACTIVE
from cg.packet import CGPacket
from cg.util import uuidify


class LeavePacket(CGPacket):
    state = STATE_LOBBY
    required_keys = []
    allowed_keys = [
        "lobby"
    ]

    def receive(self, msg, cid=None):
        self.peer.remote_state = STATE_ACTIVE

        u = self.cg.client.users_uuid.get(self.cg.client.user_id, None)
        if u is None:
            self.cg.error("Client didn't receive his own user data yet!")
            return
        lobby = self.cg.client.lobby
        if lobby is None:
            self.cg.error(f"{u.username} tried to leave a lobby though he is not in any!")
            return
        elif lobby.uuid != uuidify(msg["lobby"]):
            self.cg.error("The lobby that was sent and the lobby the client is in, don't match")
            return

        lobby.remove_user(u.uuid)
        for btn in self.cg.client.gui.servermain.s_lobby.player_buttons.values():
            btn.player = None

        self.cg.client.gui.servermain.changeSubMenu("main")
