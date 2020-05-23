#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  round_change.py
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
from peng3dnet import SIDE_CLIENT

from cg.constants import STATE_GAME_DK
from cg.packet import CGPacket
from cg.util import uuidify


class RoundChangePacket(CGPacket):
    state = STATE_GAME_DK
    required_keys = []
    allowed_keys = [
        "round",
        "phase",
        "player_list",
        "game_type",
        "modifiers",
        "winner",
        "eyes",
        "extras",
        "game_summary",
    ]
    side = SIDE_CLIENT

    def receive(self, msg, cid=None):
        if "player_list" in msg:
            own_uuid = self.cg.client.user_id.hex
            self.cg.info(f"Player list: {msg['player_list']}")
            idx = msg["player_list"].index(own_uuid)

            if idx == 0:
                # We are hand0
                self.cg.client.game.own_hand = "hand0"
                out = {
                    0: "self",
                    1: "left",
                    2: "top",
                    3: "right",
                }
            elif idx == 1:
                # We are hand1
                self.cg.client.game.own_hand = "hand1"
                out = {
                    0: "right",
                    1: "self",
                    2: "left",
                    3: "top",
                }
            elif idx == 2:
                # We are hand2
                self.cg.client.game.own_hand = "hand2"
                out = {
                    0: "top",
                    1: "right",
                    2: "self",
                    3: "left",
                }
            elif idx == 3:
                # We are hand3
                self.cg.client.game.own_hand = "hand3"
                out = {
                    0: "left",
                    1: "top",
                    2: "right",
                    3: "self",
                }
            else:
                self.cg.crash(f"Invalid own-index of {idx}")
                return

            self.cg.client.gui.ingame.game_layer.hand_to_player = out
            self.cg.client.gui.ingame.game_layer.player_list = list(map(uuidify, msg["player_list"]))

            for uidx, uraw in enumerate(msg["player_list"]):
                uid = uuidify(uraw)
                n = out[uidx]
                l = self.cg.client.gui.ingame.hud_layer.s_main.labels[n]
                name = self.cg.client.get_user_name(uid)
                l.label = f"{name}"

        if "phase" in msg:
            self.cg.info(f"Now in round phase {msg['phase']}")
            if msg["phase"] == "loading":
                self.cg.client.gui.ingame.gui_layer.s_scoreboard.continuebtn.label = self.cg.client.gui.peng.tl(
                    "cg:gui.menu.ingame.scoreboard.continuebtn.label")
                self.cg.client.gui.ingame.gui_layer.s_scoreboard.continuebtn.pressed = False
                self.cg.client.game.player_decisions = {
                    "continue": set(),
                    "adjourn": set(),
                    "cancel": set(),
                    "end": set()
                }

                self.cg.client.gui.ingame.gui_layer.changeSubMenu("loadingscreen")
            elif msg["phase"] == "dealing":
                self.cg.client.gui.ingame.gui_layer.changeSubMenu("ingame")
            elif msg["phase"] == "reservations":
                pass
            elif msg["phase"] == "tricks":
                pass
            elif msg["phase"] == "counting":
                pass
            elif msg["phase"] == "end":
                if not ("game_type" in msg and "winner" in msg and "eyes" in msg and "modifiers" in msg
                        and "extras" in msg and "round" in msg):
                    self.cg.warn("Missing parameters in cg:game.dk.change packet with phase 'end'")
                    return
                self.cg.client.gui.ingame.game_layer.clean_up()

                self.cg.client.game.scoreboard_data["winner"] = msg["winner"]
                self.cg.client.game.scoreboard_data["game_type"] = msg["game_type"]
                self.cg.client.game.scoreboard_data["eyes"] = msg["eyes"]
                self.cg.client.game.scoreboard_data["game_summary"] = msg["game_summary"]

                self.cg.client.game.round_num = msg["round"]
            else:
                self.cg.crash(f"Invalid round phase {msg['phase']}")
