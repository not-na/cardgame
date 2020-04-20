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

        self.players_with_reserv: List[uuid.UUID] = []
        self.players_with_solo: Dict[uuid.UUID, str] = {}
        self.poverty_player: Optional[uuid.UUID] = None

        self.parties: Dict[str, List[uuid.UUID]] = {
            "re": [],
            "kontra": [],
            "none": []
        }

        self.game_state: str = ""
        self.reserv_state: str = ""

        self.game_type: str = "normal"

        self.pigs: Tuple[bool, Optional[uuid.UUID]] = (False, None)
        self.superpigs: Tuple[bool, Optional[uuid.UUID]] = (False, None)

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
        self.poverty_cards: List[uuid.UUID] = []

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
        pass

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
                raise ValueError(f"Cannot transfer card from {from_slot} to {to_slot}")

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

        self.slots[from_slot].remove(card.card_id)
        self.slots[to_slot].append(card.card_id)

    def register_event_handlers(self):
        self.game.cg.add_event_listener("cg:game.dk.reservation", self.handle_reservation)
        self.game.cg.add_event_listener("cg:game.dk.reservation_solo", self.handle_reservation_solo)
        self.game.cg.add_event_listener("cg:game.dk.reservation_throw", self.handle_reservation_throw)
        self.game.cg.add_event_listener("cg:game.dk.reservation_pigs", self.handle_reservation_pigs)
        self.game.cg.add_event_listener("cg:game.dk.reservation_superpigs", self.handle_reservation_superpigs)
        self.game.cg.add_event_listener("cg:game.dk.reservation_poverty", self.handle_reservation_poverty)
        self.game.cg.add_event_listener("cg:game.dk.reservation_poverty_pass_card", self.handle_reservation_poverty_pass_card)
        self.game.cg.add_event_listener("cg:game.dk.reservation_poverty_accept", self.handle_reservation_poverty_accept)
        self.game.cg.add_event_listener("cg:game.dk.reservation_wedding", self.handle_reservation_wedding)
        self.game.cg.add_event_listener("cg:game.dk.reservation_wedding_clarification_trick", self.handle_reservation_wedding_clarification_trick)

    def handle_reservation(self, event: str, data: Dict):
        # Check for correct states
        if self.game_state is not "reservations":
            return
        if self.reserv_state is not "reservation":
            return
        if uuidify(data["player"]) != self.current_player:
            return

        # Remember players with reservation
        if data["type"] == "reservation_yes":
            self.players_with_reserv.append(self.current_player)

        # Announce decision
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": data["type"]
        })

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
            return
        if self.reserv_state is not "solo":
            return
        if uuidify(data["player"]) != self.current_player:
            return

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
                return

        # Announce decision
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": data["type"],
            "data": data["data"]
        })

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
            return
        if self.reserv_state != "throw":
            return
        if self.game.gamerules["dk.throw"] != "reservation":
            return
        if uuidify(data["player"]) != self.current_player:
            return

        # If the player want's to throw
        if data["type"] == "throw_yes":
            legal_throw = False

            # Check, whether throwing is justified
            nines = []
            kings = []
            fulls = []
            high_trumps = []
            dj = False

            player_hand = [self.cards[i] for i in self.slots[f"hand{self.players.index(self.current_player)}"]]
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
                return

            # Announce the throwing
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

            # Exit the round
            self.exit_round(remake=True)

        # If he doesn't want to throw
        elif data["type"] == "throw_no":
            # Announce the decision
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

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
            return
        if self.reserv_state != "pigs":
            return
        if self.game.gamerules["dk.pigs"] != "two_reservation":
            return
        if uuidify(data["player"]) != self.current_player:
            return

        # Register pigs a players pigs if he has them
        if data["type"] == "pigs_yes":
            player_hand = [self.cards[i] for i in self.slots[f"hand{self.players.index(self.current_player)}"]]
            if list(map(lambda x: x.card_value, player_hand)).count("da") != 2:  # Not two diamond aces in the hand
                return
            else:
                self.pigs = (True, self.current_player)

        # Announce decision
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": data["type"]
        })

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
            return
        if self.reserv_state != "superpigs":
            return
        if not self.pigs[0]:
            return
        if self.game.gamerules["dk.superpigs"] != "reservation":
            return
        if uuidify(data["player"]) != self.current_player:
            return

        # Register valid superpigs
        if data["type"] == "pigs_yes":
            legal_spigs = False

            player_hand = [self.cards[i] for i in self.slots[f"hand{self.players.index(self.current_player)}"]]
            if self.game.gamerules["dk.without9"] == "with_all":
                legal_spigs = list(map(lambda x: x.card_value, player_hand)).count("d9") == 2
            elif self.game.gamerules["dk.without9"] in ["with_four", "without"]:
                legal_spigs = list(map(lambda x: x.card_value, player_hand)).count("dk") == 2

            if not legal_spigs:
                return
            else:
                self.superpigs = (True, self.current_player)

        # Announce decision
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": data["type"]
        })

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
            return
        if self.reserv_state != "poverty":
            return
        if self.game.gamerules["dk.poverty"] == "None":
            return
        if uuidify(data["player"]) != self.current_player:
            return

        # If the player wants to play a poverty
        if data["type"] == "poverty_yes":
            # Check if his poverty is legal
            trumps = []
            player_hand = [self.cards[i] for i in self.slots[f"hand{self.players.index(self.current_player)}"]]
            for c in player_hand:
                if c.color == "d" or c.value in ["j", "q"] or c.card_value == "h10":
                    trumps.append(c)
            legal_poverty = len(trumps) <= 3

            if not legal_poverty:
                return

            self.poverty_player = self.current_player

            # Announce decision
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

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
            return
        if self.reserv_state not in ["poverty_sell", "poverty_circulate", "poverty_return"]:
            return
        if self.game.gamerules["dk.poverty"] == "None":
            return
        if uuidify(data["player"]) != self.current_player:
            return
        # This packet must contain 3 cards
        if type(data["card"]) != list:
            return
        if len(data["card"]) != 3:
            return

        cards = [uuidify(i) for i in data["card"]]

        # Check if the card is valid
        player_hand = self.slots[f"hand{self.players.index(self.current_player)}"]
        for card in cards:
            if card not in player_hand:
                return

        # This packet must be received 3 times before continuing
        self.poverty_cards = cards

        # When the three cards have been chosen
        if len(self.poverty_cards) == 3:
            # If the poverty player passes the cards
            if data["type"] == "pass_card":
                # Check if he chose all his trumps
                player_hand = [self.cards[i] for i in self.slots[f"hand{self.players.index(self.current_player)}"]]
                for c in player_hand:
                    if (c.color == "d" or c.value in ["j",
                                                      "q"] or c.card_value == "h10") and c.card_id not in self.poverty_cards:
                        return  # TODO Handle wrong cards passed

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
            return
        if self.reserv_state != ["poverty_sell", "poverty_circulate", "poverty_return"]:
            return
        if self.game.gamerules["dk.poverty"] == "None":
            return
        if uuidify(data["player"]) != self.current_player:
            return

        # If the player accepts the poverty
        if data["type"] == "poverty_accept":
            # Announce the decision
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

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
                return

            # Announce the amount of trumps
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"],
                "data": data["data"]
            })

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
            return
        if self.reserv_state != "wedding":
            return
        if self.game.gamerules["dk.wedding"] == "None":
            return
        if uuidify(data["player"]) != self.current_player:
            return

        # If the player want's to play a wedding
        if data["type"] == "wedding_yes":
            # Check if the wedding is legal
            player_hand = [self.cards[i] for i in self.slots[f"hand{self.players.index(self.current_player)}"]]
            if not list(map(lambda x: x.card_value, player_hand)).count("cq") == 2:  # Hand contains two queens of clubs
                return

            # Announce decision
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

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
            return
        if self.reserv_state != "wedding":
            return
        if self.game.gamerules["dk.wedding"] != "wish_trick":
            return
        if uuidify(data["player"]) != self.current_player:
            return

        # Announce decision
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": data["type"],
            "data": data["data"]
        })

        self.start_wedding(self.current_player, data["data"]["trick"])
