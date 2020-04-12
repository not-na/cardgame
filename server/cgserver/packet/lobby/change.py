#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  change.py
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
from cg.constants import STATE_LOBBY, ROLE_CREATOR, ROLE_REMOVE
from cg.packet import CGPacket


class ChangePacket(CGPacket):
    state = STATE_LOBBY
    required_keys = []
    allowed_keys = [
        "users",
        "game",
        "gamerules",
    ]

    def receive(self, msg, cid=None):
        u = self.peer.clients[cid].user

        if "users" in msg:
            for uid, udat in msg["users"].items():
                if "role" in udat and udat["role"] < u.lobby.user_roles[u.uuid] and uid in u.lobby.users:
                    # Users can only up/downgrade to below their own level
                    u.lobby.user_roles[uid] = udat["role"]
                    u.lobby.send_to_all("cg:lobby.change", {
                        "users": {uid: {"role": udat["role"]}},
                    })

                    self.cg.send_event("cg:lobby.user.role", {"user": uid, "cause": u.uuid, "role": udat["role"]})
                else:
                    self.cg.warn(f"User {u.username} with role {u.lobby.user_roles[u.uuid]} tried to up/downgrade user"
                                 f"{uid} to role {udat['role']}")

        if "game" in msg and msg["game"] is not None:
            if u.lobby.user_roles[u.uuid] < ROLE_CREATOR:
                self.cg.warn(f"User {u.username} tried to change a lobby game with insufficient rights")
                return

            oldgame = u.lobby.game
            u.lobby.game = msg["game"]

            if oldgame != u.lobby.game:
                if oldgame is None:
                    # Invite all other party members
                    # TODO: add this after parties are implemented
                    pass

                self.cg.send_event("cg:lobby.game.change", {"old": oldgame, "lobby": u.lobby})
                self.cg.send_event(f"cg:lobby.game.change.{u.lobby.game}", {"old": oldgame, "lobby": u.lobby})

        if "gamerules" in msg:
            if u.lobby.user_roles[u.uuid] < ROLE_CREATOR:
                self.cg.warn(f"User {u.username} tried to change gamerules with insufficient rights")
                return

            u.lobby.update_gamerules(msg["gamerules"])
