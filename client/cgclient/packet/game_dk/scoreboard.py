#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  scoreboard.py
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


class ScoreboardPacket(CGPacket):
    state = STATE_GAME_DK
    required_keys = [
        "player"
    ]
    allowed_keys = [
        "player",
        "pips",
        "pip_change",
        "points",
        "point_change"
    ]
    side = SIDE_CLIENT

    def receive(self, msg, cid=None):
        if uuidify(msg["player"]) not in self.cg.client.game.player_list:
            self.cg.warn("Received cg:game.dk.scoreboard packet with player id that is not in this game")
            return

        if "points" in msg and "point_change" in msg:
            self.cg.client.game.scoreboard_data["points"][
                self.cg.client.game.player_list.index(uuidify(msg["player"]))] = msg["points"]
            self.cg.client.game.scoreboard_data["point_change"][
                self.cg.client.game.player_list.index(uuidify(msg["player"]))] = msg["point_change"]
