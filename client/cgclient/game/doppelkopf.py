#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  doppelkopf.py
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
from typing import List

import cgclient

from cg import CardGame
from . import CGame


class DoppelkopfGame(CGame):
    SLOT_NAMES: List[str] = [
        "stack",
        "poverty",
        "table",
        "hand0",
        "hand1",
        "hand2",
        "hand3",
        "tricks0",
        "tricks1",
        "tricks2",
        "tricks3",
    ]
    menu: cgclient.gui.ingame.IngameMenu

    default_intent = "play"
    card_intent_packet = "cg:game.dk.card.intent"

    table_index_shift = 0
    poverty_pos = "self"

    def __init__(self, c: CardGame, game_id: uuid.UUID, player_list: List[uuid.UUID], lobby: cgclient.lobby.Lobby):
        super().__init__(c, game_id, player_list, lobby)
        self.round_num = 1

        self.scoreboard_data = {
            "receives": 0,
            "winner": "None",
            "game_type": "None",
            "eyes": (0, 0),
            "game_summary": [],
            "point_change": [0, 0, 0, 0],
            "points": [0, 0, 0, 0],
        }

        self.player_decisions = {
            "continue": set(),
            "adjourn": set(),
            "cancel": set(),
            "end": set()
        }

    def start(self):
        self.menu = self.cg.client.gui.ingame

        self.menu.game_layer.reinit()
        self.menu.gui_layer.s_scoreboard.init_game(self.player_list)

    def sort_cards(self):
        order = ['h9', 'hk', 'ha', 's9', 'sk', 's10', 'sa', 'c9', 'ck', 'c10', 'ca',
                 'd9', 'dk', 'd10', 'da', 'dj', 'hj', 'sj', 'cj', 'dq', 'hq', 'sq', 'cq', 'h10', 'j0', ""]
        self.slots[self.own_hand].sort(key=lambda x: order.index(x.value))

        for c in self.slots[self.own_hand]:
            c.start_anim(self.own_hand, self.own_hand)
