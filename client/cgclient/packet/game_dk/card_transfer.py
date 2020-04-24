#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  card_transfer
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
import cgclient
from peng3dnet import SIDE_CLIENT

from cg.constants import STATE_GAME_DK
from cg.packet import CGPacket
from cg.util import uuidify


class CardTransferPacket(CGPacket):
    state = STATE_GAME_DK
    required_keys = [
        "card_id",
        "card_value",
        "from_slot",
        "to_slot"
    ]
    allowed_keys = [
        "card_id",
        "card_value",
        "from_slot",
        "to_slot"
    ]
    side = SIDE_CLIENT

    def receive(self, msg, cid=None):
        if msg["from_slot"] is None:
            # Create a new card
            if msg["to_slot"] != "stack":
                self.cg.warn(f"Created card in non-stack slot {msg['to_slot']} with value '{msg['card_value']}'")

            c = cgclient.gui.card.Card(
                self.cg,
                self.cg.client.gui.ingame.game_layer,
                msg["to_slot"],
                uuidify(msg["card_id"]),
                msg["card_value"],
            )
            self.cg.client.gui.ingame.game_layer.cards[c.cardid] = c
            self.cg.client.gui.ingame.game_layer.slots[c.slot].append(c)

            c.redraw()

            self.cg.debug(f"Created card {c.cardid} in slot {c.slot} with value '{c.value}'")
        else:
            # TODO: implement card transfers and animations
            pass
