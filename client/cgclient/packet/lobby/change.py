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

from cg.constants import STATE_LOBBY, ROLE_NONE, ROLE_REMOVE
from cg.packet import CGPacket
from cg.util import uuidify


class ChangePacket(CGPacket):
    state = STATE_LOBBY
    required_keys = []
    allowed_keys = [
        "users",
        "game",
        "gamerules",
        "gamerule_validators",
    ]

    def receive(self, msg, cid=None):
        if self.cg.client.lobby is None:
            self.cg.fatal(f"Not in lobby, but received lobby change packet")
            self.cg.crash("Received lobby change packet while not in lobby")

        if "users" in msg:
            player_buttons = self.cg.client.gui.servermain.s_lobby.player_buttons
            for uid, udat in msg["users"].items():
                uid = uuidify(uid)
                if udat.get("role", ROLE_NONE) == ROLE_REMOVE:
                    # Remove user from visual user list
                    player_buttons[self.cg.client.lobby.users.index(uid)].player = None
                    # Remove user from list
                    self.cg.client.lobby.remove_user(uid)
                    return
                elif uid not in self.cg.client.lobby.users:
                    # New user, add
                    self.cg.client.lobby.add_user(uid, udat)
                    # Add to visual user list
                    player_buttons[self.cg.client.lobby.users.index(uid)].player = self.cg.client.get_user(uid)
                else:
                    # Some user data changed
                    if "role" in udat:
                        self.cg.client.lobby.user_roles[uid] = udat["role"]
                    if "ready" in udat:
                        self.cg.client.lobby.user_ready[uid] = udat["ready"]
                    if "index" in udat:
                        # Get old player button
                        for index, pbtn in player_buttons.copy().items():
                            if pbtn.player.uuid == uid:
                                # Swap the player buttons
                                player_buttons[index] = player_buttons[udat["index"]]
                                player_buttons[udat["index"]] = pbtn
                                break

        if "game" in msg:
            if msg["game"] != self.cg.client.lobby.game:
                # Game has changed
                self.cg.client.lobby.game = msg["game"]
                self.cg.send_event("cg:lobby.game.change", {"game": msg["game"]})

        if "gamerules" in msg:
            self.cg.client.lobby.gamerules.update(msg["gamerules"])

            self.cg.send_event("cg:lobby.gamerules.change", {"gamerules": msg["gamerules"]})

        if "gamerule_validators" in msg:
            self.cg.client.lobby.gamerule_validators = msg["gamerule_validators"]
            # No update, just overwrite it
            self.cg.send_event("cg:lobby.gameruleval.change", {"validators": msg["gamerule_validators"]})
