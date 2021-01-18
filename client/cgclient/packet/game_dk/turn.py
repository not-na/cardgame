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
        "current_player",
        "rebtn_state",
    ]
    side = SIDE_CLIENT

    last_trick = -1

    def receive(self, msg, cid=None):
        cur_player = uuidify(msg["current_player"])
        idx = self.cg.client.gui.ingame.game_layer.player_list.index(cur_player)

        for i, n in self.cg.client.gui.ingame.game_layer.hand_to_player.items():
            l = self.cg.client.gui.ingame.hud_layer.s_main.getWidget(f"{n}img")
            if i == idx:
                l.halo.switchImage("default")
            else:
                l.halo.switchImage("transparent")

            l.redraw()

        if msg["current_trick"] != self.last_trick:
            # New trick, re-calculate offset of table cards
            self.last_trick = msg["current_trick"]

            cidx = self.cg.client.game.player_list.index(cur_player)
            sidx = self.cg.client.game.player_list.index(self.cg.client.user_id)
            offset = cidx-sidx-1
            self.cg.client.game.table_index_shift = offset

        if "rebtn_state" in msg:
            if msg["rebtn_state"] == "invis":
                self.cg.client.gui.ingame.gui_layer.s_ingame.rebtn.visible = False
            elif msg["rebtn_state"] == "enabled":
                self.cg.client.gui.ingame.gui_layer.s_ingame.rebtn.visible = \
                    self.cg.client.gui.ingame.gui_layer.s_ingame.rebtn.enabled = \
                    self.cg.client.gui.ingame.gui_layer.s_ingame.rebtn.purpose != "none"
            elif msg["rebtn_state"] == "disabled":
                self.cg.client.gui.ingame.gui_layer.s_ingame.rebtn.visible = \
                    self.cg.client.gui.ingame.gui_layer.s_ingame.rebtn.purpose != "none"
                self.cg.client.gui.ingame.gui_layer.s_ingame.rebtn.enabled = False

        # Autoplay mode
        if self.cg.client.game is not None and self.cg.client.game.AUTOPLAY and \
                cur_player == self.cg.client.user_id:
            self.cg.send_event("cg:game.dk.cheat.my_turn")
