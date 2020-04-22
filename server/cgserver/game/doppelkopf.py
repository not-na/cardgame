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
import random
from typing import List, Optional, Dict, Tuple, Union

from cg.error import CardTransferError, GameStateError, WrongPlayerError, InvalidMoveError, RuleError
from cg.util import uuidify
from . import CGame
from .card import *

import cg
import uuid

from cg.constants import STATE_GAME_DK


class DoppelkopfGame(CGame):
    GAMERULES = {
        "general.wrongmove": {
            "type": "select",
            "default": "prohibit",
            "options": [
                "prohibit",
                "allow_points",
                "allow_stopgame",
            ],
            "requirements": {},
        },
        "dk.heart10": {
            "type": "bool",
            "default": True,
            "requirements": {},
        },
        "dk.heart10_prio": {
            "type": "select",
            "default": "first",
            "options": [
                "first",
                "second",
            ],
            "requirements": {
                "dk.heart10": [True],
            },
        },
        "dk.heart10_lasttrick": {
            "type": "select",
            "default": "first",
            "options": [
                "first",
                "second",
            ],
            "requirements": {
                "dk.heart10": [True],
            },
        },
        "dk.doppelkopf": {
            "type": "bool",
            "default": True,
            "requirements": {},
        },
        "dk.fox": {
            "type": "bool",
            "default": True,
            "requirements": {},
        },
        "dk.fox_lasttrick": {
            "type": "bool",
            "default": False,
            "requirements": {
                "dk.fox": [True],
            },
        },
        "dk.pigs": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "one_first",
                "one_on_play",
                "one_on_fox",
                "two_reservation",
                "two_on_play",
            ],
            "requirements": {
                "dk.fox": [True],
            },
        },
        "dk.superpigs": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "reservation",  # dk.pigs: two_reservation
                "on_pig",
                "on_play",
            ],
            "requirements": {
                "dk.fox": [True],
                "dk.pigs": ["two_reservation", "two_on_play"],
            },
        },
        "dk.charlie": {
            "type": "bool",
            "default": True,
            "requirements": {},
        },
        "dk.charlie_broken": {
            "type": "bool",
            "default": False,
            "requirements": {
                "dk.charlie": [True],
            },
        },
        "dk.jane": {  # Lieschen Müller
            "type": "bool",
            "default": False,
            "requirements": {
                "dk.charlie": [True],
                "dk.charlie_broken": [True],
            },
        },
        "dk.charlie_prio": {
            "type": "select",
            "default": "first",
            "options": [
                "first",
                "second",
            ],
            "requirements": {
                "dk.charlie": [True],
            },
        },
        "dk.without9": {
            "type": "select",
            "default": "with_all",
            "options": [
                "with_all",
                "with_four",
                "without",
            ],
            "requirements": {},
        },
        "dk.heart_trick": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.sec_black_trick": {
            "type": "bool",
            "default": False,
            "requirements": {
                "dk.without9": ["with_all"],
            },
        },
        "dk.joker": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "over_h10",  # dk.heart10: True
                "over_pigs",  # dk.pigs: not None
                "over_superpigs",  # dk.superpigs: not None
            ],
            "requirements": {},
        },
        "dk.hobgoblin": {  # Klabautermann
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.poverty": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "sell",
                "circulate",
                "circulate_duty",
            ],
            "requirements": {},
        },
        "dk.poverty_consequence": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "redeal"
                "black_sow",
                "ramsch",
            ],
            "requirements": {
                "dk.poverty": ["sell", "circulate"]
            }
        },
        "dk.throw": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "reservation",
                "throw",
            ]
        },
        "dk.throw_cases": {
            "type": "active",
            "default": [],
            "options": [
                "5_9",
                "5_k",
                "4_9+4_k",
                "9_all_c",
                "k_all_c",
                "7full",
                "t<hj",
                "t<dj"
            ],
            "requirements": {
                "dk.throw": ["reservation", "throw"],
            },
        },
        "dk.coward": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "210_no_re",
                "240_no_u90",
            ],
            "requirements": {},
        },
        "dk.wedding": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "3_trick",
                "wish_trick",
            ],
            "requirements": {},
        },
        "dk.repeat_game": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.re_kontra": {
            "type": "select",
            "default": "+2",
            "options": [
                "+2",
                "*2",
                "*2_extra"
            ],
            "requirements": {},
        },
        "dk.knock": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.buck_round": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "succession",
                "parallel",
            ],
            "requirements": {},
        },
        "dk.buck_cause": {
            "type": "active",
            "default": [],
            "options": [
                "4hearts",
                "draw",
                "0points",  # repeat_game: False
                "re_kontra_lost",
                "solo_lost",
            ],
            "requirements": {
                "dk.buck_round": ["succession", "parallel"],
            },
        },
        "dk.buck_amount": {
            "type": "number",
            "default": 4,
            "min": 1,
            "max": 4,
            "step": 1,
        },
        "dk.solo_shift_h10": {
            "type": "bool",
            "default": False,
            "requirements": {
                "dk.heart10": [True],
            },
        },
        "dk.solist_begins": {
            "type": "bool",
            "default": False
        },
        "dk.solo.null": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.boneless": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.pure_color": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.king": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.brothel": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.noble_brothel": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.picture": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.monastery": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.aces": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.10s": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.9s": {
            "type": "bool",
            "default": False,
            "requirements": {
                "dk.without9": ["with_all"]
            },
        },
    }
    SOLO_ORDER = [
        "solo_aces",
        "solo_10s",
        "solo_picture",
        "solo_noble_brothel",
        "solo_monastery",
        "solo_king",
        "solo_brothel",
        "solo_queen",
        "solo_jack",
        "solo_9s",
        "solo_clubs",
        "solo_spades",
        "solo_hearts",
        "solo_diamonds",
        "solo_pure_clubs",
        "solo_pure_spades",
        "solo_pure_hearts",
        "solo_pure_diamonds",
        "solo_fleshless",
        "solo_null",
        "solo_boneless"

    ]

    def __init__(self, c: cg.CardGame, lobby: uuid.UUID):
        super().__init__(c, lobby)

        self.players: List[uuid.UUID] = self.lobby.users

        self.rounds: List[DoppelkopfRound] = []
        self.current_round: Optional[DoppelkopfRound] = None

    def start(self):
        self.send_to_all("cg:game.start", {
            "game_type": "doppelkopf",
            "game_id": self.game_id.hex
        })

        for player in self.players:
            self.cg.server.server.clients[self.cg.server.users_uuid[player].cid].state = STATE_GAME_DK

        self.start_round(0)

    def start_round(self, round_num: int):
        players = self.players[round_num:] + self.players[:round_num]  # Each round, another player begins

        self.current_round = DoppelkopfRound(self, players, self.gamerules)
        self.rounds.append(self.current_round)

    def send_to_all(self, packet: str, data: dict, exclude: Union[uuid.UUID, List[uuid.UUID]] = None):
        for u in self.players:
            if (type(u) == uuid.UUID and u != exclude) or (type(u) == list and u not in exclude):
                self.cg.server.send_to_user(u, packet, data)

    def register_event_handlers(self):
        super().register_event_handlers()

        # Add event handler registration here


