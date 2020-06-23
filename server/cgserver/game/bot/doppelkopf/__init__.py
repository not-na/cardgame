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
import abc
import itertools
import uuid
from typing import Dict, List, Any, Union, Set, Optional

import cg
from cg.util import uuidify
from .. import Bot


class Card(object):
    def __init__(self, card_id: uuid.UUID, slot: str, color: str, value: str):
        self.card_id: uuid.UUID = card_id

        self.color: str = color
        self.value: str = value

        self.slot: str = slot

    @property
    def card_value(self) -> str:
        """
        Returns the value of the card as a string.

        This is simply a property combining :py:attr:`color` and :py:attr:`value`\\ .

        Note that this may be an empty string if the card value is not known.

        :return: Combination of color and value
        """
        return self.color + self.value

    @card_value.setter
    def card_value(self, value):
        if value == "":
            self.color = ""
            self.value = ""
        else:
            self.color = value[0]
            self.value = value[1:]


class DoppelkopfBot(Bot):
    """
    Base class for all bots for the Doppelkopf game.

    Note that this class is abstract and thus cannot be used directly as a bot.

    This class implements common Doppelkopf-related utilities. These utilities should be
    used by subclasses to simplify bot development.
    """

    BOT_VERSION: int = 1

    round_num: int

    players: List[uuid.UUID]
    player_index: int

    slots: Dict[str, List[Card]]

    moves: List[Dict[uuid.UUID, Dict[str, Any]]]
    state: str
    game_type: str

    current_re: str

    max_tricks: int

    party: Optional[str]
    parties: Dict[str, Set[uuid.UUID]]
    modifiers: Dict[str, List[str]]

    current_player: uuid.UUID

    cache: Dict[str, Any]

    def __init__(self, c: cg.CardGame, bot_id: uuid.UUID, name: str):
        super().__init__(c, bot_id, name)

        self.cache = {}

    @property
    def own_hand(self) -> List[Card]:
        return self.slots[f"hand{self.player_index}"]

    def get_hand(self, player: uuid.UUID, trick=False) -> List[Card]:
        key = ("hand" if not trick else "trick") + str(self.players.index(player))
        return self.slots[key]

    def get_card(self, card_id: uuid.UUID) -> Card:
        for card in itertools.chain(*self.slots.values()):
            if card.card_id == card_id:
                return card

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
                if not self.gamerules["dk.solo_shift_h10"]:
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
                if not self.gamerules["dk.solo_shift_h10"]:
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
                if not self.gamerules["dk.heart10"]:
                    return "hearts"
            elif self.game_type in ["solo_spades", "solo_clubs"]:
                if self.gamerules["dk.solo_shift_h10"]:
                    return "hearts"
                if not self.gamerules["dk.heart10"]:
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
                if not self.gamerules["dk.solo_shift_h10"]:
                    return "diamonds"

        if card.card_value == "da":
            if self.game_type in ["solo_hearts", "solo_spades", "solo_clubs", "solo_jack", "solo_queen",
                                  "solo_brothel", "solo_king", "solo_monastery", "solo_noble_brothel", "solo_picture",
                                  "solo_fleshless", "solo_boneless", "solo_pure_hearts", "solo_pure_spades",
                                  "solo_pure_clubs", "solo_10s", "solo_9s"]:
                return "diamonds"

        return "trump"

    def update_party(self, player: uuid.UUID, party: str) -> None:
        self.parties[party].add(player)
        if self.game_type in ["normal", "poverty", "ramsch", "wedding"]:
            counterparty = "re" if party == "kontra" else "kontra"
            if len(self.parties[party]) == 2:
                for p in self.players:
                    if p not in self.parties[party]:
                        self.parties[counterparty].add(p)
        else:
            if len(self.parties["re"]) == 1:
                for p in self.players:
                    if p not in self.parties["re"]:
                        self.parties["kontra"].add(player)
            elif len(self.parties["kontra"]) == 3:
                for p in self.players:
                    if p not in self.parties["kontra"]:
                        self.parties["re"].add(player)

    def select_move(self) -> Optional[Dict[str, Dict]]:
        moves = self.get_valid_moves()
        if len(moves) == 0:
            return

    def do_move(self) -> None:
        move = self.select_move()
        if move is None:
            return

        if move["type"] == "announcement":
            data = None if "data" not in move["data"] else move["data"]["data"]
            self.announce(move["data"]["type"], data)

        elif move["type"] == "play_card":
            self.play_card(move["data"]["card"])

        elif move["type"] == "play_poverty_card":
            self.play_poverty_cards(move["data"]["cards"], move["data"]["type"])

    def announce(self, t: str, data: Any = None):
        if t in ["continue_yes", "continue_no",
                 "adjourn_yes", "adjourn_no",
                 "cancel_yes", "cancel_no",
                 "end_yes", "end_no"]:
            self.send_event(f"cg:game.dk.play.{t}", {
                "player": self.bot_id.hex
            })

        elif t in ["reservation_yes", "reservation_no"]:
            self.send_event("cg:game.dk.reservation", {
                "player": self.bot_id.hex,
                "type": t
            })

        elif t in ["solo_yes", "solo_no"]:
            if t == "solo_yes":
                if "data" is None:
                    raise KeyError(f"cg:game.dk.announce packet with type 'solo_yes' must contain the key 'data'!")
                elif "type" not in data:
                    raise KeyError(
                        f"cg:game.dk.announce packet with type 'solo_yes' must contain 'data' containing key 'type'!")

            self.send_event("cg:game.dk.reservation_solo", {
                "player": self.bot_id.hex,
                "type": t,
                "data": data if t == "solo_yes" else {}
            })

        elif t in ["throw_yes", "throw_no"]:
            self.send_event("cg:game.dk.reservation_throw", {
                "player": self.bot_id.hex,
                "type": t
            })

        elif t in ["pigs_yes", "pigs_no"]:
            self.send_event("cg:game.dk.reservation_pigs", {
                "player": self.bot_id.hex,
                "type": t
            })

        elif t in ["superpigs_yes", "superpigs_no"]:
            self.send_event("cg:game.dk.reservation_superpigs", {
                "player": self.bot_id.hex,
                "type": t
            })

        elif t in ["poverty_yes", "poverty_no"]:
            self.send_event("cg:game.dk.reservation_poverty", {
                "player": self.bot_id.hex,
                "type": t
            })

        elif t in ["poverty_accept", "poverty_decline"]:
            self.send_event("cg:game.dk.reservation_poverty_accept", {
                "player": self.bot_id.hex,
                "type": t
            })

        elif t == "poverty_return":
            if "data" is None:
                raise KeyError(f"cg:game.dk.announce packet with type 'poverty_return' must contain the key 'data'!")
            elif "amount" not in data:
                raise KeyError(
                    f"cg:game.dk.announce packet with type 'poverty_return' must contain 'data' containing key 'amount'!")

            self.send_event("cg:game.dk.reservation_poverty_accept", {
                "player": self.bot_id.hex,
                "type": t,
                "data": data
            })

        elif t in ["wedding_yes", "wedding_no"]:
            self.send_event("cg:game.dk.reservation_wedding", {
                "player": self.bot_id.hex,
                "type": t
            })

        elif t == "wedding_clarification_trick":
            if "data" is None:
                raise KeyError(
                    f"cg:game.dk.announce packet with type 'wedding_clarification_trick' must contain the key 'data'!")
            elif "trick" not in data:
                raise KeyError(
                    f"cg:game.dk.announce packet with type 'wedding_clarification_trick' must contain 'data' containing key 'trick'!")

            self.send_event("cg:game.dk.reservation_wedding_clarification_trick", {
                "player": self.bot_id.hex,
                "type": t,
                "data": data
            })

        elif t == "pigs":
            self.send_event("cg:game.dk.call_pigs", {
                "player": self.bot_id.hex,
                "type": t
            })

        elif t == "superpigs":
            self.send_event("cg:game.dk.call_superpigs", {
                "player": self.bot_id.hex,
                "type": t
            })

        elif t in ["re", "kontra"]:
            self.send_event("cg:game.dk.call_re", {
                "player": self.bot_id.hex,
                "type": t
            })

        elif t in ["no90", "no60", "no30", "black"]:
            self.send_event("cg:game.dk.call_denial", {
                "player": self.bot_id.hex,
                "type": t
            })

        elif t == "black_sow_solo":
            if "data" is None:
                raise KeyError(f"cg:game.dk.announce packet with type 'solo_yes' must contain the key 'data'!")
            elif "type" not in data:
                raise KeyError(
                    f"cg:game.dk.announce packet with type 'solo_yes' must contain 'data' containing key 'type'!")

            self.send_event("cg:game.dk.black_sow_solo", {
                "player": self.bot_id.hex,
                "type": t,
                "data": data
            })

        elif t == "throw":
            self.send_event("cg:game.dk.throw", {
                "player": self.bot_id.hex,
                "type": t,
            })

        elif t == "ready":
            self.send_event("cg:game.dk.ready", {
                "player": self.bot_id.hex,
                "type": t,
            })

    def play_card(self, card: Card) -> None:
        """
        Plays a single card.

        Only basic plausibility checks are performed.

        Note that no errors will be raised if the card could not be played. This is due
        to the internal architecture. Rather, a status message will be sent.

        :param card: Card to be played, must be in correct slot
        :return: None
        """
        self.send_event("cg:game.dk.play_card", {
            "player": self.bot_id.hex,
            "card": card.card_id.hex
        })

    def play_poverty_cards(self, cards: List[Card], t: str) -> None:
        """
        Plays the specified cards as a poverty intent.

        :param cards: List of cards to play
        :param t: Intent to use. See proto spec for more details
        :return: None
        """
        self.send_event("cg:game.dk.reservation_poverty_pass_card", {
            "player": self.bot_id.hex,
            "type": t,
            "card": [card.card_id.hex for card in cards]
        })
        pass

    def initialize(self, data: Dict[str, Any]) -> None:
        self.init_game(data)

    def init_game(self, data: Dict[str, Any]) -> None:
        self.gamerules = data["gamerules"]

        self.max_tricks = 12 if self.gamerules["dk.without9"] == "with_all" else \
            11 if self.gamerules["dk.without9"] == "with_four" else \
                10 if self.gamerules["dk.without9"] == "without" else 0

    def init_round(self, data: Dict[str, Any]):
        self.player_index = data["player_list"].index(self.bot_id)

        self.slots = {
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
        self.moves = []

        self.state = "loading"
        self.game_type = "normal"

        self.current_re = ""

        self.parties = {"re": set(), "kontra": set()}
        self.modifiers = {"re": [], "kontra": []}

        self.party = None

        self.cache.clear()

    def get_valid_moves(self) -> List[Dict[str, Dict]]:
        """
        Returns a list of cards that could be played.

        :return: List of cards
        """
        moves = []

        if self.state == "w_for_ready":
            moves.append(
                {
                    "type": "announcement",
                    "data": {"type": "ready"}
                }
            )

            if self.gamerules.get("dk.throw", False):
                legal_throw = False
                # Check, whether throwing is justified
                nines = []
                kings = []
                fulls = []
                high_trumps = []
                dj = False

                player_hand = self.own_hand
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

                if "5_9" in self.gamerules["dk.throw_cases"]:
                    legal_throw = legal_throw or len(nines) >= 5
                if "5_k" in self.gamerules["dk.throw_cases"]:
                    legal_throw = legal_throw or len(kings) >= 5
                if "4_9+4_k" in self.gamerules["dk.throw_cases"]:
                    legal_throw = legal_throw or len(nines) >= 4 and len(kings) >= 4
                if "9_all_c" in self.gamerules["dk.throw_cases"]:
                    legal_throw = legal_throw or len(set(list(map(lambda x: x.color, nines)))) == 4
                if "k_all_c" in self.gamerules["dk.throw_cases"]:
                    legal_throw = legal_throw or len(set(list(map(lambda x: x.color, kings)))) == 4
                if "7full" in self.gamerules["dk.throw_cases"]:
                    legal_throw = legal_throw or len(fulls) >= 7
                if "t<hj" in self.gamerules["dk.throw_cases"]:
                    legal_throw = legal_throw or len(high_trumps) == 0
                if "t<dj" in self.gamerules["dk.throw_cases"]:
                    legal_throw = legal_throw or len(high_trumps) == 0 and not dj

                if legal_throw:
                    moves.append(
                        {
                            "type": "announcement",
                            "data": {"type": "throw"}
                        }
                    )

        elif self.state == "reservation":
            moves.append(
                {
                    "type": "announcement",
                    "data": {"type": "reservation_yes"}
                }
            )
            moves.append(
                {
                    "type": "announcement",
                    "data": {"type": "reservation_no"}
                }
            )

        elif self.state == "solo":
            moves.append(
                {
                    "type": "announcement",
                    "data": {"type": "solo_no"}
                }
            )
            for solo in self.gamerules.get("dk.solos", []):
                moves.append(
                    {
                        "type": "announcement",
                        "data": {
                            "type": "solo_yes",
                            "data": {"type": solo}
                        }
                    }
                )

        elif self.state == "pigs":
            moves.append(
                {
                    "type": "announcement",
                    "data": {"type": "pigs_no"}
                }
            )

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

            if list(map(lambda x: x.card_value, self.own_hand)).count(fox_card) == 2:
                moves.append(
                    {
                        "type": "announcement",
                        "data": {"type": "pigs_yes"}
                    }
                )

        elif self.state == "superpigs":
            moves.append(
                {
                    "type": "announcement",
                    "data": {"type": "superpigs_no"}
                }
            )

            if self.game_type == "solo_hearts":
                superpig_color = "h"
            elif self.game_type == "solo_spades":
                superpig_color = "s"
            elif self.game_type == "solo_clubs":
                superpig_color = "c"
            elif self.game_type in ["normal", "silent_wedding", "wedding", "poverty", "ramsch", "ramsch_sw",
                                    "solo_diamonds", "solo_null", "black_sow"]:
                superpig_color = "d"
            else:
                superpig_color = ""

            if self.gamerules.get("dk.without9", "with_all") == "with_all":
                superpig_value = "9"
            else:
                superpig_value = "k"

            superpig_card = superpig_color + superpig_value

            if list(map(lambda x: x.card_value, self.own_hand)).count(superpig_card) == 2:
                moves.append(
                    {
                        "type": "announcement",
                        "data": {"type": "superpigs_yes"}
                    }
                )

        elif self.state == "poverty":
            moves.append(
                {
                    "type": "announcement",
                    "data": {"type": "poverty_no"}
                }
            )

            trumps = []
            for c in self.own_hand:

                if c.color == "d" or c.value in ["j", "q"] or c.color == "j" or (
                        c.card_value == "h10" and self.gamerules.get("dk.heart10")):
                    trumps.append(c)
            if len(trumps) <= 3:
                moves.append(
                    {
                        "type": "announcement",
                        "data": {"type": "poverty_yes"}
                    }
                )

        elif self.state == "poverty_trump_choice":
            trumps = []
            for c in self.own_hand:
                if c.color == "d" or c.value in ["j", "q"] or c.color == "j" or (
                        c.card_value == "h10" and self.gamerules.get("dk.heart10")):
                    trumps.append(c)

            if len(trumps) == 3:
                moves.append(
                    {
                        "type": "play_poverty_card",
                        "data": {
                            "cards": [c.card_id.hex for c in trumps],
                            "type": "pass"
                        }
                    }
                )

            elif len(trumps) < 3:
                hand = self.own_hand.copy()
                for i in trumps:
                    hand.remove(i)

                permutations = list(itertools.combinations(hand, 3 - len(trumps)))

                for i in permutations:
                    moves.append(
                        {
                            "type": "play_poverty_card",
                            "data": {
                                "cards": [c.card_id.hex for c in trumps] + [b.card_id.hex for b in i],
                                "type": "pass"
                            }
                        }
                    )

        elif self.state == "poverty_accept":
            moves.append(
                {
                    "type": "announcement",
                    "data": {"type": "poverty_decline"}
                }
            )
            moves.append(
                {
                    "type": "announcement",
                    "data": {"type": "poverty_accept"}
                }
            )

        elif self.state == "poverty_return_choice":
            permutations = list(itertools.combinations(self.own_hand, 3))

            for i in permutations:
                moves.append(
                    {
                        "type": "play_poverty_card",
                        "data": {
                            "cards": [b.card_id.hex for b in i],
                            "type": "return"
                        }
                    }
                )

        elif self.state == "poverty_return_trumps":
            cs = self.moves[-1][self.bot_id]["data"]["cards"]
            cards = []
            for card in itertools.chain(*self.slots.values()):
                if card.card_id.hex in cs:
                    cards.append(card)

            trumps = 0
            for c in cards:
                if c.color == "d" or c.value in ["j", "q"] or c.color == "j" or (
                        c.card_value == "h10" and self.gamerules.get("dk.heart10")):
                    trumps += 1

            moves.append(
                {
                    "type": "announcement",
                    "data": {
                        "type": "poverty_return_trumps",
                        "data": {"amount": trumps}
                    }
                }
            )

        elif self.state == "wedding":
            moves.append(
                {
                    "type": "announcement",
                    "data": {"type": "wedding_no"}
                }
            )

            if list(map(lambda x: x.card_value, self.own_hand)).count("cq") == 2:
                moves.append(
                    {
                        "type": "announcement",
                        "data": {"type": "wedding_yes"}
                    }
                )

        elif self.state == "wedding_clarification_trick":
            moves.append(
                {
                    "type": "announcement",
                    "data": {
                        "type": "wedding_clarification_trick",
                        "trick": "foreign"
                    }
                }
            )
            moves.append(
                {
                    "type": "announcement",
                    "data": {
                        "type": "wedding_clarification_trick",
                        "trick": "trump"
                    }
                }
            )
            moves.append(
                {
                    "type": "announcement",
                    "data": {
                        "type": "wedding_clarification_trick",
                        "trick": "miss"
                    }
                }
            )
            moves.append(
                {
                    "type": "announcement",
                    "data": {
                        "type": "wedding_clarification_trick",
                        "trick": "clubs"
                    }
                }
            )
            moves.append(
                {
                    "type": "announcement",
                    "data": {
                        "type": "wedding_clarification_trick",
                        "trick": "spades"
                    }
                }
            )
            moves.append(
                {
                    "type": "announcement",
                    "data": {
                        "type": "wedding_clarification_trick",
                        "trick": "hearts"
                    }
                }
            )
            moves.append(
                {
                    "type": "announcement",
                    "data": {
                        "type": "wedding_clarification_trick",
                        "trick": "diamonds"
                    }
                }
            )

        elif self.state == "tricks":
            if self.current_player == self.bot_id:
                # Play a card
                for card in self.own_hand:
                    legal_move = False
                    if len(self.slots["table"]) == 0:
                        legal_move = True
                    elif self.get_card_color(card) == self.get_card_color(self.slots["table"][0]):
                        legal_move = True
                    elif list(map(lambda x: self.get_card_color(x), self.own_hand)).count(
                            self.get_card_color(self.slots["table"][0])) == 0:
                        legal_move = True

                    if self.cache.get("pigs_call_self", False):
                        if self.game_type == "solo_hearts":
                            pig_card = "ha"
                        elif self.game_type == "solo_spades":
                            pig_card = "sa"
                        elif self.game_type == "solo_clubs":
                            pig_card = "ca"
                        else:
                            pig_card = "da"

                        legal_move = legal_move and card.card_value == pig_card

                    if self.cache.get("superpigs_call_self", False):
                        if self.gamerules["dk.without9"] == "with_all":
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

                        legal_move = legal_move and card.card_value == superpig_card

                    if legal_move:
                        moves.append(
                            {
                                "type": "play_card",
                                "data": {"card": card}
                            }
                        )

                # Call re
                wedding_find_trick = self.cache.get("wedding_find_trick", 0)
                if self.current_re == "re":
                    legal_re = len(self.own_hand) >= (
                            self.max_tricks - wedding_find_trick)  # Only one card played, wedding_find_trick is 1 by default
                    legal_re = legal_re or (  # Answering to a kontra
                            (len(self.own_hand) >= (self.max_tricks - 1 - wedding_find_trick))
                            and ("kontra" in self.modifiers["kontra"]))
                    legal_re = legal_re or (  # Answering to no90
                            (len(self.own_hand) >= (self.max_tricks - 2 - wedding_find_trick))
                            and ("no90" in self.modifiers["kontra"]))
                    legal_re = legal_re or (  # Answering to no60
                            (len(self.own_hand) >= (self.max_tricks - 3 - wedding_find_trick))
                            and ("no60" in self.modifiers["kontra"]))
                    legal_re = legal_re or (  # Answering to no30
                            (len(self.own_hand) >= (self.max_tricks - 4 - wedding_find_trick))
                            and ("no30" in self.modifiers["kontra"]))
                    legal_re = legal_re or (  # Answering to black
                            (len(self.own_hand) >= (self.max_tricks - 5 - wedding_find_trick))
                            and ("black" in self.modifiers["kontra"]))
                    if legal_re:
                        moves.append(
                            {
                                "type": "announcement",
                                "data": {"type": "re"}
                            }
                        )

                elif self.current_re == "kontra":
                    legal_kontra = len(self.own_hand) >= (
                            self.max_tricks - wedding_find_trick)  # Only one card played, wedding_find_trick is 1 by default
                    legal_kontra = legal_kontra or (  # Answering to a kontra
                            (len(self.own_hand) >= (self.max_tricks - 1 - wedding_find_trick))
                            and ("re" in self.modifiers["re"]))
                    legal_kontra = legal_kontra or (  # Answering to no90
                            (len(self.own_hand) >= (self.max_tricks - 2 - wedding_find_trick))
                            and ("no90" in self.modifiers["re"]))
                    legal_kontra = legal_kontra or (  # Answering to no60
                            (len(self.own_hand) >= (self.max_tricks - 3 - wedding_find_trick))
                            and ("no60" in self.modifiers["re"]))
                    legal_kontra = legal_kontra or (  # Answering to no30
                            (len(self.own_hand) >= (self.max_tricks - 4 - wedding_find_trick))
                            and ("no30" in self.modifiers["re"]))
                    legal_kontra = legal_kontra or (  # Answering to black
                            (len(self.own_hand) >= (self.max_tricks - 5 - wedding_find_trick))
                            and ("black" in self.modifiers["re"]))
                    if legal_kontra:
                        moves.append(
                            {
                                "type": "announcement",
                                "data": {"type": "kontra"}
                            }
                        )

                elif self.current_re == "no90":
                    if len(self.own_hand) >= (self.max_tricks - 1 - wedding_find_trick):
                        moves.append(
                            {
                                "type": "announcement",
                                "data": {"type": "no90"}
                            }
                        )

                elif self.current_re == "no60":
                    if len(self.own_hand) >= (self.max_tricks - 2 - wedding_find_trick):
                        moves.append(
                            {
                                "type": "announcement",
                                "data": {"type": "no60"}
                            }
                        )

                elif self.current_re == "no30":
                    if len(self.own_hand) >= (self.max_tricks - 3 - wedding_find_trick):
                        moves.append(
                            {
                                "type": "announcement",
                                "data": {"type": "no30"}
                            }
                        )

                elif self.current_re == "black":
                    if len(self.own_hand) >= (self.max_tricks - 4 - wedding_find_trick):
                        moves.append(
                            {
                                "type": "announcement",
                                "data": {"type": "black"}
                            }
                        )

                # Call pigs
                if self.gamerules["dk.pigs"] not in ["None", "two_reservation"]:
                    if not self.cache.get("pigs", False):
                        # Find out, which cards are the pigs in this round
                        if self.game_type == "solo_hearts":
                            pig_card = "ha"
                        elif self.game_type == "solo_spades":
                            pig_card = "sa"
                        elif self.game_type == "solo_clubs":
                            pig_card = "ca"
                        else:
                            pig_card = "da"

                        legal_pigs = False
                        if len(self.slots["table"]) == 0:
                            legal_pigs = True
                        elif self.get_card_color(Card(
                                uuid.uuid4(), "", pig_card[0], pig_card[1])) == self.get_card_color(
                            self.slots["table"][0]):
                            legal_pigs = True
                        elif list(map(lambda x: self.get_card_color(x), self.own_hand)).count(
                                self.get_card_color(self.slots["table"][0])) == 0:
                            legal_pigs = True

                        if legal_pigs:
                            if self.gamerules["dk.pigs"] in ["two_on_play", "one_first"]:
                                # The player has two pigs on his hand
                                if list(map(lambda x: x.card_value, self.own_hand)).count(pig_card) == 2:
                                    moves.append(
                                        {
                                            "type": "announcement",
                                            "data": {"type": "pigs"}
                                        }
                                    )

                            elif self.gamerules["dk.pigs"] == "one_on_play":
                                # The player had two pigs at the start of the game and still one left
                                if list(map(lambda x: x.card_value, self.start_hand)).count(pig_card) == 2:
                                    if list(map(lambda x: x.card_value, self.own_hand)).count(pig_card) > 0:
                                        moves.append(
                                            {
                                                "type": "announcement",
                                                "data": {"type": "pigs"}
                                            }
                                        )

                            elif self.gamerules["dk.pigs"] == "one_on_fox":
                                # The player had two pigs at the start of the game and still one left
                                if (list(map(lambda x: x.card_value, self.start_hand)).count(pig_card) == 2 and
                                        list(map(lambda x: x.card_value, self.own_hand)).count(pig_card) == 1):
                                    if self.party is not None:
                                        for card in itertools.chain(
                                                *[self.get_hand(p, True) for p in self.parties[self.party]]):
                                            if card.card_value == pig_card:
                                                moves.append(
                                                    {
                                                        "type": "announcement",
                                                        "data": {"type": "pigs"}
                                                    }
                                                )

            # Superpigs
            if self.gamerules["dk.superpigs"] not in ["None", "reservation"]:
                if self.cache.get("pigs", False) and not self.cache.get("superpigs", False):
                    if self.gamerules["dk.without9"] == "with_all":
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

                    if self.gamerules["dk.superpigs"] == "on_play":
                        if self.current_player == self.bot_id:
                            if list(map(lambda x: x.card_value, self.own_hand)).count(superpig_card) == 2:
                                legal_superpigs = False
                                if len(self.slots["table"]) == 0:
                                    legal_superpigs = True
                                elif self.get_card_color(Card(uuid.uuid4(), "", superpig_card[0], superpig_card[1])
                                                         ) == self.get_card_color(self.slots["table"][0]):
                                    legal_superpigs = True
                                elif list(map(lambda x: self.get_card_color(x), self.own_hand)).count(
                                        self.get_card_color(self.slots["table"][0])) == 0:
                                    legal_superpigs = True

                                if legal_superpigs:
                                    moves.append(
                                        {
                                            "type": "announcement",
                                            "data": {"type": "superpigs"}
                                        }
                                    )

                    elif self.gamerules["dk.superpigs"] == "on_pig":
                        if list(map(lambda x: x.card_value, self.own_hand)).count(superpig_card) == 2:
                            if "pigs" in list(map(lambda x: list(x.values())[0].get("announcement", "None"),
                                                  self.moves))[-2:]:
                                moves.append(
                                    {
                                        "type": "announcement",
                                        "data": {"type": "superpigs"}
                                    }
                                )

            if list(map(lambda x: x["type"], moves)).count("play_card") == 0:
                moves.insert(0, None)

        return moves

    def add_move(self, player: str, type: str, data: Any, datadata: Any = None):
        self.moves.append({uuidify(player): {type: data}})
        if datadata is not None:
            self.moves[-1][uuidify(player)]["data"] = datadata

    def on_packet(self, packet: str, data: Dict) -> None:
        """
        Calls the appropriate handlers and updates internal state.

        :param packet: Name of the received packet
        :param data: Packet-specific data in dictionary form
        :return: None
        """
        # For each packet, the structure is as follows:
        # Update any internal state that is changed by the packet
        # Similar to a real client
        # Then call the appropriate handler with the packet data

        if packet == "cg:game.start":
            self.initialize(data)
        elif packet == "cg:game.dk.question":
            self.on_question(data)
        elif packet == "cg:game.dk.card.transfer":
            # TODO: transfer card in self.slots
            self.on_card_transfer(data)
        elif packet == "cg:game.dk.turn":
            # TODO: store current player and call do_turn() if appropriate
            self.on_turn(data)
        elif packet == "cg:game.dk.scoreboard":
            self.on_scoreboard(data)
        elif packet == "cg:game.dk.round.change":
            self.on_round_change(data)
        elif packet == "cg:status.message":
            # TODO: do some error logging if an error occured
            # TODO: figure out what to do if a bot tries to play an invalid card
            self.on_status_message(data)
        # Add more packets here
        else:
            self.cg.debug(f"Bot {self.bot_id} could not handle packet type {packet} with data {data}")

    def serialize(self) -> Dict[str, Any]:
        return {
            # Basic bot data
            "uuid": self.bot_id.hex,
            "name": self.name,
            "type": self.BOT_NAME,

            # Game state data
            # TODO: implement game state saving
        }

    @classmethod
    def deserialize(cls, cg, lobby, data) -> "DoppelkopfBot":
        if data["type"] != cls.BOT_NAME:
            # Sanity check
            raise TypeError(f"Tried to deserialize '{data['type']}' bot as a '{cls.BOT_NAME}' bot")
        if data["version"] != cls.BOT_VERSION:
            raise TypeError(
                f"Tried to deserialize '{data['type']}' bot of version {data['version']}, but we are at version {cls.BOT_VERSION}!")

        bot = cls(cg, data["uuid"], data["name"])

        # TODO: implement game state restoration

        return bot

    @classmethod
    def supports_game(cls, game: str) -> bool:
        return game == "dk"

    # The event handlers below are not marked as abstract, since that would require all
    # subclasses to implement them, even if they are unneccessary for the bot
    # Thus, we simply define placeholders here

    def on_question(self, data: Dict) -> None:
        if data["target"] == self.bot_id.hex:
            self.state = data["type"]
            self.do_move()

    def on_announce(self, data: Dict) -> None:
        player = uuidify(data["announcer"])
        if "data" in data:
            self.add_move(player, "announcement", data["type"], data["data"])
        else:
            self.add_move(player, "announcement", data["type"])

        if data["type"] == "re":
            self.update_party(player, "re")
            self.modifiers["re"].append("re")
            if player == self.bot_id:
                self.do_move()
        elif data["type"] == "kontra":
            self.parties["kontra"].add(player)
            self.update_party(player, "kontra")
            self.modifiers["kontra"].append("kontra")
            if player == self.bot_id:
                self.do_move()
        elif data["type"] in ["no90", "no60", "no30", "black"]:
            self.update_party(player, data["data"]["party"])
            self.modifiers[data["data"]["party"]].append(data["type"])
            if player == self.bot_id:
                self.do_move()

        elif data["type"] == "poverty_yes":
            self.cache["poverty_player"] = player
        elif data["type"] == "poverty_accept":
            self.cache["poverty_acceptant"] = player
        elif data["type"] == "wedding_yes":
            self.cache["wedding_player"] = player
            if self.gamerules["dk.wedding"] == "3_trick":
                self.cache["wedding_clarification_trick"] = "foreign"
        elif data["type"] == "wedding_clarification_trick":
            self.cache["wedding_clarification_trick"] = data["data"]["trick"]

        elif data["type"] in ["pigs_yes", "pigs"]:
            self.cache["pigs"] = True
            if data["type"] == "pigs" and player == self.bot_id:
                self.cache["pigs_call_self"] = True
                self.do_move()
        elif data["type"] == ["superpigs_yes", "superpigs"]:
            self.cache["superpigs"] = True
            if data["type"] == "superpigs" and player == self.bot_id:
                self.cache["superpigs_call_self"] = self.gamerules["dk.superpigs"] == "on_play"
                self.do_move()

        elif data["type"] in ["continue_yes", "adjourn_yes", "cancel_yes", "end_yes"]:
            if self.cache.get("continue_choice", "") != data["type"]:
                if self.cache.get("continue_choice", "") != "":
                    self.announce(self.cache["continue_choice"][:-4] + "_no")
                self.cache["continue_choice"] = data["type"]
                self.announce(self.cache["continue_choice"])

    def on_card_transfer(self, data: Dict) -> None:
        if data["from_slot"] is None:
            if data["card_value"] == "":
                color = value = ""
            else:
                color, value = data["card_value"][0], data["card_value"][1:]
            card = Card(uuidify(data["card_id"]), data["to_slot"], color, value)
        else:
            card = self.get_card(uuidify(data["card_id"]))
            if data["to_slot"] == "table":
                self.add_move(data["player"], "card", card)
                if self.game_type in ["normal", "ramsch"]:
                    if card.card_value == "cq":
                        self.update_party(self.current_player, "re")
            if data["card_value"] != "":
                card.card_value = data["card_value"]

        self.slots[data["from_slot"]].remove(card)
        self.slots[data["to_slot"]].append(card)

        self.cache["pigs_call_self"] = self.cache["superpigs_call_self"] = False

    def on_turn(self, data: Dict) -> None:
        self.current_player = uuidify(data["current_player"])
        if self.current_player == self.bot_id:
            self.do_move()

    def on_scoreboard(self, data: Dict) -> None:
        pass

    def on_round_change(self, data: Dict) -> None:
        if "game_type" in data:
            self.game_type = data["game_type"]

            if self.game_type == "poverty":
                self.update_party(self.cache["poverty_player"], "re")
                self.update_party(self.cache["poverty_acceptant"], "re")
            elif self.game_type == "wedding":
                self.update_party(self.cache["wedding_player"], "re")
            elif self.game_type not in ["normal", "ramsch"]:
                self.update_party(uuidify(data["solist"]), "re")

        if "phase" in data:
            if data["phase"] == "loading":
                self.init_round(data)

            elif data["phase"] == "w_for_ready":
                self.state = "w_for_ready"
                self.do_move()
                self.start_hand = self.own_hand.copy()

            elif data["phase"] == "tricks":
                self.state = "tricks"

        if "rebtn_lbl" in data:
            self.current_re = data["rebtn_lbl"]
            if data["rebtn_lbl"] in ["re", "kontra"]:
                self.party = data["rebtn_lbl"]

        if "wedding_find_trick" in data:
            self.cache["wedding_find_trick"] = data["wedding_find_trick"]

    def on_status_message(self, data: Dict) -> None:
        pass
