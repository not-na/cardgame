#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  card.py
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

import uuid
from typing import Dict


class Card(object):
    def __init__(self, color: str, value: str):
        self.card_id: uuid.UUID = uuid.uuid4()

        self.color = color
        self.value = value

    @property
    def card_value(self) -> str:
        return self.color + self.value

    @card_value.setter
    def card_value(self, value):
        if value == "":
            self.color = ""
            self.value = ""
        else:
            self.color = value[0]
            self.value = value[1:]


def create_dk_deck(with9: int = 8, joker: bool = False):
    if with9 not in [0, 4, 8]:
        raise ValueError("with9 cannot be", with9)

    card_dict: Dict[uuid.UUID, Card] = {}
    for i in range(2):  # Each card 2 times
        for color in ["c", "s", "h", "d"]:
            for value in ["a", "k", "q", "j", "10", "9"]:
                if value == "9" and (with9 == 0 or (with9 == 4 and i == 1)):
                    continue
                card = Card("j", "0") if joker and color == "d" and i == 0 and (
                    (with9 == 0 and value == "k") or (with9 in [4, 8] and value == "9")
                ) else Card(color, value)
                card_dict[card.card_id] = card

    return card_dict


def create_dk_prepped_deck():
    deck = 2
    hands = {}
    if deck == 0:
        hands = {
            0: ['ca', 'ca', 'c10', 'sa', 'sa', 's10', 'ha', 'ha', 'h10', 'da', 'da', 'd10'],
            1: ['ck', 'ck', 'c10', 'sk', 'sk', 's10', 'hk', 'hk', 'h10', 'dk', 'dk', 'd10'],
            2: ['cq', 'cq', 'cj', 'sq', 'sq', 'sj', 'hq', 'hq', 'hj', 'dq', 'dq', 'dj'],
            3: ['c9', 'c9', 'cj', 's9', 's9', 'sj', 'h9', 'h9', 'hj', 'd9', 'd9', 'dj']
        }
    elif deck == 1:
        hands = {
            0: ["ca", "c9", "h9", "s9", "hk", "d10", "sa", "h10", "dk", "hq", "sj", "da"],
            1: ["c10", "c9", "ha", "sk", "sj", "hk", "sk", "sq", "cq", "dk", "d9", "cj"],
            2: ["ca", "c10", "ha", "s10", "s10", "sa", "s9", "h10", "d9", "d10", "da", "cj"],
            3: ["ck", "ck", "h9", "sq", "dj", "hj", "cq", "hq", "dq", "dq", "dj", "hj"]
        }
    elif deck == 2:
        hands = {
            3: ["h10", "h10", "cq", "cq", "sq", "sq", "hq", "hq", "ca", "c10", "h9", "c9"],
            1: ["dq", "dq", "cj", "cj", "sj", "sj", "hj", "hj", "ca", "c10", "ck", "hk"],
            2: ["dj", "dj", "da", "da", "d10", "d10", "dk", "sa", "s10", "sk", "s9", "ha"],
            0: ["d9", "d9", "dk", "sa", "s10", "sk", "s9", "ha", "hk", "c9", "ck", "h9"]
        }

    card_values = []
    for i in range(4):
        for j in range(4):
            for k in range(3):
                card_values.append(hands[j].pop(0))

    cards = {}
    for card in card_values:
        c = Card(card[0], card[1:])
        cards[c.card_id] = c

    return cards
