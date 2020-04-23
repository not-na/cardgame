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
        self.card_value: str = color + value


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
