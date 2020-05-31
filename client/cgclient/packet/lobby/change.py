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
from cg.util import uuidify, check_requirements

import cgclient


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
                    continue
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
                        self.cg.send_event("cg:lobby.player.ready", {
                            "player": uid,
                            "ready": udat["ready"]
                        })
                    if "index" in udat:
                        index = self.cg.client.lobby.users.index(uid)
                        self.cg.client.lobby.users[index] = self.cg.client.lobby.users[udat["index"]]
                        self.cg.client.lobby.users[udat["index"]] = uid

                        # Swap the player buttons
                        for index, pbtn in player_buttons.copy().items():
                            if pbtn.player.uuid == uid:
                                player_buttons[index] = player_buttons[udat["index"]]
                                player_buttons[udat["index"]] = pbtn
                                break

            player_buttons[0].pos = (lambda sw, sh, bw, bh: (3, sh * (2 / 9 + (3 * 11 / 72))))  # TODO Fix potential memory leak
            player_buttons[0].redraw()

            player_buttons[1].pos = (lambda sw, sh, bw, bh: (3, sh * (2 / 9 + (2 * 11 / 72))))
            player_buttons[1].redraw()

            player_buttons[2].pos = (lambda sw, sh, bw, bh: (3, sh * (2 / 9 + (1 * 11 / 72))))
            player_buttons[2].redraw()

            player_buttons[3].pos = (lambda sw, sh, bw, bh: (3, sh * (2 / 9)))
            player_buttons[3].redraw()

        if "game" in msg:
            if msg["game"] != self.cg.client.lobby.game:
                # Game has changed
                self.cg.client.lobby.game = msg["game"]
                self.cg.send_event("cg:lobby.game.change", {"game": msg["game"]})

        if "gamerule_validators" in msg:
            if self.cg.client.lobby.gamerule_validators == msg["gamerule_validators"]:
                return

            self.cg.client.lobby.gamerule_validators = msg["gamerule_validators"]
            # No update, just overwrite it
            self.cg.send_event("cg:lobby.gameruleval.change", {"validators": msg["gamerule_validators"]})

            c = 0
            page = -1
            gamerules = {}
            s_gamerule = self.cg.client.gui.servermain.s_gamerule
            for gamerule, grdat in self.cg.client.lobby.gamerule_validators.items():
                c += 1
                gamerules[gamerule] = grdat
                if c % 2 == 0:
                    page += 1

                    # TODO Fix Memory Leak with containers being
                    s_gamerule.gamerule_containers[page] = cgclient.gui.servermain.GameRuleContainer(
                        f"grcontainer{page}", s_gamerule,
                        self.cg.client.gui.window, self.peer.peng,
                        s_gamerule.grid.get_cell([0, 1], [12, 4], border=0), None,
                        page, gamerules
                    )
                    s_gamerule.addWidget(s_gamerule.gamerule_containers[page])
                    gamerules.clear()
            if c % 2 != 0:
                page += 1

                s_gamerule.gamerule_containers[page] = cgclient.gui.servermain.GameRuleContainer(
                    f"grcontainer{page}", s_gamerule,
                    self.cg.client.gui.window, self.peer.peng,
                    s_gamerule.grid.get_cell([0, 1], [12, 4], border=0), None,
                    page, gamerules
                )
                s_gamerule.addWidget(s_gamerule.gamerule_containers[page])
                gamerules.clear()

        if "gamerules" in msg:
            self.cg.client.lobby.gamerules.update(msg["gamerules"])

            self.cg.send_event("cg:lobby.gamerules.change", {"gamerules": msg["gamerules"]})

            for gamerule, btn in self.cg.client.gui.servermain.s_gamerule.rule_buttons.items():
                btn.disabled_background.visible = not check_requirements(gamerule, "", self.cg.client.lobby.gamerules,
                                                                         self.cg.client.lobby.gamerule_validators)

            for gamerule in msg["gamerules"]:
                self.cg.client.gui.servermain.s_gamerule.rule_buttons[gamerule].set_rule(
                    self.cg.client.lobby.gamerules[gamerule]
                )

        if "user_roles" in msg:
            for i in msg["user_roles"]:
                if uuidify(i) in self.cg.client.lobby.user_roles:
                    self.cg.client.lobby.user_roles[uuidify(i)] = msg["user_roles"][i]
                else:
                    self.cg.warn("Tried to set user role of user that is not in the conderned lobby (on the client)!")
                    return
            self.cg.send_event("cg:lobby.admin.change", {
                uuidify(k): v for k, v in msg["user_roles"].items()
            })

