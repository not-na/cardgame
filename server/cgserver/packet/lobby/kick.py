#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  kick.py
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

from cg.constants import STATE_LOBBY
from cg.packet import CGPacket
from cg.util import uuidify


class KickPacket(CGPacket):
    state = STATE_LOBBY
    required_keys = [
        "uuid",
        "reason"
    ]
    allowed_keys = [
        "uuid",
        "reason"
    ]
    side = SIDE_SERVER

    def receive(self, msg, cid=None):
        u = self.peer.clients[cid].user
        lobby = self.cg.server.lobbies.get(u.lobby, None)
        if lobby is None:
            self.cg.error("cg:lobby.kick packet can only be sent while in a lobby!")
            return

        user = self.cg.server.users_uuid.get(uuidify(msg["uuid"]), None)

        if user is None:
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.kick.user_not_exist", data={
                "uuid": msg["uuid"]
            })
        elif user.uuid not in lobby.users:
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.kick.user_not_in_lobby", data={
                "username": user.username
            })
        elif lobby.started:
            self.cg.server.send_status_message(u, "warning", "cg:msg.lobby.kick.lobby_started")

        else:
            lobby.remove_user(user.uuid)

            if msg["reason"].strip() == "":
                self.cg.server.send_status_message(user, "notice", "cg:msg.lobby.kick.no_reason")
            else:
                self.cg.server.send_status_message(user, "notice", "cg:msg.lobby.kick.reason", data={
                    "reason": msg["reason"]
                })

            self.cg.server.send_status_message(u, "notice", "cg:msg.lobby.kick.success", data={
                "username": user.username
            })
