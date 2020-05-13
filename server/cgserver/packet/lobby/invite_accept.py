#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  invite_accept.py
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
from peng3dnet import SIDE_SERVER

from cg.constants import STATE_ACTIVE, ROLE_PLAYER
from cg.packet import CGPacket
from cg.util import uuidify


class InviteAcceptPacket(CGPacket):
    state = STATE_ACTIVE
    required_keys = [
        "accepted",
        "lobby_id",
        "inviter"
    ]
    allowed_keys = [
        "accepted",
        "lobby_id",
        "inviter"
    ]
    side = SIDE_SERVER

    def receive(self, msg, cid=None):
        u = self.peer.clients[cid].user
        lobby = self.cg.server.lobbies.get(uuidify(msg["lobby_id"]), None)
        inviter = self.cg.server.users_uuid.get(uuidify(msg["inviter"]), None)

        if lobby is None:
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.invite.accept.lobby_not_exists")
        elif inviter.uuid not in lobby.users:
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.invite.accept.invalid_inviter")
        elif u.uuid not in lobby.invitations:
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.invite.accept.not_invited")
        elif lobby.started:
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.invite.accept.lobby_started_game")
        elif self.cg.server.game_reg[lobby.game].check_playercount(len(lobby.users), True):
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.invite.accept.lobby_full")
        else:
            if msg["accepted"]:
                lobby.add_user(u, ROLE_PLAYER)
            else:
                self.cg.server.send_status_message(inviter, "notice", "cg:msg.lobby.invite.decline", data={
                    "username": u.username
                })
            lobby.invitations.remove(u.uuid)

