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
from cg.constants import STATE_LOBBY, ROLE_CREATOR, ROLE_REMOVE, ROLE_ADMIN
from cg.packet import CGPacket
from cg.util import uuidify


class ChangePacket(CGPacket):
    state = STATE_LOBBY
    required_keys = []
    allowed_keys = [
        "users",
        "user_order",
        "user_roles",
        "game",
        "gamerules",
        "gamerule_validators",
        "supported_bots",
    ]

    def receive(self, msg, cid=None):
        u = self.peer.clients[cid].user
        lobby = self.cg.server.lobbies.get(u.lobby, None)
        if lobby is None:
            self.cg.warn("Received Lobby Change packet though the sender is in no lobby!")

        if "users" in msg:
            for uid, udat in msg["users"].items():
                if "role" in udat and udat["role"] < lobby.user_roles[u.uuid] and uid in lobby.users:
                    # Users can only up/downgrade to below their own level
                    lobby.user_roles[uid] = udat["role"]
                    lobby.send_to_all("cg:lobby.change", {
                        "users": {uid: {"role": udat["role"]}},
                    })

                    self.cg.send_event("cg:lobby.user.role", {"user": uid, "cause": u.uuid, "role": udat["role"]})
                else:
                    self.cg.warn(f"User {u.username} with role {lobby.user_roles[u.uuid]} tried to up/downgrade user"
                                 f"{uid} to role {udat['role']}")

        if "user_order" in msg:
            if lobby.user_roles[u.uuid] >= ROLE_ADMIN:
                user_order = [uuidify(p) for p in msg["user_order"]]
                lobby.users = user_order
                for p in lobby.users:
                    self.cg.server.send_to_user(p, "cg:lobby.change", {
                        "users": {i.hex: {
                            "index": lobby.users.index(i)
                        } for i in lobby.users}
                    })
            else:
                self.cg.server.send_status_message(u, "warn", "cg:msg.lobby.change_user_order.missing_rights")
                self.cg.warn(f"User {u.username} tried to change a lobby user order with insufficient rights")
                self.cg.server.send_to_user(u, "cg:lobby.change", {
                    "users": {i.hex: {
                        "index": lobby.users.index(i)
                    } for i in lobby.users}
                })

        if "game" in msg and msg["game"] is not None:
            if lobby.user_roles[u.uuid] < ROLE_ADMIN:
                self.cg.server.send_status_message(u, "warn", "cg:msg.lobby.change_game.missing_rights")
                self.cg.warn(f"User {u.username} tried to change a lobby game with insufficient rights")
                return

            lobby.game_data = None

            oldgame = lobby.game
            lobby.game = msg["game"]

            if oldgame != lobby.game:
                if oldgame is None:
                    # Invite all other party members
                    # TODO: add this after parties are implemented
                    self.cg.warn("Invite of other players of party is not yet implemented")

                self.cg.send_event("cg:lobby.game.change", {"old": oldgame, "lobby": lobby})
                self.cg.send_event(f"cg:lobby.game.change.{lobby.game}", {"old": oldgame, "lobby": lobby})

        if "gamerules" in msg:
            if lobby.user_roles[u.uuid] < ROLE_ADMIN:
                self.cg.server.send_status_message(u, "warn", "cg:msg.lobby.change_gamerules.missing_rights")
                self.cg.warn(f"User {u.username} tried to change gamerules with insufficient rights")
                self.cg.server.send_to_user(u, "cg:lobby.change", {
                    "gamerules": {gamerule: lobby.gamerules[gamerule] for gamerule in lobby.gamerules}
                })
                return

            lobby.game_data = None
            lobby.update_gamerules(msg["gamerules"])

        if "user_roles" in msg:
            if lobby.user_roles[u.uuid] < ROLE_ADMIN:
                self.cg.server.send_status_message(u, "warn", "cg:msg.lobby.change_admin.missing_rights")
                self.cg.warn(f"User {u.username} tried to make someone an admin with insufficient rights")
                return
            for i in msg["user_roles"]:
                if uuidify(i) in lobby.user_roles:
                    lobby.user_roles[uuidify(i)] = msg["user_roles"][i]
                else:
                    self.cg.warn("Tried to set user role of user that is not in the conderned lobby!")

            lobby.send_to_all("cg:lobby.change", {
                "user_roles": {k.hex: v for k, v in lobby.user_roles.items()}
            })
