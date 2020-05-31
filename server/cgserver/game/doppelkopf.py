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
import time
from itertools import chain
from typing import List, Optional, Dict, Tuple, Union, Set

from cg.error import CardTransferError, GameStateError, WrongPlayerError, InvalidMoveError, RuleError
from cg.util import uuidify
from . import CGame
from .card import *

import cg
import uuid

from cg.constants import STATE_GAME_DK


class DoppelkopfGame(CGame):
    GAMERULES = {
        # "general.wrongmove": {
        #     "type": "select",
        #     "default": "prohibit",
        #     "options": [
        #         "prohibit",
        #         "allow_points",
        #         "allow_stopgame",
        #     ],
        #     "requirements": {},
        # },
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
                "on_pig",  # dk.pigs: two_on_play
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
                "redeal",
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
            ],
            "requirements": {},
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
            "default": "3_trick",
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
            "type": "select",
            "default": "4",
            "options": [
                "1",
                "2",
                "3",
                "4"
            ],
            "requirements": {
                "dk.buck_round": ["succession", "parallel"],
            },
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
            "default": False,
            "requirements": {},
        },
        "dk.solo_prio": {
            "type": "select",
            "default": "first",
            "options": [
                "first",
                "prio"
            ],
            "requirements": {},
        },
        "dk.solos": {
            "type": "active",
            "default": [
                "solo_queen",
                "solo_jack",
                "solo_clubs",
                "solo_spades",
                "solo_hearts",
                "solo_diamonds",
                "solo_fleshless",
            ],
            "options": [
                "solo_queen",
                "solo_jack",
                "solo_clubs",
                "solo_spades",
                "solo_hearts",
                "solo_diamonds",
                "solo_fleshless",
                "solo_aces",
                "solo_10s",
                "solo_king",
                "solo_9s",
                "solo_picture",
                "solo_noble_brothel",
                "solo_monastery",
                "solo_brothel",
                "solo_pure_clubs",
                "solo_pure_spades",
                "solo_pure_hearts",
                "solo_pure_diamonds",
                "solo_null",
                "solo_boneless",
            ],
            "requirements": {}
        },
        "dk.open_cards": {
            "type": "bool",
            "default": False,
            "requirements": {}
        }
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

        self.fake_players: List[uuid.UUID] = []

        if self.DEV_MODE:
            while len(self.players) < 4:
                pid = uuid.uuid4()
                self.players.append(pid)
                self.fake_players.append(pid)

        self.player_decisions: Dict[str, Set[uuid.UUID]] = {
            "continue": set(),
            "adjourn": set(),
            "cancel": set(),
            "end": set()
        }

        self.rounds: List[DoppelkopfRound] = []
        self.round_num: int = 0
        self.current_round: Optional[DoppelkopfRound] = None

        self.game_summaries = []

        self.points: Dict[uuid.UUID, int] = {}
        self.scores: List[List[int]] = []

        self.buckrounds: List[int] = []

    def start(self):
        for p in self.players:
            self.points[p] = 0

        self.send_to_all("cg:game.start", {
            "game_type": "doppelkopf",
            "game_id": self.game_id.hex,
            "player_list": [p.hex for p in self.players]
        })

        self.start_round(0)

    def start_round(self, round_num: int):
        players = self.players[round_num % 4:] + self.players[:round_num % 4]  # Each round, another player begins

        self.current_round = DoppelkopfRound(self, players)
        self.rounds.append(self.current_round)

        self.send_to_all("cg:game.dk.round.change", {
            "round": round_num,
            "phase": "loading",
            "player_list": [p.hex for p in players]
        })

        self.current_round.start()

    def send_to_all(self, packet: str, data: dict, exclude: Optional[List[uuid.UUID]] = None):
        if exclude is None:
            exclude = []

        for u in self.players:
            if u not in exclude:
                self.send_to_user(u, packet, data)

    def send_to_user(self, user: uuid.UUID, packet: str, data: dict):
        if user not in self.fake_players:
            self.cg.server.send_to_user(user, packet, data)

        if user in self.fake_players:
            user = "fake_player_" + str(self.fake_players.index(user))
        if packet != "cg:game.dk.card.transfer":
            self.cg.info(f"sent packet {packet} with content {data} to user {user}")

    def collect_statistics(self):
        data = {
            "game_id": self.game_id,
            "game_data": {
                "cretion_time": self.creation_time,
                "rounds": {},
                "botgame": len(self.fake_players) == 0
            },
            "players": []
        }
        for r in self.rounds:
            data["game_data"]["rounds"][r.round_id.hex] = {
                "moves": [
                    (
                        self.players.index(v["player"]),
                        f"{v['type']}:{v['data']}"
                    ) for v in r.moves.values()
                ]
            }
        for p in self.players:
            if p not in self.fake_players:
                data["players"].append(p.hex)

        self.cg.send_event("cg:stats.game.new", data)

    def register_event_handlers(self):
        super().register_event_handlers()

        self.cg.add_event_listener("cg:game.dk.end_round", self.handle_end_round, group=self.game_id)

        self.cg.add_event_listener("cg:game.dk.play.continue_yes", self.handle_continue_play, group=self.game_id)
        self.cg.add_event_listener("cg:game.dk.play.continue_no", self.handle_not_continue_play, group=self.game_id)
        self.cg.add_event_listener("cg:game.dk.play.cancel_yes", self.handle_cancel_play, group=self.game_id)
        self.cg.add_event_listener("cg:game.dk.play.cancel_no", self.handle_not_cancel_play, group=self.game_id)
        self.cg.add_event_listener("cg:game.dk.play.end_yes", self.handle_end_play, group=self.game_id)
        self.cg.add_event_listener("cg:game.dk.play.end_no", self.handle_not_end_play, group=self.game_id)

    def handle_end_round(self, event: str, data: Dict):
        # Send the information on the round
        self.send_to_all("cg:game.dk.round.change", {
            "phase": "end",
            "game_type": data["game_type"],
            "winner": data["winner"],
            "eyes": data["eyes"],
            "modifiers": data["modifiers"],
            "extras": data["extras"],
            "round": self.round_num,
            "game_summary": data["game_summary"]
        })

        self.game_summaries.append(data["game_summary"])

        m = -1 if data["game_type"] in ["ramsch", "ramsch_sw"] else 1  # In case of Ramsch, the points are swapped

        # Determine if the round should be played again
        remake_round = data["game_type"] in ["throw", "poverty_cancel"]  # The round was cancelled due to reservations
        remake_round = remake_round or (  # The winner got 0 or less points (depending on the rules)
                self.gamerules["dk.repeat_game"] and
                ((data["winner"] == "kontra" and data["game_value"] >= 0) or
                 (data["winner"] == "re" and data["game_value"] <= 0)))

        self.scores.append([])
        if not remake_round:
            # Handle buckround modifier for points
            if self.gamerules["dk.buck_round"] == "succession":
                if len(self.buckrounds) == 1:
                    m *= 2
                    self.buckrounds[0] -= 1
                    if self.buckrounds == [0]:
                        self.buckrounds = []
            elif self.gamerules["dk.buck_round"] == "parallel":
                for i in range(len(self.buckrounds)):
                    m *= 2
                    self.buckrounds[i] -= 1
                while 0 in self.buckrounds:
                    self.buckrounds.remove(0)

            for p in self.players:
                if p in data["re"]:
                    if len(data["re"]) == 1:  # Solo
                        self.points[p] += 3 * m * data["game_value"]
                        self.scores[-1].append(3 * m * data["game_value"])
                        self.send_to_all("cg:game.dk.scoreboard", {
                            "player": p.hex,
                            "points": self.points[p],
                            "point_change": 3 * m * data["game_value"]
                        })
                    else:
                        self.points[p] += m * data["game_value"]
                        self.scores[-1].append(m * data["game_value"])
                        self.send_to_all("cg:game.dk.scoreboard", {
                            "player": p.hex,
                            "points": self.points[p],
                            "point_change": m * data["game_value"]
                        })
                elif p in data["kontra"]:
                    self.points[p] -= m * data["game_value"]
                    self.scores[-1].append(-m * data["game_value"])
                    self.send_to_all("cg:game.dk.scoreboard", {
                        "player": p.hex,
                        "points": self.points[p],
                        "point_change": -m * data["game_value"]
                    })

            # Add new buckround events
            if self.gamerules["dk.buck_round"] == "succession":
                if data["buckround_events"] != 0:
                    if len(self.buckrounds) == 1:
                        self.buckrounds[0] += data["buckround_events"] * int(self.gamerules["dk.buck_amount"])
                    else:
                        self.buckrounds.append(data["buckround_events"] * int(self.gamerules["dk.buck_amount"]))
            elif self.gamerules["dk.buck_round"] == "parallel":
                self.buckrounds.extend(data["buckround_events"] * [int(self.gamerules["dk.buck_amount"])])

            self.round_num += 1  # Only increase round_num if the game wasn't cancelled

        self.cg.event_manager.del_group(self.current_round.round_id)  # Deinitialise the round's event handlers

    def handle_continue_play(self, event: str, data: Dict):
        self.player_decisions["continue"].add(data["player"])
        if self.DEV_MODE:
            for p in self.fake_players:
                self.player_decisions["continue"].add(p)
        self.send_to_all("cg:game.dk.announce", {
            "announcer": data["player"],
            "type": "continue_yes"
        })
        if len(self.player_decisions["continue"]) == 4:
            self.player_decisions: Dict[str, Set[uuid.UUID]] = {
                "continue": set(),
                "adjourn": set(),
                "cancel": set(),
                "end": set()
            }
            self.start_round(self.round_num)

    def handle_not_continue_play(self, event: str, data: Dict):
        self.player_decisions["continue"].discard(data["player"])
        self.send_to_all("cg:game.dk.announce", {
            "announcer": data["player"],
            "type": "continue_no"
        })

    def handle_cancel_play(self, event: str, data: Dict):
        self.player_decisions["cancel"].add(data["player"])
        if self.DEV_MODE:
            for p in self.fake_players:
                self.player_decisions["cancel"].add(p)
        self.send_to_all("cg:game.dk.announce", {
            "announcer": data["player"],
            "type": "cancel_yes"
        })
        if len(self.player_decisions["cancel"]) == 4:
            self.player_decisions: Dict[str, Set[uuid.UUID]] = {
                "continue": set(),
                "adjourn": set(),
                "cancel": set(),
                "end": set()
            }
            self.cancel_game()

    def handle_not_cancel_play(self, event: str, data: Dict):
        self.player_decisions["cancel"].discard(data["player"])
        self.send_to_all("cg:game.dk.announce", {
            "announcer": data["player"],
            "type": "cancel_no"
        })

    def handle_end_play(self, event: str, data: Dict):
        self.player_decisions["end"].add(data["player"])
        if self.DEV_MODE:
            for p in self.fake_players:
                self.player_decisions["end"].add(p)
        self.send_to_all("cg:game.dk.announce", {
            "announcer": data["player"],
            "type": "end_yes"
        })
        if len(self.player_decisions["end"]) == 4:
            self.player_decisions: Dict[str, Set[uuid.UUID]] = {
                "continue": set(),
                "adjourn": set(),
                "cancel": set(),
                "end": set()
            }
            self.collect_statistics()
            self.cancel_game()

    def handle_not_end_play(self, event: str, data: Dict):
        self.player_decisions["end"].discard(data["player"])
        self.send_to_all("cg:game.dk.announce", {
            "announcer": data["player"],
            "type": "end_no"
        })

    def serialize(self):
        return {
            "id": self.game_id.hex,
            "type": "dk",
            "creation_time": self.creation_time,
            "players": [i.hex for i in self.players],
            "gamerules": self.gamerules,
            "round_num": self.round_num,
            "buckrounds": self.buckrounds,
            "scores": self.scores,
            "current_points": list(self.points.values())
        }

    @classmethod
    def deserialize(cls, cg, lobby, data):
        game = cls(cg, lobby)
        game.game_id = uuidify(data["id"])
        game.creation_time = data["creation_time"]
        game.players = [uuidify(p) for p in data["players"]]
        game.gamerules = data["gamerules"]
        game.round_num = data["round_num"]
        game.buckrounds = data["buckrounds"]
        game.scores = data["points"]
        for i, p in enumerate(game.players):
            game.points[p] = data["current_points"][i]

        return game

    @classmethod
    def check_playercount(cls, count: int, ignore_devmode=False):
        if ignore_devmode:
            return count == 4
        return cls.DEV_MODE or count == 4


