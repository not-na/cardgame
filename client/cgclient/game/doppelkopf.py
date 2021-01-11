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

    gamerules = dict()

    def __init__(self, c: CardGame, game_id: uuid.UUID, player_list: List[uuid.UUID], lobby: cgclient.lobby.Lobby):
        super().__init__(c, game_id, player_list, lobby)
        self.round_num = 1

        self.game_type = "normal"

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
        order = ['h9', 'hk', 'h10', 'ha', 's9', 'sk', 's10', 'sa', 'c9', 'ck', 'c10', 'ca',
                 'd9', 'dk', 'd10', 'da', 'dj', 'hj', 'sj', 'cj', 'dq', 'hq', 'sq', 'cq', 'j0', ""]
        if self.gamerules["dk.heart10"]:
            order.remove('h10')
            order.insert(-2, 'h10')

        if self.game_type in ["solo_hearts", "solo_spades", "solo_clubs"]:
            order = ['d9', 'dk', 'd10', 'da', 'dj', 'hj', 'sj', 'cj', 'dq', 'hq', 'sq', 'cq', 'j0', '']
            if self.game_type != "solo_clubs":
                order = order[:4] + ['c9', 'ck', 'c10', 'ca'] + order[4:]
            if self.game_type != "solo_spades":
                order = order[:4] + ['s9', 'sk', 's10', 'sa'] + order[4:]
            if self.game_type != "solo_hearts":
                order = order[:4] + ['s9', 'sk', 's10', 'sa'] + order[4:]#

            if self.gamerules["dk.heart10"]:
                if not self.gamerules["dk.solo_shift_h10"]:
                    order.remove('h10')
                    order.insert(-2, 'h10')
                else:
                    if self.game_type == "solo_hearts":
                        order.remove('s10')
                        order.insert(-2, 's10')
                    elif self.game_type == "solo_spades":
                        order.remove('c10')
                        order.insert(-2, 'c10')
                    elif self.game_type == "solo_clubs":
                        order.remove('d10')
                        order.insert(-2, 'd10')

        elif self.game_type in ["solo_9s", "solo_jack", "solo_queen", "solo_king", "solo_10s", "solo_aces",
                                "solo_fleshless", "solo_boneless", "solo_brothel", "solo_monastery",
                                "solo_noble_brothel", "solo_picture", "solo_pure_diamonds", "solo_pure_hearts",
                                "solo_pure_spades", "solo_pure_clubs"]:
            order = [color + value for color in ['d', 'h', 's', 'c'] for value in ['9', 'j', 'q', 'k', '10', 'a']] +\
                    ['j0', '']
            if self.game_type == "solo_9s":
                for c in ['d9', 'h9', 's9', 'c9']:
                    order.remove(c)
                order = order[:-2] + ['d9', 'h9', 's9', 'c9'] + order[-2:]
            elif self.game_type == "solo_10s":
                for c in ['d10', 'h10', 's10', 'c10']:
                    order.remove(c)
                order = order[:-2] + ['d10', 'h10', 's10', 'c10'] + order[-2:]
            elif self.game_type == "solo_aces":
                for c in ['da', 'ha', 'sa', 'ca']:
                    order.remove(c)
                order = order[:-2] + ['da', 'ha', 'sa', 'ca'] + order[-2:]
            elif self.game_type == "solo_pure_diamonds":
                order = order[6:-2] + order[:6] + order[-2:]
            elif self.game_type == "solo_pure_hearts":
                order = order[:6] + order[12:-2] + order[6:12] + order[-2:]
            elif self.game_type == "solo_pure_spades":
                order = order[:12] + order[18:-2] + order[12:18] + order[-2:]
            else:  # picture solos and fleshless / boneless / pure clubs
                if self.game_type in ["solo_jacks", "solo_brothel", "solo_monastery", "solo_picture"]:
                    for c in ['dj', 'hj', 'sj', 'cj']:
                        order.remove(c)
                    order = order[:-2] + ['dj', 'hj', 'sj', 'cj'] + order[-2:]
                if self.game_type in ["solo_queens", "solo_brothel", "solo_noble_brothel", "solo_picture"]:
                    for c in ['dq', 'hq', 'sq', 'cq']:
                        order.remove(c)
                    order = order[:-2] + ['dq', 'hq', 'sq', 'cq'] + order[-2:]
                if self.game_type in ["solo_kings", "solo_monastery", "solo_noble_brothel", "solo_picture"]:
                    for c in ['dk', 'hk', 'sk', 'ck']:
                        order.remove(c)
                    order = order[:-2] + ['dk', 'hk', 'sk', 'ck'] + order[-2:]

        self.slots[self.own_hand].sort(key=lambda x: order.index(x.value))

        for c in self.slots[self.own_hand]:
            c.start_anim(self.own_hand, self.own_hand)
