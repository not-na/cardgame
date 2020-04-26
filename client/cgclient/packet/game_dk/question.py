#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  question.py
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


class QuestionPacket(CGPacket):
    state = STATE_GAME_DK
    required_keys = [
        "type",
        "target"
    ]
    allowed_keys = [
        "type",
        "target"
    ]
    side = SIDE_CLIENT

    def receive(self, msg, cid=None):
        if uuidify(msg["target"]) == self.cg.client.user_id:
            if msg["type"] in [
                "reservation",
                "throw",
                "pigs",
                "superpigs",
                "poverty",
                "poverty_accept",
                "wedding",
            ]:
                # Simple 2-choice question
                self.cg.client.gui.ingame.popup_layer.ask_question_2choice(msg["type"])
            elif msg["type"] == "poverty_trump_choice":
                # TODO: Notify player that they have to play some cards
                self.cg.info(f"Choose three cards for poverty_trump_choice")
                # Choose three cards
                self.cg.client.game.clear_selection()

                self.cg.client.game.cur_intent = "pass_card"
                self.cg.client.game.cards_batchsize = 3
            elif msg["type"] == "poverty_return_choice":
                self.cg.info(f"Choose three cards for poverty_return_choice")
                # TODO: Notify player that they have to play some cards
                # Choose three cards
                self.cg.client.game.clear_selection()

                self.cg.client.game.cur_intent = "return_card"
                self.cg.client.game.cards_batchsize = 3
            else:
                # TODO: implement these other question types
                # Missing:
                # poverty_return_trumps
                # wedding_clarification_trick
                # solo
                # accusation_vote
                self.cg.warn(f"Question type {msg['type']} is not yet implemented")
        else:
            # Question not for this player, only display notification
            # TODO: implement player notifications
            self.cg.info(f"Question for other player {msg['target']} of type {msg['type']}")