class DoppelkopfRound(object):
    def __init__(self, game: DoppelkopfGame, players: List[uuid.UUID], buckround: bool = False):
        self.register_event_handlers()

        self.game: DoppelkopfGame = game

        self.players: List[uuid.UUID] = players
        self.current_player: Optional[uuid.UUID] = None

        self.game_state: str = ""
        self.reserv_state: str = ""

        self.game_type: str = "normal"

        self.parties: Dict[str, List[uuid.UUID]] = {
            "re": [],
            "kontra": [],
            "none": []
        }
        self.player_eyes: Dict[uuid.UUID, int] = dict((p, 0) for p in self.players)

        self.modifiers: Dict[str, List[str]] = {
            "general": ["buckround"] if buckround else [],
            "re": [],
            "kontra": []
        }

        self.cards: Dict[uuid.UUID, Card] = {}
        self.slots: Dict[str, List[uuid.UUID]] = {
            "stack": [],
            "hand0": [],
            "hand1": [],
            "hand2": [],
            "hand3": [],
            "poverty": [],
            "table": [],
            "tricks0": [],
            "tricks1": [],
            "tricks2": [],
            "tricks3": [],
        }

        self.moves: Dict[int, Dict[str, Union[str, uuid.UUID]]] = {}
        self.move_counter: int = 0

        self.players_with_reserv: List[uuid.UUID] = []
        self.players_with_solo: Dict[uuid.UUID, str] = {}
        self.poverty_cards: List[uuid.UUID] = []
        self.poverty_player: Optional[uuid.UUID] = None

        self.pigs: Tuple[bool, Optional[uuid.UUID]] = (False, None)
        self.superpigs: Tuple[bool, Optional[uuid.UUID]] = (False, None)
        self.pig_call: bool = True
        self.superpig_call: bool = True

        self.trick_num: int = 0
        self.current_trick: List[Tuple[uuid.UUID, uuid.UUID]] = []

        self.start_hands = self.hands

    @property
    def hands(self) -> Dict[uuid.UUID, List[uuid.UUID]]:
        hands = {}
        for i, p in enumerate(self.players):
            hands[p] = self.slots[f"hand{i}"].copy()
        return hands

    @property
    def moves_by_player(self) -> Dict[uuid.UUID, Dict[int, Dict[str, str]]]:
        mbp = {}
        for p in self.players:
            mbp[p] = {}
        for i, move in self.moves.items():
            mbp[move["player"]][i] = {"type": move["type"], "data": move["data"]}

        return mbp

    def add_move(self, player: uuid.UUID, tp: str, data: str):
        self.moves[self.move_counter] = {
            "player": player,
            "type": tp,
            "data": data
        }
        self.move_counter += 1

    def transfer_card(self, card: Card, from_slot: str, to_slot: str):
        if from_slot == "stack":
            if "hand" in to_slot:
                receiver = self.players[int(to_slot.strip("hand"))]
                self.game.cg.server.send_to_user(receiver, "cg:game.dk.card.transfer", {
                    "card_id": card.card_id,
                    "card_value": card.card_value,
                    "from_slot": from_slot,
                    "to_slot": to_slot
                })
                self.game.send_to_all("cg:game.dk.card.transfer", {
                    "card_id": card.card_id,
                    "card_value": "",
                    "from_slot": from_slot,
                    "to_slot": to_slot
                }, exclude=receiver)
            else:
                raise CardTransferError(f"Cannot transfer card from {from_slot} to {to_slot}")

        elif "hand" in from_slot:
            if to_slot == "poverty":
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.card.transfer", {
                    "card_id": card.card_id,
                    "card_value": card.card_value,
                    "from_slot": from_slot,
                    "to_slot": to_slot
                })
                self.game.send_to_all("cg:game.dk.card.transfer", {
                    "card_id": card.card_id,
                    "card_value": "",
                    "from_slot": from_slot,
                    "to_slot": to_slot
                }, exclude=self.current_player)

            elif to_slot == "table":
                self.game.send_to_all("cg:game.dk.card.transfer", {
                    "card_id": card.card_id,
                    "card_value": card.card_value,
                    "from_slot": from_slot,
                    "to_slot": to_slot
                })
            else:
                raise CardTransferError(f"Cannot transfer card from {from_slot} to {to_slot}")

        elif from_slot == "poverty":
            if to_slot == "poverty":
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.card.transfer", {
                    "card_id": card.card_id,
                    "card_value": card.card_value,
                    "from_slot": from_slot,
                    "to_slot": to_slot
                })
                self.game.send_to_all("cg:game.dk.card.transfer", {
                    "card_id": card.card_id,
                    "card_value": "",
                    "from_slot": from_slot,
                    "to_slot": to_slot
                }, exclude=self.current_player)

            elif "hand" in to_slot:
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.card.transfer", {
                    "card_id": card.card_id,
                    "card_value": card.card_value,
                    "from_slot": from_slot,
                    "to_slot": to_slot
                })
                self.game.send_to_all("cg:game.dk.card.transfer", {
                    "card_id": card.card_id,
                    "card_value": "",
                    "from_slot": from_slot,
                    "to_slot": to_slot
                }, exclude=self.current_player)

            else:
                raise CardTransferError(f"Cannot transfer card from {from_slot} to {to_slot}")

        elif from_slot == "table":
            if "tricks" in to_slot:
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.card.transfer", {
                    "card_id": card.card_id,
                    "card_value": "",
                    "from_slot": from_slot,
                    "to_slot": to_slot
                })

        else:
            raise CardTransferError(f"Cannot transfer card from {from_slot} to {to_slot}")

        self.slots[from_slot].remove(card.card_id)
        self.slots[to_slot].append(card.card_id)

    def get_card_color(self, card: Card) -> str:
        # Clubs
        if card.card_value == "c9":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_spades", "solo_jacks", "solo_queens",
                                  "solo_brothel", "solo_kings", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_spades", "solo_aces", "solo_10s"]:
                return "clubs"

        if card.card_value == "cj":
            if self.game_type in ["solo_queens", "solo_kings", "solo_noble_brothel", "solo_fleshless", "solo_boneless",
                                  "solo_pure_diamonds", "solo_pure_hearts", "solo_pure_spades", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "clubs"

        if card.card_value == "cq":
            if self.game_type in ["solo_jacks", "solo_kings", "solo_monastery", "solo_fleshless", "solo_boneless",
                                  "solo_pure_diamonds", "solo_pure_hearts", "solo_pure_spades", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "clubs"

        if card.card_value == "ck":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_spades", "solo_jacks", "solo_queens",
                                  "solo_brothel", "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_spades", "solo_aces", "solo_10s", "solo_9s"]:
                return "clubs"

        if card.card_value == "c10":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_jacks", "solo_queens", "solo_brothel",
                                  "solo_kings", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_spades", "solo_aces", "solo_9s"]:
                return "clubs"
            elif self.game_type == "solo_spades":
                if not self.game.gamerules["dk.solo_shift_h10"]:
                    return "clubs"

        if card.card_value == "ca":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_spades", "solo_jacks", "solo_queens",
                                  "solo_brothel", "solo_kings", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_spades", "solo_10s", "solo_9s"]:
                return "clubs"

        # Spades
        if card.card_value == "s9":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_clubs", "solo_jacks", "solo_queens",
                                  "solo_brothel", "solo_kings", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_clubs", "solo_aces", "solo_10s"]:
                return "spades"

        if card.card_value == "sj":
            if self.game_type in ["solo_queens", "solo_kings", "solo_noble_brothel", "solo_fleshless", "solo_boneless",
                                  "solo_pure_diamonds", "solo_pure_hearts", "solo_pure_clubs", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "spades"

        if card.card_value == "sq":
            if self.game_type in ["solo_jacks", "solo_kings", "solo_monastery", "solo_fleshless", "solo_boneless",
                                  "solo_pure_diamonds", "solo_pure_hearts", "solo_pure_clubs", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "spades"

        if card.card_value == "sk":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_clubs", "solo_jacks", "solo_queens",
                                  "solo_brothel", "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_clubs", "solo_aces", "solo_10s", "solo_9s"]:
                return "spades"

        if card.card_value == "s10":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_jacks", "solo_queens", "solo_brothel",
                                  "solo_kings", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_clubs", "solo_aces", "solo_9s"]:
                return "spades"
            elif self.game_type == "solo_hearts":
                if not self.game.gamerules["dk.solo_shift_h10"]:
                    return "spades"

        if card.card_value == "sa":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_clubs", "solo_jacks", "solo_queens",
                                  "solo_brothel", "solo_kings", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_clubs", "solo_10s", "solo_9s"]:
                return "spades"

        # Hearts
        if card.card_value == "h9":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_spades", "solo_clubs", "solo_jacks", "solo_queens",
                                  "solo_brothel", "solo_kings", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s"]:
                return "hearts"

        if card.card_value == "hj":
            if self.game_type in ["solo_queens", "solo_kings", "solo_noble_brothel", "solo_fleshless", "solo_boneless",
                                  "solo_pure_diamonds", "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "hearts"

        if card.card_value == "hq":
            if self.game_type in ["solo_jacks", "solo_kings", "solo_monastery", "solo_fleshless", "solo_boneless",
                                  "solo_pure_diamonds", "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "hearts"

        if card.card_value == "hk":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_spades", "solo_clubs", "solo_jacks", "solo_queens",
                                  "solo_brothel", "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s", "solo_9s"]:
                return "hearts"

        if card.card_value == "h10":
            if self.game_type in ["solo_queens", "solo_brothel", "solo_kings", "solo_monastery", "solo_noble_brothel",
                                  "solo_picture", "solo_fleshless", "solo_boneless", "solo_pure_diamonds",
                                  "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_9s"]:
                return "hearts"
            elif self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                    "solo_diamonds", "solo_null"]:
                if not self.game.gamerules["dk.heart10"]:
                    return "hearts"
            elif self.game_type in ["solo_spades", "solo_clubs"]:
                if self.game.gamerules["dk.solo_shift_h10"]:
                    return "hearts"

        if card.card_value == "ha":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_spades", "solo_clubs", "solo_jacks", "solo_queens",
                                  "solo_brothel", "solo_kings", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_spades", "solo_pure_clubs", "solo_10s", "solo_9s"]:
                return "hearts"

        # Diamonds
        if card.card_value == "d9":
            if self.game_type in ["solo_hearts", "solo_spades", "solo_clubs", "solo_jacks", "solo_queens",
                                  "solo_brothel", "solo_kings", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "", "solo_pure_hearts", "solo_pure_spades",
                                  "solo_pure_clubs", "solo_aces", "solo_10s"]:
                return "diamonds"

        if card.card_value == "dj":
            if self.game_type in ["solo_queens", "solo_kings", "solo_noble_brothel", "solo_fleshless", "solo_boneless",
                                  "solo_pure_hearts", "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "diamonds"

        if card.card_value == "dq":
            if self.game_type in ["solo_jacks", "solo_kings", "solo_monastery", "solo_fleshless", "solo_boneless",
                                  "solo_pure_hearts", "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "diamonds"

        if card.card_value == "dk":
            if self.game_type in ["solo_hearts", "solo_spades", "solo_clubs", "solo_jacks", "solo_queens",
                                  "solo_brothel", "solo_fleshless", "solo_boneless","solo_pure_hearts",
                                  "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s", "solo_9s"]:
                return "diamonds"

        if card.card_value == "d10":
            if self.game_type in ["solo_hearts", "solo_spades", "solo_jacks", "solo_queens", "solo_brothel",
                                  "solo_kings", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_pure_hearts", "solo_pure_spades",
                                  "solo_pure_clubs", "solo_aces", "solo_9s"]:
                return "diamonds"
            elif self.game_type == "solo_clubs":
                if not self.game.gamerules["dk.solo_shift_h10"]:
                    return "diamonds"

        if card.card_value == "da":
            if self.game_type in ["solo_hearts", "solo_spades", "solo_clubs", "solo_jacks", "solo_queens",
                                  "solo_brothel", "solo_kings", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_pure_hearts", "solo_pure_spades",
                                  "solo_pure_clubs", "solo_10s", "solo_9s"]:
                return "diamonds"

        return "trump"

    def get_trick_winner(self) -> uuid.UUID:
        cards_sorted = sorted([i[1] for i in self.current_trick], key=self.get_card_sort_key, reverse=True)

        if self.cards[cards_sorted[0]].card_value == self.cards[cards_sorted[1]].card_value:
            if self.get_card_sort_key(self.cards[cards_sorted[0]]) == 100:  # Valid h10 (or s10, c10, d10 if solo)
                if self.current_trick == len(self.cards) / 4:  # Last Trick
                    if self.game.gamerules["dk.heart10_lasttrick"] == "first":
                        for i in self.current_trick:  # Return first h10
                            if i[1] == cards_sorted[0]:
                                return i[0]
                    elif self.game.gamerules["dk.heart10_lasttrick"] == "second":
                        for i in self.current_trick:  # Return second h10
                            if i[1] == cards_sorted[1]:
                                return i[0]
                else:  # Not last Trick
                    if self.game.gamerules["dk.heart10_prio"] == "first":
                        for i in self.current_trick:  # Return first h10
                            if i[1] == cards_sorted[0]:
                                return i[0]
                    elif self.game.gamerules["dk.heart10_prio"] == "second":
                        for i in self.current_trick:  # Return second h10
                            if i[1] == cards_sorted[1]:
                                return i[0]

            if self.cards[cards_sorted[0]].card_value == "cj":  # Jack of clubs, Charlie
                if self.current_trick == len(self.cards) / 4:  # Last Trick
                    if self.game.gamerules["dk.charlie_prio"] == "first":
                        for i in self.current_trick:  # Return first jack of clubs
                            if i[1] == cards_sorted[0]:
                                return i[0]
                    elif self.game.gamerules["dk.charlie_prio"] == "second":
                        for i in self.current_trick:  # Return second jack of clubs
                            if i[1] == cards_sorted[1]:
                                return i[0]

        # If the rules above don't apply, return the highest card
        for i in self.current_trick:
            if i[1] == cards_sorted[0]:
                return i[0]

    def get_card_sort_key(self, card: Card) -> int:
        first_card = self.cards[self.current_trick[0][1]]

        if self.get_card_color(first_card) != "trump":
            # Card is of same color -> color was served
            if self.get_card_color(card) == self.get_card_color(first_card):
                if card.value == "9":
                    return 1
                elif card.value == "j":
                    return 3
                elif card.value == "q":
                    return 4
                elif card.value == "k":
                    return 5
                elif card.value == "10":
                    return 6
                elif card.value == "a":
                    return 7

            # Card is neither of same color nor trump -> card was dropped
            elif self.get_card_color(card) != self.get_card_color(first_card):
                return 0

        elif self.get_card_color(first_card) == "trump":
            # 9, king, 10, ace of diamonds in normal version
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow",
                                  "ramsch", "solo_diamonds", "solo_null"]:
                if card.card_value == "d9" and not (
                        self.superpig_call and self.game.gamerules["dk.without9"] == "with_all"):
                    return 10
                elif card.card_value == "dk" and not (
                        self.superpig_call and self.game.gamerules["dk.without9"] != "with_all"):
                    return 11
                elif card.card_value == "d10":
                    return 12
                elif card.card_value == "da" and not self.pig_call:
                    return 13

                elif card.card_value == "h10" and self.game.gamerules["dk.heart10"]:
                    return 100
                elif card.card_value == "da" and self.pig_call:
                    return 200
                elif card.card_value == "d9" and (
                        self.superpig_call and self.game.gamerules["dk.without9"] == "with_all"):
                    return 300
                elif card.card_value == "dk" and (
                        self.superpig_call and self.game.gamerules["dk.without9"] != "with_all"):
                    return 300

            # 9, king, 10, ace of hearts in hearts solo
            elif self.game_type == "solo_hearts":
                if card.card_value == "h9" and not (
                        self.superpig_call and self.game.gamerules["dk.without9"] == "with_all"):
                    return 10
                elif card.card_value == "hk" and not (
                        self.superpig_call and self.game.gamerules["dk.without9"] != "with_all"):
                    return 11
                elif card.card_value == "h10" and not self.game.gamerules["dk.solo_shift_h10"]:
                    return 12
                elif card.card_value == "ha" and not self.pig_call:
                    return 13

                elif card.card_value == "h10" and self.game.gamerules["dk.heart10"] and not self.game.gamerules[
                    "dk.solo_shift_h10"]:
                    return 100
                elif card.card_value == "s10" and self.game.gamerules["dk.solo_shift_h10"]:
                    return 100
                elif card.card_value == "ha" and self.pig_call:
                    return 200
                elif card.card_value == "h9" and (
                        self.superpig_call and self.game.gamerules["dk.without9"] == "with_all"):
                    return 300
                elif card.card_value == "hk" and (
                        self.superpig_call and self.game.gamerules["dk.without9"] != "with_all"):
                    return 300

            # 9, king, 10, ace of spades in spades solo
            elif self.game_type == "solo_spades":
                if card.card_value == "s9" and not (
                        self.superpig_call and self.game.gamerules["dk.without9"] == "with_all"):
                    return 10
                elif card.card_value == "sk" and not (
                        self.superpig_call and self.game.gamerules["dk.without9"] != "with_all"):
                    return 11
                elif card.card_value == "s10" and not self.game.gamerules["dk.solo_shift_h10"]:
                    return 12
                elif card.card_value == "sa" and not self.pig_call:
                    return 13

                elif card.card_value == "s10" and self.game.gamerules["dk.heart10"] and not self.game.gamerules[
                    "dk.solo_shift_h10"]:
                    return 100
                elif card.card_value == "c10" and self.game.gamerules["dk.solo_shift_h10"]:
                    return 100
                elif card.card_value == "sa" and self.pig_call:
                    return 200
                elif card.card_value == "s0" and (
                        self.superpig_call and self.game.gamerules["dk.without9"] == "with_all"):
                    return 300
                elif card.card_value == "sk" and (
                        self.superpig_call and self.game.gamerules["dk.without9"] != "with_all"):
                    return 300

            # 9, king, 10, ace of clubs in clubs solo
            elif self.game_type == "solo_clubs":
                if card.card_value == "c9" and not (
                        self.superpig_call and self.game.gamerules["dk.without9"] == "with_all"):
                    return 10
                elif card.card_value == "ck" and not (
                        self.superpig_call and self.game.gamerules["dk.without9"] != "with_all"):
                    return 11
                elif card.card_value == "c10" and not self.game.gamerules["dk.solo_shift_h10"]:
                    return 12
                elif card.card_value == "ca" and not self.pig_call:
                    return 13

                elif card.card_value == "c10" and self.game.gamerules["dk.heart10"] and not self.game.gamerules[
                    "dk.solo_shift_h10"]:
                    return 100
                elif card.card_value == "d10" and self.game.gamerules["dk.solo_shift_h10"]:
                    return 100
                elif card.card_value == "ca" and self.pig_call:
                    return 200
                elif card.card_value == "c9" and (
                        self.superpig_call and self.game.gamerules["dk.without9"] == "with_all"):
                    return 300
                elif card.card_value == "ck" and (
                        self.superpig_call and self.game.gamerules["dk.without9"] != "with_all"):
                    return 300

            # Jacks in normal version and solos with jack trumps
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_spades", "solo_clubs", "solo_jacks",
                                  "solo_brothel", "solo_monastery", "solo_picture", "solo_null"]:
                if card.card_value == "dj":
                    return 20
                elif card.card_value == "hj":
                    return 21
                elif card.card_value == "sj":
                    return 22
                elif card.card_value == "cj":
                    return 23

            # Queens in normal version and solos with queen trumps
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_spades", "solo_clubs", "solo_queens",
                                  "solo_brothel", "solo_noble_brothel", "solo_picture", "solo_null"]:
                if card.card_value == "dq":
                    return 30
                elif card.card_value == "hq":
                    return 31
                elif card.card_value == "sq":
                    return 32
                elif card.card_value == "cq":
                    return 33

            # Kings in solos with king trumps
            if self.game_type in ["solo_kings", "solo_monastery", "solo_noble_brothel", "solo_picture"]:
                if card.card_value == "dk":
                    return 40
                elif card.card_value == "hk":
                    return 41
                elif card.card_value == "sk":
                    return 42
                elif card.card_value == "ck":
                    return 43

            # 9, jack, queen, king, 10, ace of diamonds in pure diamonds solo
            if self.game_type == "solo_pure_diamonds":
                if card.card_value == "d9":
                    return 10
                elif card.card_value == "dj":
                    return 12
                elif card.card_value == "dq":
                    return 13
                elif card.card_value == "dk":
                    return 14
                elif card.card_value == "d10":
                    return 15
                elif card.card_value == "da":
                    return 16

            # 9, jack, queen, king, 10, ace of hearts in pure hearts solo
            if self.game_type == "solo_pure_hearts":
                if card.card_value == "h9":
                    return 10
                elif card.card_value == "hj":
                    return 12
                elif card.card_value == "hq":
                    return 13
                elif card.card_value == "hk":
                    return 14
                elif card.card_value == "h10":
                    return 15
                elif card.card_value == "ha":
                    return 16

            # 9, jack, queen, king, 10, ace of spades in pure spades solo
            if self.game_type == "solo_pure_spades":
                if card.card_value == "s9":
                    return 10
                elif card.card_value == "sj":
                    return 12
                elif card.card_value == "sq":
                    return 13
                elif card.card_value == "sk":
                    return 14
                elif card.card_value == "s10":
                    return 15
                elif card.card_value == "sa":
                    return 16

            # 9, jack, queen, king, 10, ace of clubs in pure clubs solo
            if self.game_type == "solo_pure_clubs":
                if card.card_value == "c9":
                    return 10
                elif card.card_value == "cj":
                    return 12
                elif card.card_value == "cq":
                    return 13
                elif card.card_value == "ck":
                    return 14
                elif card.card_value == "c10":
                    return 15
                elif card.card_value == "ca":
                    return 16

            # Aces in aces solo
            if self.game_type == "solo_aces":
                if card.card_value == "da":
                    return 10
                elif card.card_value == "ha":
                    return 11
                elif card.card_value == "sa":
                    return 12
                elif card.card_value == "ca":
                    return 13

            # 10s in tens solo
            if self.game_type == "solo_10s":
                if card.card_value == "d10":
                    return 10
                elif card.card_value == "h10":
                    return 11
                elif card.card_value == "s10":
                    return 12
                elif card.card_value == "c10":
                    return 13

            # 9s in nines solo
            if self.game_type == "solo_9s":
                if card.card_value == "d9":
                    return 10
                elif card.card_value == "h9":
                    return 11
                elif card.card_value == "s9":
                    return 12
                elif card.card_value == "c9":
                    return 13

            # Jolly Joker
            if card.card_value == "jj":
                if self.game.gamerules["dk.joker"] == "over_h10":
                    return 150
                elif self.game.gamerules["dk.joker"] == "over_pigs":
                    return 250
                elif self.game.gamerules["dk.joker"] == "over_superpigs":
                    return 350

    def get_eyes(self, card: Card) -> int:
        if card.card_value == "jj":
            return 0

        if card.value == "9":
            return 0
        elif card.value == "j":
            return 2
        elif card.value == "q":
            return 3
        elif card.value == "k":
            return 4
        elif card.value == "10":
            return 10
        elif card.value == "a":
            return 11

    def start(self):
        # Create card deck
        with9 = self.game.gamerules["dk.without9"]
        with9 = 0 if with9 == "without" else 4 if with9 == "with_four" else 8

        joker = self.game.gamerules["dk.joker"]
        joker = joker != "None"

        self.cards = create_dk_deck(with9=with9, joker=joker)

        for card_id in self.cards:
            self.slots["stack"].append(card_id)

        # Deal the cards
        self.game_state = "dealing"

        for i in range(4):  # Four times
            for j in range(4):  # To each player
                for k in range(3):  # 3 cards
                    stack = self.slots["stack"]
                    card_id = stack.pop(random.randint(0, len(stack) - 1))
                    self.transfer_card(self.cards[card_id], "stack", f"hand{j}")

        # Reservations: Only initialisation, the rest of the code is handled by event handlers
        self.game_state = "reservations"
        self.reserv_state = "reservation"
        self.current_player = self.players[0]
        self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
            "type": "reservation",
            "target": self.players[0].hex
        })

    def start_normal(self):
        self.reserv_state = "finished"

        for player, hand in self.hands.items():
            # Check for silent wedding
            if list(map(lambda x: self.cards[x].card_value, hand)).count("cq") == 2:
                self.players_with_solo[player] = "silent_wedding"
                self.start_solo(player)
                return

            # Put the players into their parties
            elif list(map(lambda x: self.cards[x].card_value, hand)).count("cq") == 1:
                self.parties["re"].append(player)
            elif list(map(lambda x: self.cards[x].card_value, hand)).count("cq") == 0:
                self.parties["kontra"].append(player)

            # Check for pigs
            if self.game.gamerules["dk.pigs"] in ["one_first", "one_on_play", "two_on_play"]:
                if list(map(lambda x: self.cards[x].card_value, hand)).count("da") == 2:
                    self.pigs = (True, player)

            # Check for superpigs
            if self.game.gamerules["dk.superpigs"] in ["on_pig", "on_play"]:
                if self.pigs[0]:
                    if self.game.gamerules["dk.without9"] == "with_all":
                        if list(map(lambda x: self.cards[x].card_value, hand)).count("d9") == 2:
                            self.superpigs = (True, player)
                    elif self.game.gamerules["dk.without9"] in ["with_four", "without"]:
                        if list(map(lambda x: self.cards[x].card_value, hand)).count("dk") == 2:
                            self.superpigs = (True, player)

        self.game_type = "normal"
        self.game_state = "tricks"

        self.current_player = self.players[0]
        self.trick_num = 1

        self.game.send_to_all("cg:game.dk.turn", {
            "current_trick": 1,
            "total_tricks": len(self.cards) / 4,
            "current_player": self.current_player.hex
        })

    def start_solo(self, solist: uuid.UUID):
        pass

    def start_poverty(self, accepter: uuid.UUID):
        pass

    def start_black_sow(self):
        pass

    def start_ramsch(self):
        pass

    def start_wedding(self, bride: uuid.UUID, trick: Optional[str] = None):
        pass

    def exit_round(self, remake=False):
        pass

    def register_event_handlers(self):
        self.game.cg.add_event_listener("cg:game.dk.reservation", self.handle_reservation)
        self.game.cg.add_event_listener("cg:game.dk.reservation_solo", self.handle_reservation_solo)
        self.game.cg.add_event_listener("cg:game.dk.reservation_throw", self.handle_reservation_throw)
        self.game.cg.add_event_listener("cg:game.dk.reservation_pigs", self.handle_reservation_pigs)
        self.game.cg.add_event_listener("cg:game.dk.reservation_superpigs", self.handle_reservation_superpigs)
        self.game.cg.add_event_listener("cg:game.dk.reservation_poverty", self.handle_reservation_poverty)
        self.game.cg.add_event_listener("cg:game.dk.reservation_poverty_pass_card",
                                        self.handle_reservation_poverty_pass_card)
        self.game.cg.add_event_listener("cg:game.dk.reservation_poverty_accept", self.handle_reservation_poverty_accept)
        self.game.cg.add_event_listener("cg:game.dk.reservation_wedding", self.handle_reservation_wedding)
        self.game.cg.add_event_listener("cg:game.dk.reservation_wedding_clarification_trick",
                                        self.handle_reservation_wedding_clarification_trick)

        self.game.cg.add_event_listener("cg:game.dk.play_card", self.handle_play_card)
        self.game.cg.add_event_listener("cg:game.dk.call_pigs", self.handle_call_pigs)
        self.game.cg.add_event_listener("cg:game.dk.call_superpigs", self.handle_call_superpigs)

    def handle_reservation(self, event: str, data: Dict):
        # Check for correct states
        if self.game_state is not "reservations":
            raise GameStateError(f"Game state for reservation handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state is not "reservation":
            raise GameStateError(
                f"Reservations state for reservation handling must be 'reservation', not {self.reserv_state}!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the reservation handling packet is not the current player!")

        # Remember players with reservation
        if data["type"] == "reservation_yes":
            self.players_with_reserv.append(self.current_player)

        # Announce decision
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": data["type"]
        })

        # Register move
        self.add_move(self.current_player, "announcement", data["type"])

        # Go on to next player
        self.current_player = self.players[(self.players.index(self.current_player) + 1) % len(self.players)]

        # Ask next player for reservation if he hasn't been asked yet
        if self.current_player != self.players[0]:
            self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                "type": "reservation",
                "target": self.current_player.hex
            })

        # After everyone was asked...
        else:
            # Ask the first player with reservation for a solo
            if len(self.players_with_reserv) > 0:
                self.current_player = self.players_with_reserv[0]
                self.reserv_state = "solo"
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "solo",
                    "target": self.current_player.hex
                })
            # Abort, if there aren't any reservations
            else:
                self.start_normal()

    def handle_reservation_solo(self, event: str, data: Dict):
        # Check for correct states
        if self.game_state is not "reservations":
            raise GameStateError(f"Game state for solo handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state is not "solo":
            raise GameStateError(f"Reservations state for solo handling must be 'solo', not {self.reserv_state}!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the solo handling packet is not the current player!")

        # Remember, if the player want's to play a valid solo
        if data["type"] == "solo_yes":
            solo_type = data["data"]["type"]
            if (  # Validate solo
                    solo_type in ["solo_queen", "solo_jack", "solo_clubs", "solo_spades", "solo_hearts",
                                  "solo_diamonds", "solo_fleshless"] or
                    self.game.gamerules["dk." + solo_type.replace("_", ".")] or
                    (
                            solo_type in ["solo_pure_clubs", "solo_pure_clubs", "solo_pure_clubs",
                                          "solo_pure_clubs"] and
                            self.game.gamerules["dk.solo.pure_color"]
                    )):
                self.players_with_solo[self.current_player] = solo_type
            else:
                raise RuleError(f"Solo of type {solo_type} is either disabled or does not exist!")

        # Announce decision
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": data["type"],
            "data": data["data"]
        })

        # Register move
        self.add_move(self.current_player, "announcement",
                      "solo_no" if data["type"] == "solo_no" else data["data"]["type"])

        # Go to the next player with reservation
        self.current_player = self.players_with_reserv[
            (self.players_with_reserv.index(self.current_player) + 1) % len(self.players_with_reserv)
            ]

        # Ask the next player for a solo if he hasn't been asked yet
        if self.current_player != self.players_with_reserv[0]:

            self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                "type": "solo",
                "target": self.current_player.hex
            })

        # After asking all players with reservations
        else:
            # If one ore more players want to play a solo, determine the higher solo and initialise it
            if len(self.players_with_solo) >= 1:
                solist = list(self.players_with_solo.keys())[0]
                for player, solo in self.players_with_solo.items():
                    if self.game.SOLO_ORDER.index(solo) < self.game.SOLO_ORDER.index(self.players_with_solo[solist]):
                        solist = player

                self.start_solo(solist)

            # If no one wants to play a solo
            else:
                self.current_player = self.players_with_reserv[0]

                # Ask for the next reservation that is enabled in the rules
                if self.game.gamerules["dk.throw"] == "reservation":
                    self.reserv_state = "throw"
                    self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "throw",
                        "target": self.current_player.hex
                    })
                elif self.game.gamerules["dk.pigs"] == "two_reservation":
                    self.reserv_state = "pigs"
                    self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "pigs",
                        "target": self.current_player.hex
                    })
                elif self.game.gamerules["dk.poverty"] != "None":
                    self.reserv_state = "poverty",
                    self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "poverty",
                        "target": self.current_player.hex
                    })
                elif self.game.gamerules["dk.wedding"] != "None":
                    self.reserv_state = "wedding",
                    self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "wedding",
                        "target": self.current_player.hex
                    })
                # Or abort, if there aren't any left
                else:
                    self.start_normal()

    def handle_reservation_throw(self, event: str, data: Dict):
        # Check for valid states
        if self.game_state != "reservations":
            raise GameStateError(f"Game state for throw handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state != "throw":
            raise GameStateError(f"Reservations state for throw handling must be 'throw', not {self.reserv_state}!")
        if self.game.gamerules["dk.throw"] != "reservation":
            raise RuleError("Throwing is not permitted by the rules!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the throw handling packet is not the current player!")

        # If the player want's to throw
        if data["type"] == "throw_yes":
            legal_throw = False

            # Check, whether throwing is justified
            nines = []
            kings = []
            fulls = []
            high_trumps = []
            dj = False

            player_hand = [self.cards[i] for i in self.hands[self.current_player]]
            for card in player_hand:
                if card.value == "9":
                    nines.append(card)
                elif card.value == "k":
                    kings.append(card)
                elif card.value in ["10", "a"]:
                    fulls.append(card)
                if card.card_value in ["h10", "cq", "sq", "hq", "dq", "cj", "sj", "hj"]:
                    high_trumps.append(card)
                if card.card_value == "dj":
                    dj = True

            if "5_9" in self.game.gamerules["dk.throw_cases"]:
                legal_throw = legal_throw or len(nines) >= 5
            if "5_k" in self.game.gamerules["dk.throw_cases"]:
                legal_throw = legal_throw or len(kings) >= 5
            if "4_9+4_k" in self.game.gamerules["dk.throw_cases"]:
                legal_throw = legal_throw or len(nines) >= 4 and len(kings) >= 4
            if "9_all_c" in self.game.gamerules["dk.throw_cases"]:
                legal_throw = legal_throw or len(set(list(map(lambda x: x.color, nines)))) == 4
            if "k_all_c" in self.game.gamerules["dk.throw_cases"]:
                legal_throw = legal_throw or len(set(list(map(lambda x: x.color, kings)))) == 4
            if "7full" in self.game.gamerules["dk.throw_cases"]:
                legal_throw = legal_throw or len(fulls) >= 7
            if "t<hj" in self.game.gamerules["dk.throw_cases"]:
                legal_throw = legal_throw or len(high_trumps) == 0
            if "t<dj" in self.game.gamerules["dk.throw_cases"]:
                legal_throw = legal_throw or len(high_trumps) == 0 and not dj

            if not legal_throw:
                raise InvalidMoveError(f"Throwing with the current hand is illegal!")

            # Announce the throwing
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

            # Register move
            self.add_move(self.current_player, "announcement", data["type"])

            # Exit the round
            self.exit_round(remake=True)

        # If he doesn't want to throw
        elif data["type"] == "throw_no":
            # Announce the decision
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

            # Register move
            self.add_move(self.current_player, "announcement", data["type"])

            # Go to next player with reservation
            self.current_player = self.players_with_reserv[
                (self.players_with_reserv.index(self.current_player) + 1) % len(self.players_with_reserv)]

            # Ask if he want's to throw as long as he hasn't been asked yet
            if self.current_player != self.players_with_reserv[0]:
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "throw",
                    "target": self.current_player.hex
                })

            # If nobody want's to throw
            else:
                # Ask for the next reservation that is enabled in the rules
                if self.game.gamerules["dk.pigs"] == "two_reservation":
                    self.reserv_state = "pigs"
                    self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "pigs",
                        "target": self.current_player.hex
                    })
                elif self.game.gamerules["dk.poverty"] != "None":
                    self.reserv_state = "poverty",
                    self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "poverty",
                        "target": self.current_player.hex
                    })
                elif self.game.gamerules["dk.wedding"] != "None":
                    self.reserv_state = "wedding",
                    self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "wedding",
                        "target": self.current_player.hex
                    })
                # Or abort if there aren't any left
                else:
                    self.start_normal()

    def handle_reservation_pigs(self, event: str, data: Dict):
        # Check for valid states
        if self.game_state != "reservations":
            raise GameStateError(f"Game state for pigs handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state != "pigs":
            raise GameStateError(f"Reservations state for pigs handling must be 'pigs', not {self.reserv_state}!")
        if self.game.gamerules["dk.pigs"] != "two_reservation":
            raise RuleError("Pigs are disabled by the rules!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the pigs handling packet is not the current player!")

        # Register pigs a players pigs if he has them
        if data["type"] == "pigs_yes":
            player_hand = [self.cards[i] for i in self.hands[self.current_player]]
            if list(map(lambda x: x.card_value, player_hand)).count("da") != 2:  # Not two diamond aces in the hand
                raise InvalidMoveError(
                    "Calling pigs is illegal for the player's hand does not contain two aces of diamonds!")
            else:
                self.pigs = (True, self.current_player)

        # Announce decision
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": data["type"]
        })

        # Register move
        self.add_move(self.current_player, "announcement", data["type"])

        # Go to next reservation
        self.current_player = self.players_with_reserv[
            (self.players_with_reserv.index(self.current_player) + 1) % len(self.players_with_reserv)
            ]

        # If no pigs have been called yet and the player hasn't been asked yet
        if not self.pigs[0] and self.current_player != self.players_with_reserv[0]:
            self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                "type": "pigs",
                "target": self.current_player.hex
            })

        # If everyone has been asked or someone called pigs
        else:
            # Reset to first reservation
            self.current_player = self.players_with_reserv[0]

            # Ask for superpigs
            if self.pigs[0] and self.game.gamerules["dk.superpigs"] == "reservation":
                self.current_player = self.players[0]
                self.reserv_state = "superpigs"
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "superpigs",
                    "target": self.current_player.hex
                })
            # Or for other reservations
            elif self.game.gamerules["dk.poverty"] != "None":
                self.reserv_state = "poverty",
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "poverty",
                    "target": self.current_player.hex
                })
            elif self.game.gamerules["dk.wedding"] != "None":
                self.reserv_state = "wedding",
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "wedding",
                    "target": self.current_player.hex
                })
            # Or abort, if no legal reservations are left
            else:
                self.start_normal()

    def handle_reservation_superpigs(self, event: str, data: Dict):
        # Check for valid states
        if self.game_state != "reservations":
            raise GameStateError(f"Game state for superpigs handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state != "superpigs":
            raise GameStateError(
                f"Reservations state for superpigs handling must be 'superpigs', not {self.reserv_state}!")
        if not self.pigs[0]:
            raise RuleError("Superpigs are illegal for no pigs have been called!")
        if self.game.gamerules["dk.superpigs"] != "reservation":
            raise RuleError("Superpigs are disabled by the rules!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the superpigs handling packet is not the current player!")

        # Register valid superpigs
        if data["type"] == "superpigs_yes":
            legal_spigs = False

            player_hand = [self.cards[i] for i in self.hands[self.current_player]]
            if self.game.gamerules["dk.without9"] == "with_all":
                legal_spigs = list(map(lambda x: x.card_value, player_hand)).count("d9") == 2
            elif self.game.gamerules["dk.without9"] in ["with_four", "without"]:
                legal_spigs = list(map(lambda x: x.card_value, player_hand)).count("dk") == 2

            if not legal_spigs:
                raise InvalidMoveError(
                    "Calling Superpigs is illegal for the player's current hand doesn't contain the required cards")
            else:
                self.superpigs = (True, self.current_player)

        # Announce decision
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": data["type"]
        })

        # Register move
        self.add_move(self.current_player, "announcement", data["type"])

        # Go to next player (since superpigs weren't reserved for pigs were unknown)
        self.current_player = self.players[(self.players.index(self.current_player) + 1) % len(self.players)]

        # If nobody called superpigs and the next player hasn't been asked yet
        if not self.superpigs[0] and self.current_player != self.players[0]:
            self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                "type": "superpigs",
                "target": self.current_player.hex
            })

        # If superpigs were called or everyone was asked
        else:
            self.current_player = self.players_with_reserv[0]

            # Ask for the next legal reservation
            if self.game.gamerules["dk.poverty"] != "None":
                self.reserv_state = "poverty",
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "poverty",
                    "target": self.current_player.hex
                })
            elif self.game.gamerules["dk.wedding"] != "None":
                self.reserv_state = "wedding",
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "wedding",
                    "target": self.current_player.hex
                })
            # Or abort if none are left
            else:
                self.start_normal()

    def handle_reservation_poverty(self, event: str, data: Dict):
        # Check for valid states
        if self.game_state != "reservations":
            raise GameStateError(f"Game state for poverty handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state != "poverty":
            raise GameStateError(f"Reservations state for poverty handling must be 'poverty', not {self.reserv_state}!")
        if self.game.gamerules["dk.poverty"] == "None":
            raise RuleError("Poverty is disabled by the rules!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the poverty handling packet is not the current player!")

        # If the player wants to play a poverty
        if data["type"] == "poverty_yes":
            # Check if his poverty is legal
            trumps = []
            player_hand = [self.cards[i] for i in self.hands[self.current_player]]
            for c in player_hand:
                if c.color == "d" or c.value in ["j", "q"] or c.card_value == "h10":
                    trumps.append(c)
            legal_poverty = len(trumps) <= 3

            if not legal_poverty:
                raise InvalidMoveError(
                    "Calling a poverty is illegal for the player's current hand does contain more than 3 trumps!")

            self.poverty_player = self.current_player

            # Announce decision
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

            # Register move
            self.add_move(self.current_player, "announcement", data["type"])

            # Set the state depending on poverty handling
            if self.game.gamerules["dk.poverty"] == "sell":
                self.reserv_state = "poverty_sell"
            elif self.game.gamerules["dk.poverty"] in ["circulate", "circulate_duty"]:
                self.reserv_state = "poverty_circulate"

            # Ask for the cards the poverty player want's to exchange
            self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                "type": "poverty_trump_choice",
                "target": self.current_player.hex
            })
            # --> handle_reservation_poverty_pass_card (type = "pass_card")

        # If the player doesn't want to play a poverty
        elif data["type"] == "poverty_no":
            # Announce the decision
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

            # Register move
            self.add_move(self.current_player, "announcement", data["type"])

            # Go to the next reservation
            self.current_player = self.players_with_reserv[
                (self.players_with_reserv.index(self.current_player) + 1) % len(self.players_with_reserv)
                ]

            # If the player hasn't been asked yet, ask for a poverty
            if self.current_player != self.players_with_reserv[0]:
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "poverty",
                    "target": self.current_player.hex
                })

            # If everybody has been asked
            else:
                # Ask for the next legal reservation
                if self.game.gamerules["dk.wedding"] != "None":
                    self.reserv_state = "wedding",
                    self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "wedding",
                        "target": self.current_player.hex
                    })
                else:
                    self.start_normal()

    def handle_reservation_poverty_pass_card(self, event: str, data: Dict):
        # Check for valid states
        if self.game_state != "reservations":
            raise GameStateError(
                f"Game state for poverty card passing handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state not in ["poverty_sell", "poverty_circulate", "poverty_return"]:
            raise GameStateError(
                f"Reservations state for poverty card passing handling must be 'poverty_sell',"
                f"'poverty_circulate' or 'poverty_return', not {self.reserv_state}!")
        if self.game.gamerules["dk.poverty"] == "None":
            raise RuleError("Poverty is disabled by the rules!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(
                f"The player that sent the poverty card passing handling packet is not the current player!")
        # This packet must contain 3 cards
        if type(data["card"]) != list:
            raise InvalidMoveError(
                f"For poverty card passing handling, card data must be of type 'list', not {type(data['card'])}")
        if len(data["card"]) != 3:
            raise InvalidMoveError(
                f"For poverty card passing handling, card data must contain 3 cards, not {len(data['card'])}")

        cards = [uuidify(i) for i in data["card"]]

        # Check if the card is valid
        player_hand = self.hands[self.current_player]
        for card in cards:
            if card not in player_hand:
                raise InvalidMoveError("The players hand must contain the chosen card!")

        # This packet must be received 3 times before continuing
        self.poverty_cards = cards

        # When the three cards have been chosen
        if len(self.poverty_cards) == 3:
            # If the poverty player passes the cards
            if data["type"] == "pass_card":
                # Check if he chose all his trumps
                player_hand = [self.cards[i] for i in self.hands[self.current_player]]
                for c in player_hand:
                    if (c.color == "d" or c.value in ["j",
                                                      "q"] or c.card_value == "h10") and c.card_id not in self.poverty_cards:
                        raise InvalidMoveError("Upon calling a poverty, the player must choose to pass all his trumps!")

                if self.current_player != self.poverty_player:
                    return

                # Transfer the chosen cards to the poverty slot
                for c in self.poverty_cards:
                    self.transfer_card(self.cards[c],
                                       f"hand{self.players.index(self.current_player)}",
                                       "poverty")

                self.current_player = self.players[(self.players.index(self.current_player) + 1) % len(self.players)]

                # If the poverty mode is circulate...
                # ...make them visible for the next player
                if self.reserv_state == "poverty_circulate":
                    for c in self.poverty_cards:
                        self.transfer_card(self.cards[c],
                                           "poverty",
                                           "poverty")

                # Ask the next player if he accepts the poverty
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "poverty_accept",
                    "target": self.current_player.hex
                })
                # --> handle_reservation_poverty_accept (type = "accept" or "decline")

            # If the poverty partner passes the cards
            elif data["type"] == "return_card":
                # Transfer the chosen cards to the poverty slot
                for c in self.poverty_cards:
                    self.transfer_card(self.cards[c],
                                       f"hand{self.players.index(self.current_player)}",
                                       "poverty")

                # Ask for the amount of trumps in the returned cards
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "poverty_return_trumps",
                    "target": self.current_player.hex
                })
                # --> handle_reservation_poverty_accept (type = "return")

    def handle_reservation_poverty_accept(self, event: str, data: Dict):
        # Check for valid states
        if self.game_state != "reservations":
            raise GameStateError(
                f"Game state for poverty accept handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state != ["poverty_sell", "poverty_circulate", "poverty_return"]:
            raise GameStateError(f"Reservations state for poverty accept handling must be 'poverty_sell',"
                                 f"'poverty_circulate' or 'poverty_return', not {self.game_state}!")
        if self.game.gamerules["dk.poverty"] == "None":
            raise RuleError("Poverty is disabled by the rules!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(
                f"The player that sent the poverty accept handling packet is not the current player!")

        # If the player accepts the poverty
        if data["type"] == "poverty_accept":
            # Announce the decision
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

            # Register move
            self.add_move(self.current_player, "announcement", data["type"])

            # Transfer the cards to the players hand
            for c in self.poverty_cards:
                self.transfer_card(self.cards[c],
                                   "poverty",
                                   f"hand{self.players.index(self.current_player)}")

            # Reset the poverty slot and update the state
            self.reserv_state = "poverty_return"
            self.poverty_cards.clear()

            # Request the cards the player wants to return
            self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                "type": "poverty_return_choice",
                "target": self.current_player.hex
            })
            # --> handle_reservation_poverty_pass_card (type = "return_card")

        # If the player returns the exchanged cards
        elif data["type"] == "poverty_return":
            # Check if the amount of trumps corresponds to the called amount
            trumps = []
            for c in self.poverty_cards:
                if self.cards[c].value in ["j", "q"] or self.cards[c].color == "d" or self.cards[c].card_value == "h10":
                    trumps.append(c)

            if len(trumps) != data["data"]["amount"]:
                raise InvalidMoveError(
                    f"The amount of returned trumps({len(trumps)} does not correspond with the called"
                    f"amount ({data['data']['amount']}))!")

            # Announce the amount of trumps
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"],
                "data": data["data"]
            })

            # Register move
            self.add_move(self.current_player, "announcement", "poverty_return_" + data["data"]["amount"])

            self.current_player = self.poverty_player

            # Transfer the chosen card to the poverty player
            for c in self.poverty_cards:
                self.transfer_card(self.cards[c],
                                   "poverty",
                                   "poverty")
            for c in self.poverty_cards:
                self.transfer_card(self.cards[c],
                                   "poverty",
                                   f"hand{self.players.index(self.current_player)}")

            # Start the poverty
            accepter = uuidify(data["player"])
            self.start_poverty(accepter)

        # If the player declines the poverty
        elif data["type"] == "poverty_decline":
            # Announce decision
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

            # Register move
            self.add_move(self.current_player, "announcement", data["type"])

            # Go to next player
            self.current_player = self.players[(self.players.index(self.current_player) + 1) % len(self.players)]

            # If poverty mode is circulate
            if self.reserv_state == "poverty_circulate":
                # Show him the poverty cards
                for c in self.poverty_cards:
                    self.transfer_card(self.cards[c],
                                       "poverty",
                                       "poverty")

                # If it is the last players turn and he has to accept the poverty by rules
                if self.game.gamerules["dk.poverty"] == "circulate_duty" and self.players[
                    (self.players.index(self.current_player) + 1) % len(self.players)] == self.poverty_player:
                    self.game.cg.send_event("cg:game.dk.reservation_poverty_accept", {
                        "player": self.current_player.hex,
                        "type": "poverty_accept"
                    })
                    return
                    # --> handle_reservation_poverty_accept (type = "accept")

            # Ask the player if he want's to accept the poverty if the player hasn't been asked yet
            if self.current_player != self.poverty_player:
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "poverty_accept",
                    "target": self.current_player.hex
                })
                # --> handle_reservation_poverty_accept (type = "accept" or "decline")

            # If everybody has been asked
            else:
                # Return the poverty cards to the player
                for c in self.poverty_cards:
                    self.transfer_card(self.cards[c],
                                       "poverty",
                                       f"hand{self.players.index(self.current_player)}")
                self.poverty_cards.clear()

                # Handle the poverty_consequences rule
                # Continue as if nothing happened
                if self.game.gamerules["dk.poverty_consequences"] == "None":
                    # Go to the next reservation
                    self.current_player = self.players_with_reserv[
                        (self.players_with_reserv.index(self.current_player) + 1) % len(self.players_with_reserv)
                        ]

                    # If the player hasn't been asked yet, ask for a reservation
                    if self.current_player != self.players_with_reserv[0]:
                        self.reserv_state = "poverty"
                        self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                            "type": "poverty",
                            "target": self.current_player.hex
                        })
                        # --> handle_reservation_poverty (type = "yes", "no")

                    # If everybody has been asked
                    else:
                        # Ask for the next legal reservation
                        if self.game.gamerules["dk.wedding"] != "None":
                            self.reserv_state = "wedding",
                            self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                                "type": "wedding",
                                "target": self.current_player.hex
                            })
                        else:
                            self.start_normal()

                # Redeal the game
                elif self.game.gamerules["dk.poverty_consequences"] == "redeal":
                    # Exit the round
                    self.exit_round(remake=True)

                # Play a round of black sow
                elif self.game.gamerules["dk.poverty_consequences"] == "black_sow":
                    self.start_black_sow()

                # Play a round of ramsch
                elif self.game.gamerules["dk.poverty_consequences"] == "ramsch":
                    self.start_ramsch()

    def handle_reservation_wedding(self, event: str, data: Dict):
        # Check for valid states
        if self.game_state != "reservations":
            raise GameStateError(f"Game state for wedding handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state != "wedding":
            raise GameStateError(f"Reservation state for wedding handling must be 'wedding', not {self.game_state}!")
        if self.game.gamerules["dk.wedding"] == "None":
            raise RuleError("Wedding is disabled by the rules!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the wedding handling packet is not the current player!")

        # If the player want's to play a wedding
        if data["type"] == "wedding_yes":
            # Check if the wedding is legal
            player_hand = [self.cards[i] for i in self.hands[self.current_player]]
            if not list(map(lambda x: x.card_value, player_hand)).count("cq") == 2:  # Hand contains two queens of clubs
                raise InvalidMoveError(f"Calling a wedding is illegal for the player's current hand does not contain "
                                       f"two queens of clubs")

            # Announce decision
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

            # Register move
            self.add_move(self.current_player, "announcement", data["type"])

            # Continue depending on gamerules
            if self.game.gamerules["dk.wedding"] == "3_trick":
                self.start_wedding(self.current_player)

            # Ask for clarification trick wish
            elif self.game.gamerules["dk.wedding"] == "wish_trick":
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "wedding_clarification_trick",
                    "target": self.current_player.hex
                })
                # --> handle_reservation_wedding_clarification_trick

        # Otherwise
        elif data["type"] == "wedding_no":
            # Announce decision
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

            # Register move
            self.add_move(self.current_player, "announcement", data["type"])

            # Go to the next reservation
            self.current_player = self.players_with_reserv[
                (self.players_with_reserv.index(self.current_player) + 1) % len(self.players_with_reserv)
                ]

            # If the player hasn't been asked yet, ask for a wedding
            if self.current_player != self.players_with_reserv[0]:
                self.game.cg.server.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "wedding",
                    "target": self.current_player.hex
                })

            # If everybody has been asked
            else:
                self.start_normal()

    def handle_reservation_wedding_clarification_trick(self, event: str, data: Dict):
        # Check for valid states
        if self.game_state != "reservations":
            raise GameStateError(f"Game state for wedding clarification trick handling must be 'reservations', not"
                                 f"{self.game_state}!")
        if self.reserv_state != "wedding":
            raise GameStateError(f"Reservations state for wedding clarification trick handling must be 'wedding', not"
                                 f"{self.game_state}!")
        if self.game.gamerules["dk.wedding"] != "wish_trick":
            raise RuleError("Wedding is disabled by the rules!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the wedding clarification trick handling packet is not the"
                                   f"current player!")

        # Announce decision
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": data["type"],
            "data": data["data"]
        })

        # Register move
        self.add_move(self.current_player, "announcement", "wedding_clarification_trick_" + data["data"]["trick"])

        self.start_wedding(self.current_player, data["data"]["trick"])

    def handle_play_card(self, event: str, data: Dict):
        # Check for valid states
        if self.game_state != "tricks":
            raise GameStateError(
                f"Game state for poverty accept handling must be 'reservations', not {self.game_state}!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the card play handling packet is not the current player!")
        if len(self.current_trick) > 4:
            raise InvalidMoveError(f"The trick may only contain a maximum of 4 cards, not {len(self.current_trick)}!")

        # Check if card is in the players hand
        card = uuidify(data["card"])
        if card not in self.hands[self.current_player]:
            raise InvalidMoveError(f"The played card is not available in the current player's hand")

        # Check if the card may be played considering the cards that were already played
        legal_move = False
        # Yes, if it is the first card of the trick
        if len(self.current_trick) == 0:
            legal_move = True
        # Yes, if it is the same color as the first card of the trick
        elif self.get_card_color(self.cards[card]) == self.get_card_color(self.cards[self.current_trick[0][1]]):
            legal_move = True
        # Yes, if the player has no card of the required color left
        elif list(map(lambda x: self.get_card_color(self.cards[x]), self.hands[self.current_player])).count(
                self.get_card_color(self.cards[self.current_trick[0][1]])) == 0:
            legal_move = True

        if not legal_move:
            raise InvalidMoveError("This card may not be played in the context of the trick!")

        # Actually play the card
        self.current_trick.append((self.current_player, card))

        self.transfer_card(self.cards[card],
                           f"hand{self.players.index(self.current_player)}",
                           "table")

        self.add_move(self.current_player, "card", self.cards[card].card_value)

        # Go to next player
        self.current_player = self.players[(self.players.index(self.current_player) + 1) % len(self.players)]

        # Signalise him to play the next card, if the trick is not full
        if len(self.current_trick) < 4:
            self.game.send_to_all("cg:game.dk.turn", {
                "current_trick": self.trick_num,
                "total_tricks": len(self.cards) / 4,
                "current_player": self.current_player.hex
            })

        # Determine the winner of the trick
        elif len(self.current_trick) == 4:
            trick_winner = self.get_trick_winner()
            gain = sum(map(lambda x: self.get_eyes(self.cards[x[1]]), self.current_trick))
            self.player_eyes[trick_winner] += gain

            # Transfer the trick to the winners trick stack
            for i in self.current_trick:
                self.transfer_card(self.cards[i[1]],
                                   "table",
                                   f"tricks{self.players.index(trick_winner)}")

            # Inform the players on the new scores
            self.game.send_to_all("cg:game.dk.scoreboard", {
                "player": self.current_player,
                "pips": self.player_eyes[self.current_player],
                "pip_change": gain
            })

            # Deinitialise the trick
            self.current_player = trick_winner
            self.current_trick.clear()

            self.pig_call = False
            self.superpig_call = False
            # TODO Implement calling pigs and superpigs

            self.trick_num += 1
            # TODO Implement ending the round

            self.game.send_to_all("cg:game.dk.turn", {
                "current_trick": self.trick_num,
                "total_tricks": len(self.cards) / 4,
                "current_player": self.current_player.hex
            })

    def handle_call_pigs(self, event: str, data: Dict):
        # Check for valid states
        if self.game_state != "tricks":
            raise GameStateError(
                f"Game state for pigs call handling must be 'reservations', not {self.game_state}!")
        if self.game.gamerules["dk.pigs"] in ["None", "two_reservation"]:
            raise RuleError(f"Pigs are either disabled or already had to be called!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the card play handling packet is not the current player!")

        if self.pigs[1] == uuidify(data["player"]):
            if self.game.gamerules["dk.pigs"] == "one_on_call":
                self.pig_call = True

    def handle_call_superpigs(self, event: str, data: Dict):
        pass
