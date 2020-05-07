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
            self.cg.client.game.cards[c.cardid] = c
            self.cg.client.game.slots[c.slot].append(c)

            c.redraw()

            # Uncomment if needed, causes a lot of log-spam
            self.cg.info(f"Created card {c.cardid} in slot {c.slot} with value '{c.value}'")
        else:
            # Transfer existing card
            card_id = uuidify(msg["card_id"])

            if card_id not in self.cg.client.game.cards:
                self.cg.error(f"Server moved non-existent card {card_id} from {msg['from_slot']} to {msg['to_slot']}")
                return  # TODO: maybe do some better handling of this situation

            # Get the card
            card: cgclient.gui.card.Card = self.cg.client.game.cards[card_id]

            # Check for sanity of supplied data
            if card not in self.cg.client.game.slots[msg["from_slot"]]:
                self.cg.warn(f"Card {card_id} was not in slot {msg['from_slot']}, but server tried to move it to {msg['to_slot']}")
                # If the from slot was invalid, use the actual from slot instead
                from_slot = card.slot
            else:
                from_slot = msg["from_slot"]

            # Transfer the card internally
            self.cg.client.game.slots[from_slot].remove(card)
            self.cg.client.game.slots[msg["to_slot"]].append(card)

            # Redraw all cards in from and target slots to prevent visual holes
            for c in self.cg.client.game.slots[from_slot]:
                c.start_anim(from_slot, from_slot)
            for c in self.cg.client.game.slots[msg["to_slot"]]:
                if c is not card:
                    c.start_anim(msg["to_slot"], msg["to_slot"])

            # Regardless of where the card was, whatever caused it to be selected is likely not valid anymore
            card.selected = False
            # TODO: check if we need to re-compute card.hovered

            card.slot = msg["to_slot"]
            card.start_anim(from_slot, msg["to_slot"])
            card.redraw()

            self.cg.info(f"Transferred card {card.value} from {from_slot} to {msg['to_slot']}")
