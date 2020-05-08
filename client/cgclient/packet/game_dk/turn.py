#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  turn.py
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


class TurnPacket(CGPacket):
    state = STATE_GAME_DK
    required_keys = [
        "current_trick",
        "total_tricks",
        "current_player"
    ]
    allowed_keys = [
        "current_trick",
        "total_tricks",
        "current_player"
    ]
    side = SIDE_CLIENT

    last_trick = -1

    def receive(self, msg, cid=None):
        cur_player = uuidify(msg["current_player"])
        idx = self.cg.client.gui.ingame.game_layer.player_list.index(cur_player)

        for i, n in self.cg.client.gui.ingame.game_layer.hand_to_player.items():
            l = self.cg.client.gui.ingame.hud_layer.s_main.labels[n]
            if i == idx:
                c = [0, 255, 0, 255]
            else:
                c = [100, 100, 100, 255]

            l.font_color = c
            l._label.color = c
            l.redraw()

        if msg["current_trick"] != self.last_trick:
            # New trick, re-calculate offset of table cards
            self.last_trick = msg["current_trick"]

            cidx = self.cg.client.game.player_list.index(cur_player)
            sidx = self.cg.client.game.player_list.index(self.cg.client.user_id)
            offset = cidx-sidx-1
            self.cg.client.game.table_index_shift = offset
