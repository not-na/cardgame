#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  lobby.py
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
from typing import Union, Dict, List, Any

import uuid

import cgserver

import cg
from cg.constants import ROLE_REMOVE


class Lobby(object):
    def __init__(self, c: cg.CardGame, u: Union[None, uuid.UUID] = None):
        self.cg: cg.CardGame = c

        self.uuid: uuid.UUID = u if u is not None else uuid.uuid4()
        self.game: Union[str, None] = None

        self.users: List[uuid.UUID] = []
        self.user_roles: Dict[uuid.UUID, int] = {}
        self.user_ready: Dict[uuid.UUID, bool] = {}

        self.gamerules: Dict[str, Any] = {}
        # Debugging for Doppelkopf
        if cgserver.game.CGame.DEV_MODE:
            self.gamerules = {
                "dk.pigs": "two_reservation",
                "dk.superpigs": "reservation",
                "dk.throw": "reservation",
                "dk.throw_cases": [
                    "5_9",
                    "5_k",
                    "4_9+4_k",
                    "9_all_c",
                    "k_all_c",
                    "7full",
                    "t<hj",
                    "t<dj"
                ],
                "dk.poverty": "sell",
                "dk.poverty_consequence": "redeal"
            }

    def remove_user(self, user: uuid.UUID, left=False):
        if user not in self.users:
            self.cg.warn(f"Tried to remove user {user} from lobby {self.uuid}, but they are not a member")
            return

        self.cg.debug(f"Removing user {user} from lobby {self.uuid}")

        del self.users[self.users.index(user)]
        del self.user_roles[user]
        del self.user_ready[user]

        if not left:
            self.cg.server.send_to_user(user, "cg:lobby.leave", {"lobby": self.uuid.hex})

        self.send_to_all("cg:lobby.change", {
            "users": {user: {"role": ROLE_REMOVE}},
        })

    def add_user(self, user: cgserver.user.User, role: int):
        if user.uuid in self.users:
            self.cg.error(f"Tried to add user {user.username} to lobby {self.uuid}, but they are already a member")

        # Make sure all users know each other
        for u in self.users:
            # Send all existing users to the new user
            self.cg.server.send_user_data(u, user.uuid)

            # Send the new user to all existing users
            self.cg.server.send_user_data(user.uuid, u)

        user.lobby = self.uuid

        # Add user to internal DB
        self.users.append(user.uuid)
        self.user_roles[user.uuid] = role
        self.user_ready[user.uuid] = False

        self.cg.server.send_to_user(user, "cg:lobby.join", {
            "lobby": self.uuid.hex,
        })

        self.cg.server.send_to_user(user, "cg:lobby.change", {
            "users": {u.hex: {
                "ready": self.user_ready[u],
                "role": self.user_roles[u],
                }
                for u in self.users
            }
        })

        self.send_to_all("cg:lobby.change", {
            "users": {user.uuid.hex: {
                "ready": self.user_ready[user.uuid],
                "role": self.user_roles[user.uuid],
            }},
        }, user)

    def send_to_all(self, packet: str, data: dict, exclude=None):
        for u in self.users:
            if u != exclude:
                self.cg.server.send_to_user(u, packet, data)

    def set_gamerule(self, rule: str, value):
        if rule not in self.cg.server.game_reg[self.game].GAMERULES:
            # Ignore unknown rule
            return

        valid, out = cg.util.validate(value, self.cg.server.game_reg[self.game].GAMERULES[rule])
        # Ignore valid flag for now

        self.gamerules[rule] = out

        self.send_to_all("cg:lobby.change", {
            "gamerules": {rule: out},
        })

    def update_gamerules(self, new: Dict[str, Any]):
        ch = {}

        for rule, value in new.items():
            if rule not in self.cg.server.game_reg[self.game].GAMERULES:
                # Ignore unknown rule
                continue

            valid, out = cg.util.validate(value, self.cg.server.game_reg[self.game].GAMERULES[rule])
            # Ignore valid flag for now
            self.gamerules[rule] = out
            ch[rule] = out

        self.send_to_all("cg:lobby.change", {
            "gamerules": ch,
        })

    def set_variant(self, variant: str):
        self.cg.warn(f"Setting Variants is currently not implemented")

