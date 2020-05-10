#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  invite.py
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
from cg.constants import STATE_ACTIVE, STATE_LOBBY, STATE_GAME_DK
from cg.packet import CGPacket
from cg.util import uuidify


class InvitePacket(CGPacket):
    state = [STATE_ACTIVE, STATE_LOBBY]
    required_keys = []
    allowed_keys = [
        "username",
        "inviter",
        "lobby_id"
    ]

    def receive(self, msg, cid=None):
        if "inviter" not in msg:
            self.cg.error("cg:lobby.invite packet must contain key 'inviter'!")
            return

        if "lobby_id" not in msg:
            self.cg.error("cg:lobby.invite packet must contain key 'lobby_id'!")
            return

        self.cg.client.lobby_invitation = [uuidify(msg["inviter"]), uuidify(msg["lobby_id"])]

        self.cg.client.gui.servermain.changeSubMenu("lobby_inv")
