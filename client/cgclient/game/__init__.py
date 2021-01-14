#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
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
from typing import Callable, List, Mapping, Optional

import cgclient

import cg


def register_games(reg: Callable):
    from . import doppelkopf
    reg("doppelkopf", doppelkopf.DoppelkopfGame)


class CGame(object):
    SLOT_NAMES: List[str]
    default_intent: str
    card_intent_packet: str

    def __init__(self, c: cg.CardGame, game_id: uuid.UUID, player_list: List[uuid.UUID], lobby: cgclient.lobby.Lobby):
        self.cg: cg.CardGame = c

        self.game_id = game_id
        self.player_list = player_list

        self.lobby = lobby

        # Ensure all players exist in the local database
        for p in player_list:
            if p not in self.cg.client.users_uuid:
                # This is unlikely to happen if the server is implemented correctly
                # But it can happen if a game is not implemented properly
                self.cg.warn(f"Player {p} is not yet in client user database, requesting more information")
                self.cg.client.send_message("cg:status.user", {"uuid": p.hex})

        self.slots: Mapping[str, List[cgclient.gui.card.Card]] = {name: [] for name in self.SLOT_NAMES}
        self.cards: Mapping[uuid.UUID, cgclient.gui.card.Card] = {}

        self.player_order: List[uuid.UUID] = []

        self.own_hand: Optional[str] = None

        self.cards_batchsize: int = 1
        self.cur_cardbatch: List[uuid.UUID] = []
        self.cur_intent: str = "play"

    def uuid_to_side(self, u: uuid.UUID, offset=0):
        cidx = self.cg.client.gui.ingame.game_layer.player_list.index(u)
        return self.cg.client.gui.ingame.game_layer.hand_to_player[(cidx+offset) % 4]

    def start(self):
        pass

    def select_card(self, card: uuid.UUID):
        if card not in self.cards:
            self.cg.crash(f"Attempted to select card {card} that does not exist")
            return
        c = self.cards[card]
        if card in self.cur_cardbatch:
            self.cg.warn(f"Tried to select card {c.value} ({card}) that was already selected")
            return
        if self.cards[card] not in self.slots[self.own_hand]:
            self.cg.warn(f"Tried to play Card {c.value} ({card}) not in own hand")
            return

        self.cur_cardbatch.append(card)
        c.selected = True
        c.redraw()

        self.process_selection()

    def process_selection(self):
        if len(self.cur_cardbatch) > self.cards_batchsize:
            # Complain in the logs, but send the data anyway
            self.cg.error(f"{len(self.cur_cardbatch)} cards are selected, but {self.cur_intent} only expects {self.cards_batchsize}")
        if len(self.cur_cardbatch) >= self.cards_batchsize:
            self.cg.info(f"Sending card intent with intent '{self.cur_intent}' and {len(self.cur_cardbatch)} card(s)")
            # Send the packet
            if len(self.cur_cardbatch) == 1:
                self.cg.client.send_message(self.card_intent_packet, {
                    "intent": self.cur_intent,
                    "card": self.cur_cardbatch[0].hex,
                })
            else:
                self.cg.client.send_message(self.card_intent_packet, {
                    "intent": self.cur_intent,
                    "card": [cid.hex for cid in self.cur_cardbatch],
                })

            self.clear_selection()
            self.cur_intent = self.default_intent
            self.cards_batchsize = 1

    def clear_selection(self):
        for card in self.cur_cardbatch:
            self.cards[card].selected = False
            self.cards[card].redraw()
            self.cards[card].start_anim(self.cards[card].slot, self.cards[card].slot)
        self.cur_cardbatch = []

    def sort_cards(self):
        pass
