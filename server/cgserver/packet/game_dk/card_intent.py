#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  card_intend.py
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
from peng3dnet import SIDE_SERVER

from cg.constants import STATE_GAME_DK
from cg.packet import CGPacket


class CardIntentPacket(CGPacket):
    state = STATE_GAME_DK
    required_keys = [
        "intent",
        "card"
    ]
    allowed_keys = [
        "intent",
        "card"
    ]
    side = SIDE_SERVER

    def receive(self, msg, cid=None):
        t = msg["intent"]
        c = msg["card"]

        if t in ["pass_card", "return_card"]:
            self.cg.send_event("cg:game.dk.reservation_poverty_pass_card", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t,
                "card": c
            })
