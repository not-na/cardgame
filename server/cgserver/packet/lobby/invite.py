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
        if "username" not in msg:
            self.cg.error("cg:lobby.invite packet must contain key 'username'!")
            return

        u = self.peer.clients[cid].user
        lobby = self.cg.server.lobbies.get(u.lobby, None)
        if lobby is None:
            self.cg.error("cg:lobby.invite packet can only be sent while in a lobby!")
            return

        user = self.cg.server.users.get(msg["username"], None)

        if self.cg.server.game_reg[lobby.game].check_playercount(len(lobby.users), True):
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.invite.lobby_full")
        elif user is None:
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.invite.user_does_not_exist", data={
                "username": msg["username"]
            })

        elif user.cid not in self.peer.clients:
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.invite.user_not_online", data={
                "username": msg["username"]
            })

        elif user.state == STATE_LOBBY:
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.invite.user_in_lobby", data={
                "username": msg["username"]
            })

        elif user.state == STATE_GAME_DK:
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.invite.user_in_dk_game", data={
                "username": msg["username"],
            })

        elif user.state != STATE_ACTIVE:
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.invite.user_cur_not_available", data={
                "username": msg["username"],
                "state": user.state
            })

        else:
            self.cg.server.send_status_message(u, "notice", "cg:msg.lobby.invite.user_invited", data={
                "username": msg["username"]
            })
            self.cg.server.send_user_data(user.uuid, u.uuid)
            lobby.invitations.add(user.uuid)

            self.cg.server.send_to_user(user, "cg:lobby.invite", {
                "inviter": u.uuid.hex,
                "lobby_id": lobby.uuid.hex
            })

            self.cg.info(f"{u.username} invited {user.username} to lobby {lobby.uuid}")
