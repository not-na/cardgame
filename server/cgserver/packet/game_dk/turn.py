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


class TurnPacket(CGPacket):
    state = STATE_GAME_DK
    required_keys = [
        "current_trick",
        "total_tricks",
        "current_player",
    ]
    allowed_keys = [
        "current_trick",
        "total_tricks",
        "current_player",
        "rebtn_state",
        "pigbtn_state",
    ]
    side = SIDE_CLIENT
