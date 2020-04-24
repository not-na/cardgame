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


class RoundChangePacket(CGPacket):
    state = STATE_GAME_DK
    required_keys = []
    allowed_keys = [
        "round",
        "phase",
        "player_list",
        "game_type",
        "modifiers",
    ]
    side = SIDE_CLIENT

    def receive(self, msg, cid=None):
        if "player_list" in msg:
            own_uuid = self.cg.client.user_id.hex
            self.cg.info(f"Player list: {msg['player_list']}")
            idx = msg["player_list"].index(own_uuid)

            if idx == 0:
                # We are hand0
                out = {
                    0: "self",
                    1: "left",
                    2: "top",
                    3: "right",
                }
            elif idx == 1:
                # We are hand1
                out = {
                    0: "right",
                    1: "self",
                    2: "left",
                    3: "top",
                }
            elif idx == 2:
                # We are hand2
                out = {
                    0: "top",
                    1: "right",
                    2: "self",
                    3: "left",
                }
            elif idx == 3:
                # We are hand3
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