class DoppelkopfRound(object):
    DEV_MODE_PREP_CARDS = False

    CARD_DEAL_DELAY = 1.0

    def __init__(self, game: DoppelkopfGame, players: List[uuid.UUID]):
        self.game: DoppelkopfGame = game
        self.round_id: uuid.UUID = uuid.uuid4()

        self.register_event_handlers()

        self.players: List[uuid.UUID] = players
        self.current_player: Optional[uuid.UUID] = None
        self.rdy_players: List[uuid.UUID] = []

        self.game_state: str = ""
        self.reserv_state: str = ""

        self.game_type: str = "normal"

        self.parties: Dict[str, Set[uuid.UUID]] = {
            "re": set(),
            "kontra": set(),
            "none": set()
        }
        self.obvious_parties: Dict[str, Set[uuid.UUID]] = {
            "re": set(),
            "kontra": set(),
            "unknown": set()
        }

        self.player_eyes: Dict[uuid.UUID, int] = dict((p, 0) for p in self.players)

        self.modifiers: Dict[str, List[str]] = {
            "re": [],
            "kontra": []
        }
        self.extra_points: Dict[uuid.UUID, List[str]] = dict((p, []) for p in self.players)
        self.buckround_events: int = 0

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

        self.pigs: List[bool, Optional[uuid.UUID]] = [False, None]
        self.superpigs: List[bool, Optional[uuid.UUID]] = [False, None]
        self.foxes: List[List[uuid.UUID]] = []

        self.spade_tricks: int = 0
        self.club_tricks: int = 0
        self.spade_queens: int = 0

        self.trick_num: int = 0
        self.current_trick: List[Tuple[uuid.UUID, uuid.UUID]] = []
        self.max_tricks: int = 12 if self.game.gamerules["dk.without9"] == "with_all" else \
            11 if self.game.gamerules["dk.without9"] == "with_four" else \
                10 if self.game.gamerules["dk.without9"] == "without" else 0

        self.wedding_clarification_trick: Optional[str] = None
        self.wedding_find_trick: int = 1

        self.start_hands: Dict[uuid.UUID, List[uuid.UUID]] = {}

        self.deal_counter = 0

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

    def update_obvious_party(self, player: uuid.UUID, party: str, scq: bool = False):
        # Remove the player from the unknown party
        self.obvious_parties["unknown"] -= {player}
        # Add him to the new party
        self.obvious_parties[party].add(player)

        # Check if this makes the party distribution clear
        if self.game_type in ["normal", "ramsch"]:
            if len(self.obvious_parties["re"]) == 2:
                for p in self.obvious_parties["unknown"].copy():
                    self.obvious_parties["unknown"] -= {p}
                    self.obvious_parties["kontra"].add(p)
            if len(self.obvious_parties["kontra"]) == 2:
                for p in self.obvious_parties["unknown"].copy():
                    self.obvious_parties["unknown"] -= {p}
                    self.obvious_parties["re"].add(p)

        if self.game_type in ["silent_wedding", "ramsch_sw"] and scq:
            if len(self.obvious_parties["re"]) == 1:
                for p in self.obvious_parties["unknown"].copy():
                    self.obvious_parties["unknown"] -= {p}
                    self.obvious_parties["kontra"].add(p)
            if len(self.obvious_parties["kontra"]) == 3:
                for p in self.obvious_parties["unknown"].copy():
                    self.obvious_parties["unknown"] -= {p}
                    self.obvious_parties["re"].add(p)

        # Handle weddings
        if self.game_type == "wedding":
            for p in self.obvious_parties["unknown"].copy():
                self.obvious_parties["unknown"] -= {p}
                self.obvious_parties["kontra"].add(p)

        # Handle foxes
        if self.game_type in ["normal", "ramsch", "poverty", "wedding"]:
            for fox in self.foxes.copy():
                if (fox[0] in self.obvious_parties["re"] and fox[1] in self.obvious_parties["kontra"]) or (
                        fox[0] in self.obvious_parties["kontra"] and fox[1] in self.obvious_parties["re"]):
                    self.extra_points[fox[1]].append("fox")
                    self.foxes.remove(fox)
                elif (fox[0] in self.obvious_parties["re"] and fox[1] in self.obvious_parties["re"]) or (
                        fox[0] in self.obvious_parties["kontra"] and fox[1] in self.obvious_parties["kontra"]):
                    self.foxes.remove(fox)

    def add_move(self, player: uuid.UUID, tp: str, data: str):
        self.moves[self.move_counter] = {
            "player": player,
            "type": tp,
            "data": data
        }
        self.move_counter += 1

    def transfer_card(self, card: Card, from_slot: Optional[str], to_slot: str):
        self.game.cg.info(f"Transfer card {card.card_value} from {from_slot} to {to_slot}")
        if from_slot is None:
            if to_slot == "stack":
                self.game.send_to_all("cg:game.dk.card.transfer", {
                    "card_id": card.card_id.hex,
                    "card_value": "" if not self.game.DEV_MODE else card.card_value,
                    "from_slot": from_slot,
                    "to_slot": to_slot,
                })
                self.slots[to_slot].append(card.card_id)
            else:
                raise CardTransferError(f"Cannot transfer card from {from_slot} to {to_slot}")

        elif from_slot == "stack":
            if "hand" in to_slot:
                receiver = self.players[int(to_slot.strip("hand"))]
                self.game.send_to_user(receiver, "cg:game.dk.card.transfer", {
                    "card_id": card.card_id.hex,
                    "card_value": card.card_value,
                    "from_slot": from_slot,
                    "to_slot": to_slot
                })
                self.game.send_to_all("cg:game.dk.card.transfer", {
                    "card_id": card.card_id.hex,
                    "card_value": "",
                    "from_slot": from_slot,
                    "to_slot": to_slot
                }, exclude=[receiver])
            else:
                raise CardTransferError(f"Cannot transfer card from {from_slot} to {to_slot}")

        elif "hand" in from_slot:
            if to_slot == "poverty":
                self.game.send_to_user(self.current_player, "cg:game.dk.card.transfer", {
                    "card_id": card.card_id.hex,
                    "card_value": card.card_value,
                    "from_slot": from_slot,
                    "to_slot": to_slot
                })
                self.game.send_to_all("cg:game.dk.card.transfer", {
                    "card_id": card.card_id.hex,
                    "card_value": "",
                    "from_slot": from_slot,
                    "to_slot": to_slot
                }, exclude=[self.current_player])

            elif to_slot == "table":
                self.game.send_to_all("cg:game.dk.card.transfer", {
                    "card_id": card.card_id.hex,
                    "card_value": card.card_value,
                    "from_slot": from_slot,
                    "to_slot": to_slot
                })
            else:
                raise CardTransferError(f"Cannot transfer card from {from_slot} to {to_slot}")

        elif from_slot == "poverty":
            if to_slot == "poverty":
                self.game.send_to_user(self.current_player, "cg:game.dk.card.transfer", {
                    "card_id": card.card_id.hex,
                    "card_value": card.card_value,
                    "from_slot": from_slot,
                    "to_slot": to_slot
                })
                self.game.send_to_all("cg:game.dk.card.transfer", {
                    "card_id": card.card_id.hex,
                    "card_value": "",
                    "from_slot": from_slot,
                    "to_slot": to_slot
                }, exclude=[self.current_player])

            elif "hand" in to_slot:
                self.game.send_to_user(self.current_player, "cg:game.dk.card.transfer", {
                    "card_id": card.card_id.hex,
                    "card_value": card.card_value,
                    "from_slot": from_slot,
                    "to_slot": to_slot
                })
                self.game.send_to_all("cg:game.dk.card.transfer", {
                    "card_id": card.card_id.hex,
                    "card_value": "",
                    "from_slot": from_slot,
                    "to_slot": to_slot
                }, exclude=[self.current_player])

            else:
                raise CardTransferError(f"Cannot transfer card from {from_slot} to {to_slot}")

        elif from_slot == "table":
            if "tricks" in to_slot:
                self.game.send_to_all("cg:game.dk.card.transfer", {
                    "card_id": card.card_id.hex,
                    "card_value": "",
                    "from_slot": from_slot,
                    "to_slot": to_slot
                })

            else:
                raise CardTransferError(f"Cannot transfer card from {from_slot} to {to_slot}")

        else:
            raise CardTransferError(f"Cannot transfer card from {from_slot} to {to_slot}")

        if from_slot is not None:
            self.slots[from_slot].remove(card.card_id)
        self.slots[to_slot].append(card.card_id)

    def get_card_color(self, card: Card) -> str:
        # Clubs
        if card.card_value == "c9":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_spades", "solo_jack", "solo_queen",
                                  "solo_brothel", "solo_king", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_spades", "solo_aces", "solo_10s"]:
                return "clubs"

        if card.card_value == "cj":
            if self.game_type in ["solo_queen", "solo_king", "solo_noble_brothel", "solo_fleshless", "solo_boneless",
                                  "solo_pure_diamonds", "solo_pure_hearts", "solo_pure_spades", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "clubs"

        if card.card_value == "cq":
            if self.game_type in ["solo_jack", "solo_king", "solo_monastery", "solo_fleshless", "solo_boneless",
                                  "solo_pure_diamonds", "solo_pure_hearts", "solo_pure_spades", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "clubs"

        if card.card_value == "ck":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_spades", "solo_jack", "solo_queen",
                                  "solo_brothel", "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_spades", "solo_aces", "solo_10s", "solo_9s"]:
                return "clubs"

        if card.card_value == "c10":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_jack", "solo_queen", "solo_brothel",
                                  "solo_king", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_spades", "solo_aces", "solo_9s"]:
                return "clubs"
            elif self.game_type == "solo_spades":
                if not self.game.gamerules["dk.solo_shift_h10"]:
                    return "clubs"

        if card.card_value == "ca":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_spades", "solo_jack", "solo_queen",
                                  "solo_brothel", "solo_king", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_spades", "solo_10s", "solo_9s"]:
                return "clubs"

        # Spades
        if card.card_value == "s9":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_clubs", "solo_jack", "solo_queen",
                                  "solo_brothel", "solo_king", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_clubs", "solo_aces", "solo_10s"]:
                return "spades"

        if card.card_value == "sj":
            if self.game_type in ["solo_queen", "solo_king", "solo_noble_brothel", "solo_fleshless", "solo_boneless",
                                  "solo_pure_diamonds", "solo_pure_hearts", "solo_pure_clubs", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "spades"

        if card.card_value == "sq":
            if self.game_type in ["solo_jack", "solo_king", "solo_monastery", "solo_fleshless", "solo_boneless",
                                  "solo_pure_diamonds", "solo_pure_hearts", "solo_pure_clubs", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "spades"

        if card.card_value == "sk":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_clubs", "solo_jack", "solo_queen",
                                  "solo_brothel", "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_clubs", "solo_aces", "solo_10s", "solo_9s"]:
                return "spades"

        if card.card_value == "s10":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_clubs", "solo_jack", "solo_queen", "solo_brothel",
                                  "solo_king", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_clubs", "solo_aces", "solo_9s"]:
                return "spades"
            elif self.game_type == "solo_hearts":
                if not self.game.gamerules["dk.solo_shift_h10"]:
                    return "spades"

        if card.card_value == "sa":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_clubs", "solo_jack", "solo_queen",
                                  "solo_brothel", "solo_king", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_hearts", "solo_pure_clubs", "solo_10s", "solo_9s"]:
                return "spades"

        # Hearts
        if card.card_value == "h9":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_spades", "solo_clubs", "solo_jack", "solo_queen",
                                  "solo_brothel", "solo_king", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s"]:
                return "hearts"

        if card.card_value == "hj":
            if self.game_type in ["solo_queen", "solo_king", "solo_noble_brothel", "solo_fleshless", "solo_boneless",
                                  "solo_pure_diamonds", "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "hearts"

        if card.card_value == "hq":
            if self.game_type in ["solo_jack", "solo_king", "solo_monastery", "solo_fleshless", "solo_boneless",
                                  "solo_pure_diamonds", "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "hearts"

        if card.card_value == "hk":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_spades", "solo_clubs", "solo_jack", "solo_queen",
                                  "solo_brothel", "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s", "solo_9s"]:
                return "hearts"

        if card.card_value == "h10":
            if self.game_type in ["solo_queen", "solo_brothel", "solo_king", "solo_monastery", "solo_noble_brothel",
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
                if not self.game.gamerules["dk.heart10"]:
                    return "hearts"

        if card.card_value == "ha":
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_spades", "solo_clubs", "solo_jack", "solo_queen",
                                  "solo_brothel", "solo_king", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_null", "solo_pure_diamonds",
                                  "solo_pure_spades", "solo_pure_clubs", "solo_10s", "solo_9s"]:
                return "hearts"

        # Diamonds
        if card.card_value == "d9":
            if self.game_type in ["solo_hearts", "solo_spades", "solo_clubs", "solo_jack", "solo_queen",
                                  "solo_brothel", "solo_king", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "", "solo_pure_hearts", "solo_pure_spades",
                                  "solo_pure_clubs", "solo_aces", "solo_10s"]:
                return "diamonds"

        if card.card_value == "dj":
            if self.game_type in ["solo_queen", "solo_king", "solo_noble_brothel", "solo_fleshless", "solo_boneless",
                                  "solo_pure_hearts", "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "diamonds"

        if card.card_value == "dq":
            if self.game_type in ["solo_jack", "solo_king", "solo_monastery", "solo_fleshless", "solo_boneless",
                                  "solo_pure_hearts", "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s",
                                  "solo_9s"]:
                return "diamonds"

        if card.card_value == "dk":
            if self.game_type in ["solo_hearts", "solo_spades", "solo_clubs", "solo_jack", "solo_queen",
                                  "solo_brothel", "solo_fleshless", "solo_boneless", "solo_pure_hearts",
                                  "solo_pure_spades", "solo_pure_clubs", "solo_aces", "solo_10s", "solo_9s"]:
                return "diamonds"

        if card.card_value == "d10":
            if self.game_type in ["solo_hearts", "solo_spades", "solo_jack", "solo_queen", "solo_brothel",
                                  "solo_king", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_pure_hearts", "solo_pure_spades",
                                  "solo_pure_clubs", "solo_aces", "solo_9s"]:
                return "diamonds"
            elif self.game_type == "solo_clubs":
                if not self.game.gamerules["dk.solo_shift_h10"]:
                    return "diamonds"

        if card.card_value == "da":
            if self.game_type in ["solo_hearts", "solo_spades", "solo_clubs", "solo_jack", "solo_queen",
                                  "solo_brothel", "solo_king", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_pure_hearts", "solo_pure_spades",
                                  "solo_pure_clubs", "solo_10s", "solo_9s"]:
                return "diamonds"

        return "trump"

    def get_trick_winner(self) -> Tuple[uuid.UUID, List[uuid.UUID]]:
        cards_sorted = sorted([i[1] for i in self.current_trick], key=self.get_card_sort_key, reverse=True)
        self.game.cg.info(f"Sorted Trick: {[self.cards[i].card_value for i in cards_sorted]}")
        self.game.cg.info(f"sort_keys: {[self.get_card_sort_key(i[1]) for i in self.current_trick]}")

        if self.cards[cards_sorted[0]].card_value == self.cards[cards_sorted[1]].card_value:
            if self.get_card_sort_key(self.cards[cards_sorted[0]]) == 100:  # Valid h10 (or s10, c10, d10 if solo)
                if self.trick_num == self.max_tricks:  # Last Trick
                    if self.game.gamerules["dk.heart10_lasttrick"] == "first":
                        for i in self.current_trick:  # Return first h10
                            if i[1] == cards_sorted[0]:
                                return i[0], cards_sorted
                    elif self.game.gamerules["dk.heart10_lasttrick"] == "second":
                        for i in self.current_trick:  # Return second h10
                            if i[1] == cards_sorted[1]:
                                return i[0], cards_sorted
                else:  # Not last Trick
                    if self.game.gamerules["dk.heart10_prio"] == "first":
                        for i in self.current_trick:  # Return first h10
                            if i[1] == cards_sorted[0]:
                                return i[0], cards_sorted
                    elif self.game.gamerules["dk.heart10_prio"] == "second":
                        for i in self.current_trick:  # Return second h10
                            if i[1] == cards_sorted[1]:
                                return i[0], cards_sorted

            if self.cards[cards_sorted[0]].card_value == "cj":  # Jack of clubs, Charlie
                if self.trick_num == self.max_tricks:  # Last Trick
                    if self.game.gamerules["dk.charlie_prio"] == "first":
                        for i in self.current_trick:  # Return first jack of clubs
                            if i[1] == cards_sorted[0]:
                                return i[0], cards_sorted
                    elif self.game.gamerules["dk.charlie_prio"] == "second":
                        for i in self.current_trick:  # Return second jack of clubs
                            if i[1] == cards_sorted[1]:
                                return i[0], cards_sorted

        # If the rules above don't apply, return the highest card
        for i in self.current_trick:
            if i[1] == cards_sorted[0]:
                return i[0], cards_sorted

    def get_card_sort_key(self, card: Union[Card, uuid.UUID]) -> int:
        first_card = self.cards[self.current_trick[0][1]]

        if isinstance(card, uuid.UUID):
            card = self.cards[card]

        if self.get_card_color(card) != "trump":
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

        elif self.get_card_color(card) == "trump":
            # 9, king, 10, ace of diamonds in normal version
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow",
                                  "ramsch", "solo_diamonds", "solo_null"]:
                if card.card_value == "d9" and not (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] == "with_all"):
                    return 10
                elif card.card_value == "dk" and not (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] != "with_all"):
                    return 11
                elif card.card_value == "d10":
                    return 12
                elif card.card_value == "da" and not self.pigs[0]:
                    return 13

                elif card.card_value == "h10" and self.game.gamerules["dk.heart10"]:
                    return 100
                elif card.card_value == "da" and self.pigs[0]:
                    return 200
                elif card.card_value == "d9" and (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] == "with_all"):
                    return 300
                elif card.card_value == "dk" and (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] != "with_all"):
                    return 300

            # 9, king, 10, ace of hearts in hearts solo
            elif self.game_type == "solo_hearts":
                if card.card_value == "h9" and not (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] == "with_all"):
                    return 10
                elif card.card_value == "hk" and not (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] != "with_all"):
                    return 11
                elif card.card_value == "h10" and not self.game.gamerules["dk.heart10"]:
                    return 12
                elif card.card_value == "ha" and not self.pigs[0]:
                    return 13

                elif card.card_value == "h10" and self.game.gamerules["dk.heart10"] and not self.game.gamerules[
                    "dk.solo_shift_h10"]:
                    return 100
                elif card.card_value == "s10" and self.game.gamerules["dk.solo_shift_h10"]:
                    return 100
                elif card.card_value == "ha" and self.pigs[0]:
                    return 200
                elif card.card_value == "h9" and (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] == "with_all"):
                    return 300
                elif card.card_value == "hk" and (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] != "with_all"):
                    return 300

            # 9, king, 10, ace of spades in spades solo
            elif self.game_type == "solo_spades":
                if card.card_value == "s9" and not (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] == "with_all"):
                    return 10
                elif card.card_value == "sk" and not (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] != "with_all"):
                    return 11
                elif card.card_value == "s10":
                    return 12
                elif card.card_value == "sa" and not self.pigs[0]:
                    return 13

                elif card.card_value == "h10" and self.game.gamerules["dk.heart10"] and not self.game.gamerules[
                    "dk.solo_shift_h10"]:
                    return 100
                elif card.card_value == "c10" and self.game.gamerules["dk.solo_shift_h10"]:
                    return 100
                elif card.card_value == "sa" and self.pigs[0]:
                    return 200
                elif card.card_value == "s0" and (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] == "with_all"):
                    return 300
                elif card.card_value == "sk" and (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] != "with_all"):
                    return 300

            # 9, king, 10, ace of clubs in clubs solo
            elif self.game_type == "solo_clubs":
                if card.card_value == "c9" and not (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] == "with_all"):
                    return 10
                elif card.card_value == "ck" and not (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] != "with_all"):
                    return 11
                elif card.card_value == "c10":
                    return 12
                elif card.card_value == "ca" and not self.pigs[0]:
                    return 13

                elif card.card_value == "h10" and self.game.gamerules["dk.heart10"] and not self.game.gamerules[
                    "dk.solo_shift_h10"]:
                    return 100
                elif card.card_value == "d10" and self.game.gamerules["dk.solo_shift_h10"]:
                    return 100
                elif card.card_value == "ca" and self.pigs[0]:
                    return 200
                elif card.card_value == "c9" and (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] == "with_all"):
                    return 300
                elif card.card_value == "ck" and (
                        self.superpigs[0] and self.game.gamerules["dk.without9"] != "with_all"):
                    return 300

            # Jacks in normal version and solos with jack trumps
            if self.game_type in ["normal", "wedding", "silent_wedding", "poverty", "black_sow", "ramsch",
                                  "solo_diamonds", "solo_hearts", "solo_spades", "solo_clubs", "solo_jack",
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
                                  "solo_diamonds", "solo_hearts", "solo_spades", "solo_clubs", "solo_queen",
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
            if self.game_type in ["solo_king", "solo_monastery", "solo_noble_brothel", "solo_picture"]:
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
            if card.card_value in ["j0", "j1", "j2"]:
                if self.game.gamerules["dk.joker"] == "over_h10":
                    return 150
                elif self.game.gamerules["dk.joker"] == "over_pigs":
                    return 250
                elif self.game.gamerules["dk.joker"] == "over_superpigs":
                    return 350

            return 0

    def get_eyes(self, card: Card) -> int:
        if card.card_value in ["j0", "j1", "j2"]:
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

    def deal_card(self, dt):
        stack = self.slots["stack"]
        kr = 3
        if self.deal_counter >= 12:
            if self.game.gamerules["dk.without9"] == "with_four":
                kr = 2
            elif self.game.gamerules["dk.without9"] == "without":
                kr = 1

        for k in range(kr):  # 3 cards (or less in the last round, if 9s are disabled)
            if self.DEV_MODE_PREP_CARDS:
                card_id = stack.pop(0)
            else:
                card_id = stack.pop(random.randint(0, len(stack) - 1))
            self.game.cg.info(f"Dealing card {self.cards[card_id].card_value} to hand{self.deal_counter % 4}")
            self.transfer_card(self.cards[card_id], "stack", f"hand{self.deal_counter % 4}")

        self.deal_counter += 1

        if self.deal_counter >= 16:
            self.game.cg.server.schedule_function(self.deal_ready, self.CARD_DEAL_DELAY)
        else:
            self.game.cg.server.schedule_function(self.deal_card, self.CARD_DEAL_DELAY)

    def deal_ready(self, dt):
        self.game_state = "w_for_ready"
        self.game.send_to_all("cg:game.dk.round.change", {
            "phase": "w_for_ready"
        })

    def start(self):
        self.game.cg.info(f"START")

        # Create card deck
        with9 = self.game.gamerules["dk.without9"]
        with9 = 0 if with9 == "without" else 4 if with9 == "with_four" else 8

        joker = self.game.gamerules["dk.joker"]
        joker = joker != "None"

        self.cards = create_dk_deck(with9=with9, joker=joker)
        if self.DEV_MODE_PREP_CARDS:
            self.cards = create_dk_prepped_deck()

        for card in self.cards.values():
            self.transfer_card(card, None, "stack")

        # Deal the cards
        self.game_state = "dealing"
        self.game.send_to_all("cg:game.dk.round.change", {
            "phase": "dealing",
        })

        self.deal_card(0)

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
                self.parties["re"].add(player)
                self.game.send_to_user(player, "cg:game.dk.round.change", {
                    "rebtn_lbl": "re"
                })
            elif list(map(lambda x: self.cards[x].card_value, hand)).count("cq") == 0:
                self.parties["kontra"].add(player)
                self.game.send_to_user(player, "cg:game.dk.round.change", {
                    "rebtn_lbl": "kontra"
                })

            self.obvious_parties["unknown"].add(player)

        self.game_type = "normal"
        self.game_state = "tricks"
        self.start_hands = self.hands

        self.game.send_to_all("cg:game.dk.round.change", {
            "phase": "tricks",
            "game_type": "normal",
        })

        self.current_player = self.players[0]
        self.trick_num = 1

        self.game.send_to_all("cg:game.dk.turn", {
            "current_trick": 1,
            "total_tricks": self.max_tricks,
            "current_player": self.current_player.hex
        })

    def start_solo(self, solist: uuid.UUID, pigs_handled=True):
        self.reserv_state = "finished"

        self.game_type = self.players_with_solo[solist]

        # Put the players into their parties
        self.parties["re"].add(solist)
        self.game.send_to_user(solist, "cg:game.dk.round.change", {
            "rebtn_lbl": "re"
        })
        for i in self.players:
            if i != solist:
                self.parties["kontra"].add(i)
                self.game.send_to_user(i, "cg:game.dk.round.change", {
                    "rebtn_lbl": "kontra"
                })

        # Obvious parties
        if self.game_type != "silent_wedding":
            self.obvious_parties["re"].add(solist)
            for i in self.players:
                if i != solist:
                    self.obvious_parties["kontra"].add(i)
        else:
            self.obvious_parties["unknown"].update(self.players)

        # Handle question for pigs
        if not pigs_handled:
            if self.game_type in ["solo_clubs", "solo_spades", "solo_hearts", "solo_diamonds", "solo_null"]:
                self.current_player = self.players[0]
                self.reserv_state = "pigs_solo"
                self.game.send_to_all("cg:game.dk.question", {
                    "type": "pigs",
                    "target": solist.hex
                })
                return

        self.game_state = "tricks"
        self.start_hands = self.hands

        if self.game_type == "silent_wedding":
            self.game.send_to_all("cg:game.dk.round.change", {
                "phase": "tricks",
                "game_type": "normal"
            })
        else:
            self.game.send_to_all("cg:game.dk.round.change", {
                "phase": "tricks",
                "game_type": self.game_type,
                "solist": solist.hex
            })

        # Starting player
        if self.game_type != "silent_wedding" and self.game.gamerules["dk.solist_begins"]:
            self.current_player = solist
        else:
            self.current_player = self.players[0]

        self.trick_num = 1

        self.game.send_to_all("cg:game.dk.turn", {
            "current_trick": 1,
            "total_tricks": self.max_tricks,
            "current_player": self.current_player.hex
        })

    def start_poverty(self, accepter: uuid.UUID):
        self.reserv_state = "finished"

        self.game_type = "poverty"
        self.game_state = "tricks"
        self.start_hands = self.hands

        self.game.send_to_all("cg:game.dk.round.change", {
            "phase": "tricks",
            "game_type": "poverty"
        })

        # Put the players into their parties
        self.parties["re"].update([self.poverty_player, accepter])
        self.game.send_to_user(self.poverty_player, "cg:game.dk.round.change", {
            "rebtn_lbl": "re"
        })
        self.game.send_to_user(accepter, "cg:game.dk.round.change", {
            "rebtn_lbl": "re"
        })
        for i in self.players:
            if i not in self.parties["re"]:
                self.parties["kontra"].add(i)
                self.game.send_to_user(i, "cg:game.dk.round.change", {
                    "rebtn_lbl": "kontra"
                })

        # Obvious parties
        self.obvious_parties["re"].update(self.parties["re"])
        self.obvious_parties["kontra"].update(self.parties["kontra"])

        self.current_player = self.players[0]
        self.trick_num = 1

        self.game.send_to_all("cg:game.dk.turn", {
            "current_trick": 1,
            "total_tricks": self.max_tricks,
            "current_player": self.current_player.hex
        })

    def start_black_sow(self):
        self.reserv_state = "finished"

        self.game_type = "black_sow"
        self.game_state = "tricks"
        self.start_hands = self.hands

        for p in self.players:
            self.parties["none"].add(p)
            self.obvious_parties["unknown"].add(p)

        self.game.send_to_all("cg:game.dk.round.change", {
            "phase": "tricks",
            "game_type": "black_sow",
        })

        self.current_player = self.players[0]
        self.trick_num = 1

        self.game.send_to_all("cg:game.dk.turn", {
            "current_trick": 1,
            "total_tricks": self.max_tricks,
            "current_player": self.current_player.hex
        })

    def start_ramsch(self):
        self.reserv_state = "finished"

        self.game_type = "ramsch"
        self.game_state = "tricks"
        self.start_hands = self.hands

        for player, hand in self.hands.items():
            # Put the players into their parties
            if list(map(lambda x: self.cards[x].card_value, hand)).count("cq") == 1:
                self.parties["re"].add(player)
                self.game.send_to_user(player, "cg:game.dk.round.change", {
                    "rebtn_lbl": "re"
                })
            elif list(map(lambda x: self.cards[x].card_value, hand)).count("cq") == 0:
                self.parties["kontra"].add(player)
                self.game.send_to_user(player, "cg:game.dk.round.change", {
                    "rebtn_lbl": "kontra"
                })
            elif list(map(lambda x: self.cards[x].card_value, hand)).count("cq") == 2:
                self.parties["re"].add(player)
                self.game.send_to_user(player, "cg:game.dk.round.change", {
                    "rebtn_lbl": "re"
                })
                self.game_type = "ramsch_sw"

            self.obvious_parties["unknown"].add(player)

        self.game.send_to_all("cg:game.dk.round.change", {
            "phase": "tricks",
            "game_type": "ramsch",
        })

        self.current_player = self.players[0]
        self.trick_num = 1

        self.game.send_to_all("cg:game.dk.turn", {
            "current_trick": 1,
            "total_tricks": self.max_tricks,
            "current_player": self.current_player.hex
        })

    def start_wedding(self, bride: uuid.UUID, trick: Optional[str] = None):
        self.reserv_state = "finished"

        # Add players to parties
        self.parties["re"].add(bride)
        for i in self.players:
            if i != bride:
                self.parties["none"].add(i)

        # Add obvious parties
        self.obvious_parties["re"].update(self.parties["re"])
        self.obvious_parties["unknown"].update(self.parties["none"])

        self.game_type = "wedding"
        self.game_state = "tricks"
        self.start_hands = self.hands

        self.wedding_clarification_trick = trick

        self.game.send_to_all("cg:game.dk.round.change", {
            "phase": "tricks",
            "game_type": "wedding",
        })

        self.current_player = self.players[0]
        self.trick_num = 1

        self.game.send_to_all("cg:game.dk.turn", {
            "current_trick": 1,
            "total_tricks": self.max_tricks,
            "current_player": self.current_player.hex
        })

    def end_round(self):
        self.game_state = "counting"

        # Put the poor players who stayed in the None Party into the kontra party
        for p in self.parties["none"]:
            self.parties["kontra"].add(p)
        self.parties["none"].clear()

        # Game Summary
        game_summary = []

        # Count the eyes and extra_points of the parties
        re_eyes, kontra_eyes = 0, 0
        re_extra, kontra_extra = 0, 0
        re_extras, kontra_extras = [], []
        for p in self.parties["re"]:
            re_eyes += self.player_eyes[p]
            re_extra += len(self.extra_points[p])
            re_extras.extend(self.extra_points[p])
        for p in self.parties["kontra"]:
            kontra_eyes += self.player_eyes[p]
            kontra_extra += len(self.extra_points[p])
            kontra_extras.extend(self.extra_points[p])

        # Get the needed win eyes
        re_win, kontra_win = 121, 120

        if "kontra" in self.modifiers["kontra"]:
            kontra_win = 121
            if "re" not in self.modifiers["re"]:
                re_win = 120

        if "no90" in self.modifiers["re"]:
            re_win = 151
            if "no90" not in self.modifiers["kontra"]:
                kontra_win = 90
        if "no60" in self.modifiers["re"]:
            re_win = 181
            if "no90" not in self.modifiers["kontra"]:
                kontra_win = 60
        if "no30" in self.modifiers["re"]:
            re_win = 211
            if "no90" not in self.modifiers["kontra"]:
                kontra_win = 30
        if "black" in self.modifiers["re"]:
            re_win = 240
            if "no90" not in self.modifiers["kontra"]:
                kontra_win = 1

        if "no90" in self.modifiers["kontra"]:
            kontra_win = 151
            if "no90" not in self.modifiers["re"]:
                re_win = 90
        if "no60" in self.modifiers["kontra"]:
            kontra_win = 181
            if "no90" not in self.modifiers["re"]:
                re_win = 60
        if "no30" in self.modifiers["kontra"]:
            kontra_win = 211
            if "no90" not in self.modifiers["re"]:
                re_win = 30
        if "black" in self.modifiers["kontra"]:
            kontra_win = 240
            if "no90" not in self.modifiers["re"]:
                re_win = 1

        # Determine the winner
        winner = None
        if re_eyes >= re_win:
            winner = "re"
            game_summary.append("re_win")
        elif kontra_eyes >= kontra_win:
            winner = "kontra"
            game_summary.append("kontra_win")

        if re_eyes >= re_win and kontra_eyes >= kontra_win:
            raise GameStateError("Only one party can win!")

        # Determine the game value - The game value is positive for re and negative for kontra
        game_value = 0
        if winner == "re":
            game_value = 1
        elif winner == "kontra":
            game_value = -1
        else:
            game_summary.append("no_win")

        # Game summary re and kontra
        if winner is not None:
            if "re" in self.modifiers["re"]:
                game_summary.append("re")
            if "kontra" in self.modifiers["kontra"]:
                game_summary.append("kontra")

        # Eyes, under which a party was played
        if winner != "kontra":
            if kontra_eyes < 90:
                game_value += 1
                game_summary.append("no90")
            if kontra_eyes < 60:
                game_value += 1
                game_summary.remove("no90")
                game_summary.append("no60")
            if kontra_eyes < 30:
                game_value += 1
                game_summary.remove("no60")
                game_summary.append("no30")
            if kontra_eyes == 0:
                game_value += 1
                game_summary.remove("no30")
                game_summary.append("black")

        if winner != "re":
            if re_eyes < 90:
                game_value -= 1
                game_summary.append("no90")
            if re_eyes < 60:
                game_value -= 1
                game_summary.remove("no90")
                game_summary.append("no60")
            if re_eyes < 30:
                game_value -= 1
                game_summary.remove("no60")
                game_summary.append("no30")
            if re_eyes == 0:
                game_value -= 1
                game_summary.remove("no30")
                game_summary.append("black")

        # Denials that the winner reached
        if winner == "re":
            if kontra_eyes < 90 and "no90" in self.modifiers["re"]:
                game_value += 1
                game_summary.append("c_no90")
            if kontra_eyes < 60 and "no60" in self.modifiers["re"]:
                game_value += 1
                game_summary.remove("c_no90")
                game_summary.append("c_no60")
            if kontra_eyes < 30 and "no30" in self.modifiers["re"]:
                game_value += 1
                game_summary.remove("c_no60")
                game_summary.append("c_no30")
            if kontra_eyes == 0 and "black" in self.modifiers["re"]:
                game_value += 1
                game_summary.remove("c_no30")
                game_summary.append("c_black")

        if winner == "kontra":
            if re_eyes < 90 and "no90" in self.modifiers["kontra"]:
                game_value -= 1
                game_summary.append("c_no90")
            if re_eyes < 60 and "no60" in self.modifiers["kontra"]:
                game_value -= 1
                game_summary.remove("c_no90")
                game_summary.append("c_no60")
            if re_eyes < 30 and "no30" in self.modifiers["kontra"]:
                game_value -= 1
                game_summary.remove("c_no60")
                game_summary.append("c_no30")
            if re_eyes == 0 and "black" in self.modifiers["kontra"]:
                game_value -= 1
                game_summary.remove("c_no30")
                game_summary.append("c_black")

        # Denials that the looser didn't reach
        if winner == "kontra":
            if "no90" in self.modifiers["re"]:
                game_value -= 1
                game_summary.append("fc_no90")
            if "no60" in self.modifiers["re"]:
                game_value -= 1
                game_summary.remove("fc_no90")
                game_summary.append("fc_no60")
            if "no30" in self.modifiers["re"]:
                game_value -= 1
                game_summary.remove("fc_no60")
                game_summary.append("fc_no30")
            if "black" in self.modifiers["re"]:
                game_value -= 1
                game_summary.remove("fc_no30")
                game_summary.append("fc_black")

        if winner == "re":
            if "no90" in self.modifiers["kontra"]:
                game_value += 1
                game_summary.append("fc_no90")
            if "no60" in self.modifiers["kontra"]:
                game_value += 1
                game_summary.remove("fc_no90")
                game_summary.append("fc_no60")
            if "no30" in self.modifiers["kontra"]:
                game_value += 1
                game_summary.remove("fc_no60")
                game_summary.append("fc_no30")
            if "black" in self.modifiers["kontra"]:
                game_value += 1
                game_summary.remove("fc_no30")
                game_summary.append("fc_black")

        # Denials that were overshot by 30 points
        if winner != "re":
            goal = min(int(kontra_eyes / 30) * 30, 120)
            if "no90" in self.modifiers["re"] and kontra_eyes >= 120:
                game_value -= 1
                game_summary.append(f"{goal}vs_no90")
            if "no60" in self.modifiers["re"] and kontra_eyes >= 90:
                game_value -= 1
                if f"{goal}vs_no90" in game_summary:
                    game_summary.remove(f"{goal}vs_no90")
                game_summary.append(f"{goal}vs_no60")
            if "no30" in self.modifiers["re"] and kontra_eyes >= 60:
                game_value -= 1
                if f"{goal}vs_no60" in game_summary:
                    game_summary.remove(f"{goal}vs_no60")
                game_summary.append(f"{goal}vs_no30")
            if "black" in self.modifiers["re"] and kontra_eyes >= 30:
                game_value -= 1
                if f"{goal}vs_no30" in game_summary:
                    game_summary.remove(f"{goal}vs_no30")
                game_summary.append(f"{goal}vs_black")

        if winner != "kontra":
            goal = min(int(re_eyes / 30) * 30, 120)
            if "no90" in self.modifiers["kontra"] and re_eyes >= 120:
                game_value += 1
                game_summary.append(f"{goal}vs_no90")
            if "no60" in self.modifiers["kontra"] and re_eyes >= 90:
                game_value += 1
                if f"{goal}vs_no90" in game_summary:
                    game_summary.remove(f"{goal}vs_no90")
                game_summary.append(f"{goal}vs_no60")
            if "no30" in self.modifiers["kontra"] and re_eyes >= 60:
                game_value += 1
                if f"{goal}vs_no60" in game_summary:
                    game_summary.remove(f"{goal}vs_no60")
                game_summary.append(f"{goal}vs_no30")
            if "black" in self.modifiers["kontra"] and re_eyes >= 30:
                game_value += 1
                if f"{goal}vs_no30" in game_summary:
                    game_summary.remove(f"{goal}vs_no30")
                game_summary.append(f"{goal}vs_black")

        # Re and Kontra as adding multipliers
        if self.game.gamerules["dk.re_kontra"] == "+2":
            if winner == "re":
                if "re" in self.modifiers["re"]:
                    game_value += 2
                if "kontra" in self.modifiers["kontra"]:
                    game_value += 2
            elif winner == "kontra":
                if "re" in self.modifiers["re"]:
                    game_value -= 2
                if "kontra" in self.modifiers["kontra"]:
                    game_value -= 2

        # Re and Kontra as doubling multipliers
        elif self.game.gamerules["dk.re_kontra"] == "*2":
            if winner in ["re", "kontra"]:
                if "re" in self.modifiers["re"]:
                    game_value *= 2
                if "kontra" in self.modifiers["kontra"]:
                    game_value *= 2

        # One point if Kontra won against the queens of clubs
        if winner == "kontra" and self.game_type in ["normal", "ramsch", "wedding"]:
            kontra_extras.insert(0, "against_cqs")
            kontra_extra += 1

        # Punishment for cowardice
        if self.game.gamerules["dk.coward"] != "None":
            if winner == "re" and re_eyes > 210:
                if "re" not in self.modifiers["re"]:
                    game_value *= -1
                    game_summary.append("cowardice")
                elif "no90" not in self.modifiers["re"]:  # Re is in modifiers, so it isn't handled two times
                    if self.game.gamerules["dk.coward"] == "240_no_u90" and re_eyes == 240:
                        game_value *= -1
                        game_summary.append("cowardice")
            elif winner == "kontra" and kontra_eyes > 210:
                if "kontra" not in self.modifiers["kontra"]:
                    game_value *= -1
                    game_summary.append("cowardice")
                elif "no90" not in self.modifiers["kontra"]:
                    if self.game.gamerules["dk.coward"] == "240_no_u90" and kontra_eyes == 240:
                        game_value *= -1
                        game_summary.append("cowardice")

        # Adding the extra points
        game_value += re_extra
        game_value -= kontra_extra

        # Extra points in summary
        if winner != "kontra":
            for extra in re_extras:
                game_summary.append(f"p_{extra}")
            for extra in kontra_extras:
                game_summary.append(f"n_{extra}")

        if winner != "re":
            for extra in kontra_extras:
                game_summary.append(f"p_{extra}")
            for extra in re_extras:
                game_summary.append(f"n_{extra}")

        # Re and Kontra as doubling multipliers after adding the extra points
        if self.game.gamerules["dk.re_kontra"] == "*2_extra":
            if winner in ["re", "kontra"]:
                if "re" in self.modifiers["re"]:
                    game_value *= 2
                if "kontra" in self.modifiers["kontra"]:
                    game_value *= 2

        # Buckround causes
        if "draw" in self.game.gamerules["dk.buck_cause"]:
            if re_eyes == kontra_eyes:
                self.buckround_events += 1

        if "0points" in self.game.gamerules["dk.buck_cause"]:
            if winner == "re" and game_value <= 0:
                self.buckround_events += 1

        if "re_kontra_lost" in self.game.gamerules["dk.buck_cause"]:
            if winner != "re" and "re" in self.modifiers["re"]:
                self.buckround_events += 1
            if winner != "kontra" and "kontra" in self.modifiers["kontra"]:
                self.buckround_events += 1

        if "solo_lost" in self.game.gamerules["dk.buck_cause"]:
            if winner != "re" and len(self.parties["re"]) == 1:
                self.buckround_events += 1

        self.game.cg.send_event("cg:game.dk.end_round", {
            "game_type": self.game_type,
            "winner": winner,
            "game_value": game_value,
            "re": [p for p in self.parties["re"]],
            "kontra": [p for p in self.parties["kontra"]],
            "eyes": (re_eyes, kontra_eyes),
            "modifiers": self.modifiers,
            "extras": [re_extras, kontra_extras],
            "buckround_events": self.buckround_events,
            "game_summary": game_summary
        })

    def register_event_handlers(self):
        self.game.cg.add_event_listener("cg:game.dk.reservation", self.handle_reservation, cg.event.F_RAISE_ERRORS,
                                        group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.reservation_solo", self.handle_reservation_solo,
                                        cg.event.F_RAISE_ERRORS, group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.reservation_throw", self.handle_reservation_throw,
                                        cg.event.F_RAISE_ERRORS, group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.reservation_pigs", self.handle_reservation_pigs,
                                        cg.event.F_RAISE_ERRORS, group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.reservation_superpigs", self.handle_reservation_superpigs,
                                        cg.event.F_RAISE_ERRORS, group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.reservation_poverty", self.handle_reservation_poverty,
                                        cg.event.F_RAISE_ERRORS, group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.reservation_poverty_pass_card",
                                        self.handle_reservation_poverty_pass_card, cg.event.F_RAISE_ERRORS,
                                        group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.reservation_poverty_accept", self.handle_reservation_poverty_accept,
                                        cg.event.F_RAISE_ERRORS, group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.reservation_wedding", self.handle_reservation_wedding,
                                        cg.event.F_RAISE_ERRORS, group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.reservation_wedding_clarification_trick",
                                        self.handle_reservation_wedding_clarification_trick, cg.event.F_RAISE_ERRORS,
                                        group=self.round_id)

        self.game.cg.add_event_listener("cg:game.dk.play_card", self.handle_play_card, cg.event.F_RAISE_ERRORS,
                                        group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.call_pigs", self.handle_call_pigs, cg.event.F_RAISE_ERRORS,
                                        group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.call_superpigs", self.handle_call_superpigs,
                                        cg.event.F_RAISE_ERRORS, group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.call_re", self.handle_call_re, cg.event.F_RAISE_ERRORS,
                                        group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.call_denial", self.handle_call_denial, cg.event.F_RAISE_ERRORS,
                                        group=self.round_id)

        self.game.cg.add_event_listener("cg:game.dk.black_sow_solo", self.handle_black_sow_solo,
                                        cg.event.F_RAISE_ERRORS, group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.throw", self.handle_throw, cg.event.F_RAISE_ERRORS,
                                        group=self.round_id)
        self.game.cg.add_event_listener("cg:game.dk.ready", self.handle_ready, cg.event.F_RAISE_ERRORS,
                                        group=self.round_id)

        self.game.cg.add_event_listener("cg:game.dk.command", self.handle_command, cg.event.F_RAISE_ERRORS,
                                        group=self.round_id)

    def handle_ready(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_state != "w_for_ready":
            raise GameStateError(f"Game state for ready handling must be 'w_for_ready', not {self.game_state}!")

        player = uuidify(data["player"])
        if player not in self.rdy_players:
            self.rdy_players.append(player)
        else:
            raise InvalidMoveError(f"Player {player} already conveyed his readyness!")

        # Announce player ready
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": player.hex,
            "type": "ready"
        })

        # Start reservations
        if len(self.rdy_players) == 4:
            # Reservations: Only initialisation, the rest of the code is handled by event handlers
            self.game_state = "reservations"
            self.reserv_state = "reservation"

            self.game.send_to_all("cg:game.dk.round.change", {
                "phase": "reservations",
            })

            self.current_player = self.players[0]
            self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                "type": "reservation",
                "target": self.players[0].hex
            })

    def handle_throw(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_state != "w_for_ready":
            raise GameStateError(f"Game state for throw handling must be 'w_for_ready', not {self.game_state}!")
        if self.game.gamerules["dk.throw"] != "throw":
            raise RuleError("Throwing is not permitted by the rules!")

        player = uuidify(data["player"])

        legal_throw = False

        # Check, whether throwing is justified
        nines = []
        kings = []
        fulls = []
        high_trumps = []
        dj = False

        player_hand = [self.cards[i] for i in self.hands[player]]
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
            self.game.cg.server.send_status_message(player, "warn", "cg:msg.game.dk.invalid_throw")
            return

        # Announce the throwing
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": player.hex,
            "type": data["type"]
        })

        # Register move
        self.add_move(player, "announcement", data["type"])

        # Exit the round
        self.game.cg.send_event("cg:game.dk.end_round", {
            "game_type": "throw",
            "winner": None,
            "re": [],
            "kontra": [],
            "eyes": 0,
            "modifiers": self.modifiers,
            "extras": []
        })

    def handle_reservation(self, event: str, data: Dict):
        # Check for correct states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_state != "reservations":
            raise GameStateError(f"Game state for reservation handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state != "reservation":
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
            self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                "type": "reservation",
                "target": self.current_player.hex
            })

        # After everyone was asked...
        else:
            # Ask the first player with reservation for a solo
            if len(self.players_with_reserv) > 0:
                self.current_player = self.players_with_reserv[0]
                self.reserv_state = "solo"
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "solo",
                    "target": self.current_player.hex
                })
            # Abort, if there aren't any reservations
            else:
                self.start_normal()

    def handle_reservation_solo(self, event: str, data: Dict):
        # Check for correct states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_state != "reservations":
            raise GameStateError(f"Game state for solo handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state != "solo":
            raise GameStateError(f"Reservations state for solo handling must be 'solo', not {self.reserv_state}!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the solo handling packet is not the current player!")

        # Remember, if the player want's to play a valid solo
        if data["type"] == "solo_yes":
            solo_type = data["data"]["type"]
            if solo_type in self.game.gamerules["dk.solos"]:
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

        # Start the solo if the first announcer plays his solo
        if self.game.gamerules["dk.solo_prio"] == "first" and data["type"] == "solo_yes":
            if self.game.gamerules["dk.pigs"] == "two_reservation":
                self.start_solo(uuidify(data["player"]), False)
            else:
                self.start_solo(uuidify(data["player"]))
            return

        # Go to the next player with reservation
        self.current_player = self.players_with_reserv[
            (self.players_with_reserv.index(self.current_player) + 1) % len(self.players_with_reserv)
            ]

        # Ask the next player for a solo if he hasn't been asked yet
        if self.current_player != self.players_with_reserv[0]:
            self.game.send_to_user(self.current_player, "cg:game.dk.question", {
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

                if self.game.gamerules["dk.pigs"] == "two_reservation":
                    self.start_solo(uuidify(data["player"]), False)
                else:
                    self.start_solo(uuidify(data["player"]))

            # If no one wants to play a solo
            else:
                self.current_player = self.players_with_reserv[0]

                # Ask for the next reservation that is enabled in the rules
                if self.game.gamerules["dk.throw"] == "reservation":
                    self.reserv_state = "throw"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "throw",
                        "target": self.current_player.hex
                    })
                elif self.game.gamerules["dk.pigs"] == "two_reservation":
                    self.reserv_state = "pigs"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "pigs",
                        "target": self.current_player.hex
                    })
                elif self.game.gamerules["dk.poverty"] != "None":
                    self.reserv_state = "poverty"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "poverty",
                        "target": self.current_player.hex
                    })
                elif self.game.gamerules["dk.wedding"] != "None":
                    self.reserv_state = "wedding"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "wedding",
                        "target": self.current_player.hex
                    })
                # Or abort, if there aren't any left
                else:
                    self.start_normal()

    def handle_reservation_throw(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
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
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.invalid_throw")
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "throw",
                    "target": self.current_player.hex
                })
                return

            # Announce the throwing
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"]
            })

            # Register move
            self.add_move(self.current_player, "announcement", data["type"])

            # Exit the round
            self.game.cg.send_event("cg:game.dk.end_round", {
                "game_type": "throw",
                "winner": None,
                "re": [],
                "kontra": [],
                "eyes": 0,
                "modifiers": self.modifiers,
                "extras": []
            })

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
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "throw",
                    "target": self.current_player.hex
                })

            # If nobody want's to throw
            else:
                # Ask for the next reservation that is enabled in the rules
                if self.game.gamerules["dk.pigs"] == "two_reservation":
                    self.reserv_state = "pigs"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "pigs",
                        "target": self.current_player.hex
                    })
                elif self.game.gamerules["dk.poverty"] != "None":
                    self.reserv_state = "poverty"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "poverty",
                        "target": self.current_player.hex
                    })
                elif self.game.gamerules["dk.wedding"] != "None":
                    self.reserv_state = "wedding"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "wedding",
                        "target": self.current_player.hex
                    })
                # Or abort if there aren't any left
                else:
                    self.start_normal()

    def handle_reservation_pigs(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_state != "reservations":
            raise GameStateError(f"Game state for pigs handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state not in ["pigs", "pigs_solo"]:
            raise GameStateError(f"Reservations state for pigs handling must be 'pigs', not {self.reserv_state}!")
        if self.game.gamerules["dk.pigs"] != "two_reservation":
            raise RuleError("Pigs are disabled by the rules!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the pigs handling packet is not the current player!")

        # Determine the fox card for calling pigs
        if self.game_type == "solo_hearts":
            fox_card = "ha"
        elif self.game_type == "solo_spades":
            fox_card = "sa"
        elif self.game_type == "solo_clubs":
            fox_card = "ca"
        elif self.game_type in ["normal", "silent_wedding", "wedding", "poverty", "ramsch", "ramsch_sw",
                                "solo_diamonds", "solo_null", "black_sow"]:
            fox_card = "da"
        else:
            fox_card = ""

        # Register pigs a players pigs if he has them
        if data["type"] == "pigs_yes":
            player_hand = [self.cards[i] for i in self.hands[self.current_player]]
            if list(map(lambda x: x.card_value, player_hand)).count(fox_card) != 2:  # Not two diamond aces in the hand
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.invalid_pigs")
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "pigs",
                    "target": self.current_player.hex
                })
                return
            else:
                self.pigs = [True, self.current_player]

        # Announce decision
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": data["type"]
        })

        # Register move
        self.add_move(self.current_player, "announcement", data["type"])

        # Go to next reservation
        if self.reserv_state == "pigs":
            self.current_player = self.players_with_reserv[
                (self.players_with_reserv.index(self.current_player) + 1) % len(self.players_with_reserv)
                ]
        else:
            self.current_player = self.players[(self.players.index(self.current_player) + 1) % len(self.players)]

        # If no pigs have been called yet and the player hasn't been asked yet
        if not self.pigs[0] and ((self.current_player != self.players_with_reserv[0] and
                                  self.reserv_state == "pigs") or
                                 (self.current_player != self.players[0] and
                                  self.reserv_state == "pigs_solo")):
            self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                "type": "pigs",
                "target": self.current_player.hex
            })

        # If everyone has been asked or someone called pigs
        else:
            # Reset to first reservation
            if self.reserv_state == "pigs":
                self.current_player = self.players_with_reserv[0]

                # Ask for superpigs
                if self.pigs[0] and self.game.gamerules["dk.superpigs"] == "reservation":
                    self.current_player = self.players[0]
                    self.reserv_state = "superpigs"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "superpigs",
                        "target": self.current_player.hex
                    })
                # Or for other reservations
                elif self.game.gamerules["dk.poverty"] != "None":
                    self.reserv_state = "poverty"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "poverty",
                        "target": self.current_player.hex
                    })
                elif self.game.gamerules["dk.wedding"] != "None":
                    self.reserv_state = "wedding"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "wedding",
                        "target": self.current_player.hex
                    })
                # Or abort, if no legal reservations are left
                else:
                    self.start_normal()

            elif self.reserv_state == "pigs_solo":
                # Ask for superpigs
                if self.pigs[0] and self.game.gamerules["dk.superpigs"] == "reservation":
                    self.current_player = self.players[0]
                    self.reserv_state = "superpigs_solo"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "superpigs",
                        "target": self.current_player.hex
                    })
                else:
                    self.start_solo(next(iter(self.parties["re"])))

    def handle_reservation_superpigs(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_state != "reservations":
            raise GameStateError(f"Game state for superpigs handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state not in ["superpigs", "superpigs_solo"]:
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
            superpig_card = ""
            if self.game.gamerules["dk.without9"] == "with_all":
                if self.game_type == "solo_hearts":
                    superpig_card = "h9"
                elif self.game_type == "solo_spades":
                    superpig_card = "s9"
                elif self.game_type == "solo_clubs":
                    superpig_card = "c9"
                elif self.game_type in ["normal", "silent_wedding", "wedding", "poverty", "ramsch", "ramsch_sw",
                                        "solo_diamonds", "solo_null", "black_sow"]:
                    superpig_card = "d9"
            elif self.game.gamerules["dk.without9"] in ["with_four", "without"]:
                if self.game.gamerules["dk.without9"] == "with_all":
                    if self.game_type == "solo_hearts":
                        superpig_card = "hk"
                    elif self.game_type == "solo_spades":
                        superpig_card = "sk"
                    elif self.game_type == "solo_clubs":
                        superpig_card = "ck"
                    elif self.game_type in ["normal", "silent_wedding", "wedding", "poverty", "ramsch", "ramsch_sw",
                                            "solo_diamonds", "solo_null", "black_sow"]:
                        superpig_card = "dk"

            player_hand = [self.cards[i] for i in self.hands[self.current_player]]
            if not list(map(lambda x: x.card_value, player_hand)).count(superpig_card) == 2:
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn",
                                                        "cg:msg.game.dk.invalid_superpigs")
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "superpigs",
                    "target": self.current_player.hex
                })
                return
            self.superpigs = [True, self.current_player]

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
            self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                "type": "superpigs",
                "target": self.current_player.hex
            })

        # If superpigs were called or everyone was asked
        else:
            if self.reserv_state == "superpigs":
                self.current_player = self.players_with_reserv[0]

                # Ask for the next legal reservation
                if self.game.gamerules["dk.poverty"] != "None":
                    self.reserv_state = "poverty"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "poverty",
                        "target": self.current_player.hex
                    })
                elif self.game.gamerules["dk.wedding"] != "None":
                    self.reserv_state = "wedding"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "wedding",
                        "target": self.current_player.hex
                    })
                # Or abort if none are left
                else:
                    self.start_normal()

            elif self.reserv_state == "superpigs_solo":
                self.start_solo(next(iter(self.parties["re"])))

    def handle_reservation_poverty(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
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
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn",
                                                        "cg:msg.game.dk.invalid_poverty")
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "poverty",
                    "target": self.current_player.hex
                })
                return

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
            self.game.send_to_user(self.current_player, "cg:game.dk.question", {
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
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "poverty",
                    "target": self.current_player.hex
                })

            # If everybody has been asked
            else:
                # Ask for the next legal reservation
                if self.game.gamerules["dk.wedding"] != "None":
                    self.reserv_state = "wedding"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "type": "wedding",
                        "target": self.current_player.hex
                    })
                else:
                    self.start_normal()

    def handle_reservation_poverty_pass_card(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
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
                        self.game.cg.server.send_status_message(uuidify(data["player"]), "warn",
                                                                "cg:msg.game.dk.invalid_poverty_cards")
                        self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                            "type": "poverty_trump_choice",
                            "target": self.current_player.hex
                        })
                        return

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
                for c in self.poverty_cards:
                    self.transfer_card(self.cards[c],
                                       "poverty",
                                       "poverty")

                # Ask the next player if he accepts the poverty
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
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
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "poverty_return_trumps",
                    "target": self.current_player.hex
                })
                # --> handle_reservation_poverty_accept (type = "return")

    def handle_reservation_poverty_accept(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_state != "reservations":
            raise GameStateError(
                f"Game state for poverty accept handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state not in ["poverty_sell", "poverty_circulate", "poverty_return"]:
            raise GameStateError(f"Reservations state for poverty accept handling must be 'poverty_sell',"
                                 f"'poverty_circulate' or 'poverty_return', not {self.reserv_state}!")
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
            self.game.send_to_user(self.current_player, "cg:game.dk.question", {
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
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn",
                                                        "cg:msg.game.dk.invalid_return_amount",
                                                        {"ta": len(trumps), "ca": data['data']['amount']})
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "poverty_return_trumps",
                    "target": self.current_player.hex
                })
                return

            # Announce the amount of trumps
            self.game.send_to_all("cg:game.dk.announce", {
                "announcer": self.current_player.hex,
                "type": data["type"],
                "data": data["data"]
            })

            # Register move
            self.add_move(self.current_player, "announcement", "poverty_return_" + str(data["data"]["amount"]))

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
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
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
                if self.game.gamerules["dk.poverty_consequence"] == "None":
                    # Go to the next reservation
                    self.current_player = self.players_with_reserv[
                        (self.players_with_reserv.index(self.current_player) + 1) % len(self.players_with_reserv)
                        ]

                    # If the player hasn't been asked yet, ask for a reservation
                    if self.current_player != self.players_with_reserv[0]:
                        self.reserv_state = "poverty"
                        self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                            "type": "poverty",
                            "target": self.current_player.hex
                        })
                        # --> handle_reservation_poverty (type = "yes", "no")

                    # If everybody has been asked
                    else:
                        # Ask for the next legal reservation
                        if self.game.gamerules["dk.wedding"] != "None":
                            self.reserv_state = "wedding"
                            self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                                "type": "wedding",
                                "target": self.current_player.hex
                            })
                        else:
                            self.start_normal()

                # Redeal the game
                elif self.game.gamerules["dk.poverty_consequence"] == "redeal":
                    # Exit the round
                    self.game.cg.send_event("cg:game.dk.end_round", {
                        "game_type": "poverty_cancel",
                        "winner": None,
                        "re": [],
                        "kontra": [],
                        "eyes": 0,
                        "modifiers": self.modifiers,
                        "extras": []
                    })

                # Play a round of black sow
                elif self.game.gamerules["dk.poverty_consequence"] == "black_sow":
                    self.start_black_sow()

                # Play a round of ramsch
                elif self.game.gamerules["dk.poverty_consequence"] == "ramsch":
                    self.start_ramsch()

    def handle_reservation_wedding(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_state != "reservations":
            raise GameStateError(f"Game state for wedding handling must be 'reservations', not {self.game_state}!")
        if self.reserv_state != "wedding":
            raise GameStateError(f"Reservation state for wedding handling must be 'wedding', not {self.reserv_state}!")
        if self.game.gamerules["dk.wedding"] == "None":
            raise RuleError("Wedding is disabled by the rules!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the wedding handling packet is not the current player!")

        # If the player want's to play a wedding
        if data["type"] == "wedding_yes":
            # Check if the wedding is legal
            player_hand = [self.cards[i] for i in self.hands[self.current_player]]
            if not list(map(lambda x: x.card_value, player_hand)).count("cq") == 2:  # Hand contains two queens of clubs
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn",
                                                        "cg:msg.game.dk.invalid_wedding")
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "wedding",
                    "target": self.current_player.hex
                })
                return

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
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
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
                self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                    "type": "wedding",
                    "target": self.current_player.hex
                })

            # If everybody has been asked
            else:
                self.start_normal()

    def handle_reservation_wedding_clarification_trick(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_state != "reservations":
            raise GameStateError(f"Game state for wedding clarification trick handling must be 'reservations', not"
                                 f"{self.game_state}!")
        if self.reserv_state != "wedding":
            raise GameStateError(f"Reservations state for wedding clarification trick handling must be 'wedding', not"
                                 f"{self.reserv_state}!")
        if self.game.gamerules["dk.wedding"] != "wish_trick":
            raise RuleError("Wedding is disabled by the rules!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the wedding clarification trick handling packet is not the"
                                   f"current player!")

        if data["data"]["trick"] not in ["foreign", "trump", "miss", "hearts", "spades", "clubs", "diamonds"]:
            raise InvalidMoveError(f"Invalid Wedding clarification trick: {data['data']['trick']}")

        # Register move
        self.add_move(self.current_player, "announcement", "wedding_clarification_trick_" + data["data"]["trick"])

        self.start_wedding(self.current_player, data["data"]["trick"])

    def handle_play_card(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_state != "tricks":
            self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.pc_wrong_phase")
            return
        if uuidify(data["player"]) != self.current_player:
            self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.pc_wrong_turn")
            return
        if len(self.current_trick) >= 4:
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
            self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.pc_wrong_card")
            return

        # Determine fox card (for pigs and foxes)
        if self.game_type == "solo_hearts":
            fox_card = "ha"
        elif self.game_type == "solo_spades":
            fox_card = "sa"
        elif self.game_type == "solo_clubs":
            fox_card = "ca"
        elif self.game_type in ["normal", "silent_wedding", "wedding", "poverty", "ramsch", "ramsch_sw",
                                "solo_diamonds", "solo_null", "black_sow"]:
            fox_card = "da"
        else:
            fox_card = ""

        # For called pig, check if a pig is played
        if list(map(lambda x: x["data"], self.moves.values()))[-1] == "pigs":
            # Find out, which cards are the pigs in this round
            if self.cards[card].card_value != fox_card:
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn",
                                                        "cg:msg.game.dk.pc_called_pigs")
                return

        # For called superpig, check if a superpig is played:
        if self.game.gamerules["dk.superpigs"] == "on_play":
            if list(map(lambda x: x["data"], self.moves.values()))[-1] == "superpigs":
                # Find out, which cards are the superpigs in this round
                if self.game.gamerules["dk.without9"] == "with_all":
                    value = "9"
                else:
                    value = "k"

                if self.game_type == "solo_hearts":
                    color = "h"
                elif self.game_type == "solo_spades":
                    color = "s"
                elif self.game_type == "solo_clubs":
                    color = "c"
                else:
                    color = "d"

                superpig_card = color + value

                if self.cards[card].card_value != superpig_card:
                    self.game.cg.server.send_status_message(uuidify(data["player"]), "warn",
                                                            "cg:msg.game.dk.pc_called_superpigs")
                    return

        # Check if the card tells something about the parties
        if self.game_type in ["normal", "silent_wedding", "ramsch", "ramsch_sw"]:
            if self.cards[card].card_value == "cq":
                self.update_obvious_party(self.current_player, "re")

                # The second queen of clubs is being played
                if [self.cards[card].card_value for card in chain(*self.hands.values())].count("cq") == 1:
                    self.update_obvious_party(self.current_player, "re", True)
                    if not self.obvious_parties["re"] == self.parties["re"]:
                        raise GameStateError("Obvious re party doesn't correspond with re party, though it should!")

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
                "total_tricks": self.max_tricks,
                "current_player": self.current_player.hex
            })

        # Trick is full
        elif len(self.current_trick) == 4:
            self.game.cg.server.schedule_function(self.end_trick, 1, fox_card=fox_card)

    def end_trick(self, dt=None, fox_card=""):
        self.game.cg.info(f"Game Type: {self.game_type}")
        self.game.cg.info(f"Obvious Parties {self.obvious_parties}")

        # Determine the winner of the trick
        trick_winner, sorted_trick = self.get_trick_winner()
        gain = sum(map(lambda x: self.get_eyes(self.cards[x[1]]), self.current_trick))
        self.player_eyes[trick_winner] += gain

        # Check for the wedding trick
        if self.game_type == "wedding":
            if len(self.parties["kontra"]) == 0:  # Parties not decided yet
                if self.trick_num <= 3:
                    if trick_winner not in self.parties["re"]:
                        if self.wedding_clarification_trick in [None, "foreign"]:
                            wedding = True

                        elif self.wedding_clarification_trick == "trump":
                            wedding = self.get_card_color(self.cards[self.current_trick[0][1]]) == "trump"
                        elif self.wedding_clarification_trick == "miss":
                            wedding = self.get_card_color(self.cards[sorted_trick[0]]) != "trump"
                        elif self.wedding_clarification_trick in ["hearts", "spades", "clubs"]:
                            # The color must not be trumped
                            wedding = self.get_card_color(
                                self.cards[sorted_trick[0]]) == self.wedding_clarification_trick
                        elif self.wedding_clarification_trick == "diamonds":
                            # There may be no diamonds jacks or queens
                            wedding = True
                            for i in self.current_trick:
                                wedding = wedding and (self.cards[i[1]].card_value in ["d9", "d10", "dk", "da"])
                        else:
                            raise InvalidMoveError(
                                f"Invalid wedding clarification trick: {self.wedding_clarification_trick}")

                        self.game.cg.info(
                            f"wedding: {wedding}, wct: {self.wedding_clarification_trick}, card: {self.cards[sorted_trick[0]].card_value}")

                        if wedding:
                            self.parties["re"].add(trick_winner)
                            for p in self.players:
                                if p not in self.parties["re"]:
                                    self.parties["kontra"].add(p)
                                    self.game.send_to_user(p, "cg:game.dk.round.change", {
                                        "rebtn_lbl": "kontra"
                                    })
                            for p in self.parties["re"]:
                                self.game.send_to_user(p, "cg:game.dk.round.change", {
                                    "rebtn_lbl": "re"
                                })
                            self.parties["none"].clear()

                            self.update_obvious_party(trick_winner, "re")

                            self.wedding_find_trick = self.trick_num

                            # TODO Inform the players on the found wedding

                        self.game.cg.info(f"obvious parties: {self.obvious_parties}")

                    elif self.trick_num == 3:  # 3rd trick was made by re party
                        # Start diamonds solo
                        self.parties["kontra"] = self.parties["none"]
                        self.parties["none"].clear()

                        for p in self.parties["re"]:
                            self.game.send_to_user(p, "cg:game.dk.round.change", {
                                "rebtn_lbl": "re"
                            })
                        for p in self.parties["kontra"]:
                            self.game.send_to_user(p, "cg:game.dk.round.change", {
                                "rebtn_lbl": "kontra"
                            })

                        self.update_obvious_party(trick_winner, "re")

                        self.game_type = "solo_diamonds"

                        for expts in self.extra_points.values():
                            expts.clear()

                        self.game.send_to_all("cg:game.dk.round.change", {
                            "phase": "tricks",
                            "game_type": self.game_type,
                            "solist": trick_winner.hex
                        })

                        self.wedding_find_trick = self.trick_num

        # Check for extra tricks
        if self.game_type in ["normal", "wedding", "ramsch", "poverty"]:
            # Doppelkopf
            if self.game.gamerules["dk.doppelkopf"]:
                if gain >= 40:
                    self.extra_points[trick_winner].append("doppelkopf")

            # Fox
            if self.game.gamerules["dk.fox"]:
                for i in self.current_trick:
                    if self.cards[i[1]].card_value == fox_card:
                        # If the player won the trick himself
                        if i[0] == trick_winner:
                            continue

                        # If a trick winner and the fox player are in the same party
                        for party, members in self.obvious_parties.items():
                            if party != "unknown":
                                if i[0] in self.obvious_parties[party] and trick_winner in self.obvious_parties[
                                    party]:
                                    continue

                        # If the players are in different parties
                        if (i[0] in self.obvious_parties["re"] and trick_winner in self.obvious_parties[
                            "kontra"]) or (
                                i[0] in self.obvious_parties["kontra"] and trick_winner in self.obvious_parties[
                            "re"]):
                            self.extra_points[trick_winner].append("fox")

                        # If not both player's parties are sure, remember the fox and check it later
                        else:
                            self.foxes.append([i[0], trick_winner])

            # Charlie
            if self.game.gamerules["dk.charlie"]:
                if self.trick_num == self.max_tricks:
                    if self.cards[sorted_trick[0]].card_value == "cj":
                        self.extra_points[trick_winner].append("charlie")

            # Fox got the last trick
            if self.game.gamerules["dk.fox_lasttrick"]:
                if self.trick_num == self.max_tricks:
                    if self.cards[sorted_trick[0]].card_value == fox_card:
                        self.extra_points[trick_winner].append("fox_lasttrick")

            # Charlie broken and jane
            if self.game.gamerules["dk.charlie_broken"]:
                if self.trick_num == self.max_tricks:
                    for i in self.current_trick:
                        if self.cards[i[1]].card_value == "cj" and i[1] != sorted_trick[0]:
                            if trick_winner in self.parties["re"] and i[0] in self.parties["kontra"] or \
                                    trick_winner in self.parties["kontra"] and i[0] in self.parties["re"]:
                                if self.game.gamerules["dk.jane"]:
                                    if self.cards[sorted_trick[0]].card_value == "dq":
                                        self.extra_points[trick_winner].append("jane")
                                else:
                                    self.extra_points[trick_winner].append("charlie_broken")

            # Heartrick
            if self.game.gamerules["dk.heart_trick"]:
                heart_trick = True
                for i in self.current_trick:
                    heart_trick = heart_trick and self.get_card_color(self.cards[i[1]]) == "hearts"
                if heart_trick:
                    self.extra_points[trick_winner].append("heart_trick")

            # Second black trick
            if self.game.gamerules["dk.sec_black_trick"]:
                spade_trick = True
                for i in self.current_trick:
                    spade_trick = spade_trick and self.get_card_color(self.cards[i[1]]) == "spades"
                if spade_trick:
                    self.spade_tricks += 1
                    if self.spade_tricks == 2:
                        self.extra_points[trick_winner].append("sec_black_trick")

                clubs_trick = True
                for i in self.current_trick:
                    clubs_trick = clubs_trick and self.get_card_color(self.cards[i[1]]) == "clubs"
                if clubs_trick:
                    self.club_tricks += 1
                    if self.club_tricks == 2:
                        self.extra_points[trick_winner].append("sec_black_trick")

            # Hobgoblin
            if self.game.gamerules["dk.hobgoblin"]:
                if self.cards[sorted_trick[0]].card_value == "sq":
                    for i in self.current_trick:
                        if self.cards[i[1]].card_value == "sk":
                            self.extra_points[trick_winner].append("hobgoblin")

        # Check for buckround events
        if self.game_type in ["normal", "wedding", "wedding_silent", "ramsch", "poverty",
                              "ramsch_sw", "black_sow", "solo_diamonds"]:
            if "4hearts" in self.game.gamerules["dk.buck_cause"]:
                heart_trick = True
                for i in self.current_trick:
                    heart_trick = heart_trick and self.get_card_color(self.cards[i[1]]) == "hearts"
                if heart_trick:
                    self.buckround_events += 1

        # Transfer the trick to the winners trick stack
        for i in self.current_trick:
            self.transfer_card(self.cards[i[1]],
                               "table",
                               f"tricks{self.players.index(trick_winner)}")

        # Inform the players on the new scores
        self.game.send_to_all("cg:game.dk.scoreboard", {
            "player": trick_winner.hex,
            "pips": self.player_eyes[trick_winner],
            "pip_change": gain
        })

        # Not the last round
        if self.trick_num < self.max_tricks:
            # Deinitialise the trick
            self.current_player = trick_winner
            self.current_trick.clear()

            if self.game.gamerules["dk.pigs"] in ["one_first", "one_on_play", "one_on_fox"]:
                self.pigs[0] = False

            self.trick_num += 1

            # Check for black sow
            if self.game_type == "black_sow":
                for i in sorted_trick:
                    if self.cards[i].card_value == "sq":  # Queen of spades played
                        self.spade_queens += 1
                if self.spade_queens == 2:
                    self.game_state = "black_sow_solo"
                    self.game.send_to_user(self.current_player, "cg:game.dk.question", {
                        "target": trick_winner.hex,
                        "type": "black_sow_solo"
                    })
                    return

            self.game.send_to_all("cg:game.dk.turn", {
                "current_trick": self.trick_num,
                "total_tricks": self.max_tricks,
                "current_player": self.current_player.hex
            })

        # Last Round
        elif self.trick_num == self.max_tricks:
            self.game.cg.server.schedule_function(self.end_round, 1)

    def handle_call_pigs(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_type not in ["normal", "wedding", "silent_wedding", "poverty", "black_sow",
                                  "ramsch", "ramsch_sw", "solo_diamonds", "solo_hearts", "solo_spades", "solo_clubs",
                                  "solo_null"]:
            self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.invalid_pigs_game")
            return
        if self.game_state != "tricks":
            raise GameStateError(
                f"Game state for pigs call handling must be 'tricks', not {self.game_state}!")
        if self.game.gamerules["dk.pigs"] in ["None", "two_reservation"]:
            raise RuleError(f"Pigs are either disabled or already had to be called!")
        if uuidify(data["player"]) != self.current_player:
            self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.pc_wrong_turn")
            return
        if self.pigs[1] is not None:
            raise InvalidMoveError("Pigs have already been called!")

        # Find out, which cards are the pigs in this round
        if self.game_type == "solo_hearts":
            pig_card = "ha"
        elif self.game_type == "solo_spades":
            pig_card = "sa"
        elif self.game_type == "solo_clubs":
            pig_card = "ca"
        else:
            pig_card = "da"

        if self.game.gamerules["dk.pigs"] in ["two_on_play", "one_first"]:
            # The player has two pigs on his hand
            if not list(map(lambda x: self.cards[x].card_value, self.hands[self.current_player])).count(pig_card) == 2:
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.invalid_pigs")
                return
            self.pigs = [True, self.current_player]

        elif self.game.gamerules["dk.pigs"] == "one_on_play":
            # The player had two pigs at the start of the game and still one left
            if list(map(lambda x: self.cards[x].card_value, self.start_hands[self.current_player])).count(
                    pig_card) == 2:
                if list(map(lambda x: self.cards[x].card_value, self.hands[self.current_player])).count(pig_card) > 0:
                    self.pigs = [True, self.current_player]
            else:
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.invalid_pigs")
                return

        elif self.game.gamerules["dk.pigs"] == "one_on_fox":
            # The player had two pigs at the start of the game and still one left
            if not (
                    list(map(lambda x: self.cards[x].card_value, self.start_hands[self.current_player])).count(
                        pig_card) == 2 and
                    list(map(lambda x: self.cards[x].card_value, self.hands[self.current_player])).count(pig_card) > 0):
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.invalid_pigs")
                return

            # Check if the players party brought a fox home
            # The player took the fox
            for card in self.slots[f"tricks{self.players.index(self.current_player)}"]:
                if self.cards[card].value == pig_card:
                    self.pigs = [True, self.current_player]

            # The players party member(s) took it
            if not self.pigs[0]:
                cur_player_party = ""
                for party, players in self.parties.items():
                    if self.current_player in players:
                        cur_player_party = party
                if cur_player_party == "none":
                    self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:game.dk.invalid_pigs")
                    return

                for player in self.obvious_parties[cur_player_party]:
                    for card in self.slots[f"tricks{self.players.index(player)}"]:
                        if self.cards[card].card_value == pig_card:
                            self.pigs = [True, self.current_player]

            if not self.pigs[0]:
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.invalid_pigs")
                return

        # Announce the pig call
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": "pigs"
        })

        # Register the move
        self.add_move(self.current_player, "announcement", data["type"])

    def handle_call_superpigs(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_type not in ["normal", "wedding", "silent_wedding", "poverty", "black_sow",
                                  "ramsch", "ramsch_sw", "solo_diamonds", "solo_hearts", "solo_spades", "solo_clubs",
                                  "solo_null"]:
            self.game.cg.server.send_status_message(uuidify(data["player"]), "warn",
                                                    "cg:msg.game.dk.invalid_superpigs_game")
            return
        if self.game_state != "tricks":
            raise GameStateError(f"Game state for superpigs call handling must be 'tricks', not {self.game_state}!")
        if self.game.gamerules["dk.superpigs"] in ["None", "reservation"]:
            raise RuleError(f"Superpigs are either disabled or already had to be called!")
        if self.pigs[1] is None:
            raise InvalidMoveError("Superpigs cannot be called with pigs not being called!")

        player = uuidify(data["player"])

        # Find out, which cards are the superpigs in this round
        if self.game.gamerules["dk.without9"] == "with_all":
            value = "9"
        else:
            value = "k"

        if self.game_type == "solo_hearts":
            color = "h"
        elif self.game_type == "solo_spades":
            color = "s"
        elif self.game_type == "solo_clubs":
            color = "c"
        else:
            color = "d"

        superpig_card = color + value

        if self.game.gamerules["dk.superpigs"] == "on_play":
            if uuidify(data["player"]) != self.current_player:
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.pc_wrong_turn")
                return
            if not list(map(lambda x: self.cards[x].card_value, self.hands[player])).count(superpig_card) == 2:
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn",
                                                        "cg:msg.game.dk.invalid_superpigs")
                return
            self.superpigs = [True, player]

        elif self.game.gamerules["dk.superpigs"] == "on_pig":
            if not list(map(lambda x: self.cards[x].card_value, self.hands[player])).count(superpig_card) == 2:
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn",
                                                        "cg:msg.game.dk.invalid_superpigs")
                return

            if "pigs" not in list(map(lambda x: x["data"], self.moves.values()))[-2:]:
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn",
                                                        "cg:msg.game.dk.invalid_superpigs_call")
                return
            self.superpigs = [True, player]

        # Announce the superpig call
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": player.hex,
            "type": "superpigs"
        })

        # Register the move
        self.add_move(player, "announcement", data["type"])

    def handle_call_re(self, event: str, data: Dict):  # Also for Kontra
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_state != "tricks":
            raise GameStateError(
                f"Game state for re or kontra call handling must be 'tricks', not {self.game_state}!")
        if uuidify(data["player"]) != self.current_player:
            self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.pc_wrong_turn")
            return
        if len(self.parties["none"]) != 0:
            self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.re_no_party")
            return

        dtype = data["type"]

        # Check if the re or kontra is called by the correct party
        if dtype == "re" and self.current_player not in self.parties["re"]:
            raise InvalidMoveError("Re can only be called by players of the re party")
        if dtype == "kontra" and self.current_player not in self.parties["kontra"]:
            raise InvalidMoveError("Kontra can only be called by players of the kontra party")

        # Check if the re is not too late or already called
        if dtype == "re":
            if "re" in self.modifiers["re"]:
                raise InvalidMoveError("Re was already called!")

            legal_re = len(self.hands[self.current_player]) >= (
                    self.max_tricks - self.wedding_find_trick)  # Only one card played, wedding_find_trick is 1 by default
            legal_re = legal_re or (  # Answering to a kontra
                    (len(self.hands[self.current_player]) >= (self.max_tricks - 1 - self.wedding_find_trick))
                    and ("kontra" in self.modifiers["kontra"]))
            legal_re = legal_re or (  # Answering to no90
                    (len(self.hands[self.current_player]) >= (self.max_tricks - 2 - self.wedding_find_trick))
                    and ("no90" in self.modifiers["kontra"]))
            legal_re = legal_re or (  # Answering to no60
                    (len(self.hands[self.current_player]) >= (self.max_tricks - 3 - self.wedding_find_trick))
                    and ("no60" in self.modifiers["kontra"]))
            legal_re = legal_re or (  # Answering to no30
                    (len(self.hands[self.current_player]) >= (self.max_tricks - 4 - self.wedding_find_trick))
                    and ("no30" in self.modifiers["kontra"]))
            legal_re = legal_re or (  # Answering to black
                    (len(self.hands[self.current_player]) >= (self.max_tricks - 5 - self.wedding_find_trick))
                    and ("black" in self.modifiers["kontra"]))

            if not legal_re:
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.re_too_late")
                return

            self.modifiers["re"].append("re")
            for p in self.parties["re"]:
                self.game.send_to_user(p, "cg:game.dk.round.change", {
                    "rebtn_lbl": "no90"
                })

            self.update_obvious_party(self.current_player, "re")

        # Check if Kontra is not too late or already called
        elif dtype == "kontra":
            if "kontra" in self.modifiers["kontra"]:
                raise InvalidMoveError("Kontra was already called!")

            legal_kontra = len(self.hands[self.current_player]) >= (
                    self.max_tricks - self.wedding_find_trick)  # Only one card played, wedding_find_trick is 1 by default
            legal_kontra = legal_kontra or (  # Answering to a re
                    (len(self.hands[self.current_player]) >= (self.max_tricks - 1 - self.wedding_find_trick))
                    and ("re" in self.modifiers["re"]))
            legal_kontra = legal_kontra or (  # Answering to no90
                    (len(self.hands[self.current_player]) >= (self.max_tricks - 2 - self.wedding_find_trick))
                    and ("no90" in self.modifiers["re"]))
            legal_kontra = legal_kontra or (  # Answering to no60
                    (len(self.hands[self.current_player]) >= (self.max_tricks - 3 - self.wedding_find_trick))
                    and ("no60" in self.modifiers["re"]))
            legal_kontra = legal_kontra or (  # Answering to no30
                    (len(self.hands[self.current_player]) >= (self.max_tricks - 4 - self.wedding_find_trick))
                    and ("no30" in self.modifiers["re"]))
            legal_kontra = legal_kontra or (  # Answering to black
                    (len(self.hands[self.current_player]) >= (self.max_tricks - 5 - self.wedding_find_trick))
                    and ("black" in self.modifiers["re"]))

            if not legal_kontra:
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.re_too_late")
                return

            self.modifiers["kontra"].append("kontra")
            for p in self.parties["kontra"]:
                self.game.send_to_user(p, "cg:game.dk.round.change", {
                    "rebtn_lbl": "no90"
                })

            self.update_obvious_party(self.current_player, "kontra")

        # Announce decision
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": dtype
        })

        # Register move
        self.add_move(self.current_player, "announcement", dtype)

    def handle_call_denial(self, event: str, data: Dict):  # Also for Kontra
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_state != "tricks":
            raise GameStateError(
                f"Game state for denial call handling must be 'tricks', not {self.game_state}!")
        if uuidify(data["player"]) != self.current_player:
            self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.pc_wrong_turn")
            return

        rtype = data["type"]
        party = ""
        for p, pls in self.parties.items():
            if self.current_player in pls:
                party = p

        # Check if the announcement is legal
        if party == "none":
            raise InvalidMoveError(f"Cannot call {rtype} if you do not belong to a party")

        if rtype == "no90":
            if "no90" in self.modifiers[party]:
                raise InvalidMoveError("No90 has already been called by this party!")
            if party not in self.modifiers[party]:
                raise InvalidMoveError(f"No90 cannot be called by this party without having called {party}!")
            if len(self.hands[self.current_player]) < (self.max_tricks - 1 - self.wedding_find_trick):
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.re_too_late")
                return

        elif rtype == "no60":
            if "no60" in self.modifiers[party]:
                raise InvalidMoveError("No60 has already been called by this party!")
            if "no90" not in self.modifiers[party]:
                raise InvalidMoveError("No60 cannot be called by this party without having called no90!")
            if len(self.hands[self.current_player]) < (self.max_tricks - 2 - self.wedding_find_trick):
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.re_too_late")
                return

        elif rtype == "no30":
            if "no30" in self.modifiers[party]:
                raise InvalidMoveError("No30 has already been called by this party!")
            if "no60" not in self.modifiers[party]:
                raise InvalidMoveError("No30 cannot be called by this party without having called no60!")
            if len(self.hands[self.current_player]) < (self.max_tricks - 3 - self.wedding_find_trick):
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.re_too_late")
                return

        elif rtype == "black":
            if "black" in self.modifiers[party]:
                raise InvalidMoveError("Black has already been called by this party!")
            if "no30" not in self.modifiers[party]:
                raise InvalidMoveError("Black cannot be called by this party without having called no30!")
            if len(self.hands[self.current_player]) < (self.max_tricks - 4 - self.wedding_find_trick):
                self.game.cg.server.send_status_message(uuidify(data["player"]), "warn", "cg:msg.game.dk.re_too_late")
                return

        # Add the denial
        self.modifiers[party].append(rtype)
        for p in self.parties[party]:
            new = "invis"
            if rtype == "no90":
                new = "no60"
            elif rtype == "no60":
                new = "no30"
            elif rtype == "no30":
                new = "black"
            self.game.send_to_user(p, "cg:game.dk.round.change", {
                "rebtn_lbl": new
            })

        # Handle the obvious parties
        obv_party = self.current_player in self.obvious_parties[party]
        self.update_obvious_party(self.current_player, party)

        # Announce decision
        dt = {"announcer": self.current_player.hex, "type": rtype, "data": {"party": party}}
        self.game.send_to_all("cg:game.dk.announce", dt)

        # Register move
        self.add_move(self.current_player, "announcement", f"{rtype}_{party}")

    def handle_black_sow_solo(self, event: str, data: Dict):
        # Check for valid states
        if uuidify(data["player"]) not in self.game.fake_players and \
                self.game.cg.server.users_uuid[uuidify(data["player"])].cur_game != self.game.game_id:
            return
        if self.game_state != "black_sow_solo":
            raise GameStateError(
                f"Game state for black sow solo handling must be 'black_sow_solo', not {self.game_state}!")
        if self.game.gamerules["dk.poverty_consequence"] != "black_sow":
            raise RuleError("Black sow is disabled by the rules!")
        if uuidify(data["player"]) != self.current_player:
            raise WrongPlayerError(f"The player that sent the black sow handling packet is not the current player!")

        # Remember, if the player want's to play a valid solo
        solo_type = data["data"]["type"]
        if solo_type not in self.game.gamerules["dk.solos"]:
            raise RuleError(f"Solo of type {solo_type} is either disabled or does not exist!")

        # Announce decision
        self.game.send_to_all("cg:game.dk.announce", {
            "announcer": self.current_player.hex,
            "type": data["type"],
            "data": data["data"]
        })

        # Register move
        self.add_move(self.current_player, "announcement", "black_sow_" + data["data"]["type"])

        self.game_type = solo_type
        self.game_state = "tricks"

        self.game.send_to_all("cg:game.dk.round.change", {
            "phase": "tricks",
            "game_type": self.game_type,
            "solist": self.current_player.hex
        })

        # Put the players into their parties
        self.parties["re"].add(self.current_player)
        for i in self.players:
            if i != self.current_player:
                self.parties["kontra"].add(i)
        self.parties["none"].clear()

        # Obvious parties
        self.obvious_parties["re"] = self.parties["re"]
        self.obvious_parties["kontra"] = self.parties["kontra"]
        self.obvious_parties["unknown"].clear()

        self.game.send_to_all("cg:game.dk.turn", {
            "current_trick": self.trick_num,
            "total_tricks": self.max_tricks,
            "current_player": self.current_player.hex
        })

    def handle_command(self, event: str, data: Dict):
        packet = f"cg:game.dk.{data['packet']}"

        try:
            player = self.game.fake_players[int(data["player"])]
        except IndexError:
            self.game.cg.info(f"Invalid fake player index: {data['player']}")
            return
        except ValueError:
            if data['player'] == 'p':
                player = self.game.players[0]  # Real player
            elif data['player'] == 'all':
                if packet == "cg:game.dk.ready":
                    for p in self.players:
                        self.game.cg.send_event("cg:game.dk.ready", {
                            "player": p.hex,
                            "type": "ready"
                        })
                    return
                elif packet == "cg:game.dk.q":
                    for p in self.players:
                        self.game.cg.send_event("cg:game.dk.ready", {
                            "player": p.hex,
                            "type": "ready"
                        })
                    for p in self.players:
                        self.game.cg.send_event("cg:game.dk.reservation", {
                            "player": p.hex,
                            "type": "reservation_no"
                        })
                    return
                self.game.cg.info(f"Invalid packet: {packet}")
                return
            elif data['player'] in ['p0', 'p1', 'p2', 'p3']:
                player = self.players[int(data["player"][1])]
            else:
                self.game.cg.info(f"The first argument (fake player) must be an integer, not {data['player']}")
                return

        if packet == "cg:game.dk.reservation_solo":
            self.game.cg.send_event(packet, {
                "player": player.hex,
                "type": data["type"],
                "data": {"type": data["data"]}
            })

        elif packet == "cg:game.dk.black_sow_solo":
            self.game.cg.send_event(packet, {
                "player": player.hex,
                "type": data["type"],
                "data": {"type": data["data"]}
            })

        elif packet == "cg:game.dk.reservation_poverty_pass_card":
            try:
                card_data = [int(i) for i in data["card"]]
            except ValueError:
                self.game.cg.info(f"Invalid cards; cards must be of type int!")
                return

            cards = [card.hex for card in [self.hands[player][i] for i in card_data]]
            self.game.cg.send_event(packet, {
                "player": player.hex,
                "type": data["type"],
                "card": cards
            })

        elif packet == "cg:game.dk.reservation_poverty_accept" and data["type"] == "poverty_return":
            self.game.cg.send_event(packet, {
                "player": player.hex,
                "type": data["type"],
                "data": {"amount": int(data["data"])}
            })

        elif packet == "cg:game.dk.reservation_wedding_clarification_trick":
            self.game.cg.send_event(packet, {
                "player": player.hex,
                "type": data["type"],
                "data": {"trick": data["data"]}
            })

        elif packet == "cg:game.dk.play_card":
            if data["card"] == "-1":
                for i in range(len(self.hands[player])):
                    card = self.hands[player][i]
                    # Check if the card may be played considering the cards that were already played
                    legal_move = False
                    # Yes, if it is the first card of the trick
                    if len(self.current_trick) == 0:
                        legal_move = True
                    # Yes, if it is the same color as the first card of the trick
                    elif self.get_card_color(self.cards[card]) == self.get_card_color(
                            self.cards[self.current_trick[0][1]]):
                        legal_move = True
                    # Yes, if the player has no card of the required color left
                    elif list(map(lambda x: self.get_card_color(self.cards[x]), self.hands[self.current_player])).count(
                            self.get_card_color(self.cards[self.current_trick[0][1]])) == 0:
                        legal_move = True

                    if legal_move:
                        self.game.cg.send_event(packet, {
                            "player": player.hex,
                            "type": data["type"],
                            "card": card.hex
                        })
                        return
            else:
                try:
                    card = self.hands[player][int(data["card"])]
                except ValueError:
                    self.game.cg.info(f"Invalid card; card must be of type int!")
                    return
                except IndexError:
                    self.game.cg.info(f"There are only {len(self.hands[player])} cards left!")
                    return
                self.game.cg.send_event(packet, {
                    "player": player.hex,
                    "type": data["type"],
                    "card": card.hex
                })

        elif packet == "cg:game.dk.autoplay":
            self.do_autoplay()

        else:
            self.game.cg.send_event(packet, {
                "player": player.hex,
                "type": data["type"]
            })

    def do_autoplay(self):
        for i in range(12):
            players = self.players[self.players.index(self.current_player):] + \
                      self.players[:self.players.index(self.current_player)]
            time.sleep(1.5)
            for j in players:
                time.sleep(.5)
                p = 'p' + str(self.players.index(j))
                self.game.cg.send_event("cg:game.dk.command", {
                    "packet": "play_card",
                    "player": p,
                    "type": "play",
                    "card": "-1"
                })

                if self.game_state == "counting":
                    return
