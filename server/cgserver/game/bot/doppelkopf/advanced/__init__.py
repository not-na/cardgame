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
"""
This package implements an advanced tree-walking probabilistic card-playing algorithm.

It uses the probabilities of cards being in the hands of a specific player to perform a
weighted and limited depth-first-search of the game tree. While the algorithm does not
require other players to play perfectly, it does perform better if they play well.

The algorithm is independent of most global state. It only needs to know which cards are
in the hands of the player it controls and what cards have been played. This information
is usually tracked in a :py:class:`GlobalGameState` instance. If the required data were to
be tracked for a normal (human controlled) player, the bot could also "take over" for the
human player at any time.

It then creates a first :py:class:`GameState` describing the current game state. Based on
the probabilities of a player having a card and whether or not it could be played and some
other factors, it ranks the possible moves of the next player. It then tries out the best
scoring move, creating a new :py:class:`GameState` object from the choice. This is done until
a pre-defined maximum amount of moves have been simulated.

The resulting score is saved and the algorithm backs up one level in the tree. There, it
tests out alternative and slightly less-likely possibilities down to a pre-defined threshold.

The pre-defined parameters are quite important for algorithm efficiency. A too shallow
maximum depth may cause the bot to play valuable cards too early, while a large depth can
exponentially increase the required computations. The branching factor that determines how
many top-ranked probabilities are tested is also important, especially since the scores
are only based on guesses on the available cards.

Some basic optimizations include setting the possibility of cards that a player cannot have
to zero, as this allows the algorithm to skip score-computation for this card entirely.
Since all cards exist only twice, all other players cannot have a card if both have been
played or one has been played and the other is in the hand of the bot. Additionally, since
players are forced to play a matching card if available, playing a mismatched card allows
the bot to rule out an entire suit of cards.
"""
import collections
import math
import time
import uuid
from typing import Dict, Any, List, Optional, Set, Union, Iterable, Tuple

import cg
from cg import CardGame
from cg.util import uuidify

from ... import Bot
from .. import get_card_color
import cgserver.game

from . import rules
from .state import *

import cProfile


class AdvancedDKBot(Bot):
    """
    Base class for advanced Doppelkopf bots.

    Note that while this class implements most of the algorithms neccessary, actual parameters
    must be defined in subclasses.
    """

    BOT_NAME = "dk_advanced"

    BOT_VERSION: int = 1

    MAX_DEPTH: int = 2
    """
    Maximum depth in tricks.
    
    This determines the maximum depth the algorithm will search in units of completed tricks.
    """

    MAX_BRANCHES: int = 4
    """
    Maximum amount of branches to explore per parent node.
    
    If this limit is reached, the algorithm backtracks immediately.
    """

    BRANCH_MIN_THRESHOLD: float = 0.1  # TODO: determine a good value for this
    """
    Minimum threshold for moves to be considered at all.
    
    If all branches/moves with a score higher or equal to the threshold have been explored,
    the algorithm backtracks regardless of the :py:attr:`MAX_BRANCHES` limit.
    
    This limit allows reducing time spent evaluating very unlikely moves.
    """

    ALGO_TIMEOUT: float = 7.0
    """
    Timeout for the card-playing algorithm in seconds.
    
    Note that this timeout is not exact, as some operations cannot be immediately interrupted.
    """

    MIN_TIME: float = 1.0

    NAME_POOL = [
        # Example name schemes:
        # "BotGLaDOS",
        # "Somebody (Bot)",
        # TODO: add more names
        "botJosua",
        "botRuth",
        "botSamuel",
        "botEsra",
        "botNehemia",
        "botEster",
        "botHiob",
        "botJesaja",
        "botJeremia",
        "botEzechiel",
        "botDaniel",
        "botHosea",
        "botJoel",
        "botAmos",
        "botObadja",
        "botJona",
        "botMicha",
        "botNahum",
        "botHabakuk",
        "botZefanja",
        "botHaggai",
        "botZacharia",
        "botMaleachi",
        "botMatthäus",
        "botMarkus",
        "botLukas",
        "botJohannes",
        "botPaulus",
        "botTitus",
        "botPetrus",
        "botJakobus",
        "botJudas"
    ]

    players: List[uuid.UUID]

    slots: Dict[str, List[Card]]
    cards: Dict[uuid.UUID, Card]

    state: str
    game_type: str

    party: Optional[str]
    parties: Dict[str, Set[int]]

    max_tricks: int

    start_hand: CardStack

    ggs: GlobalGameState

    def __init__(self, c: cg.CardGame, bot_id: uuid.UUID, name: str):
        super().__init__(c, bot_id, name)

        self.round_num = 1
        self.players = []

        self.moves = []
        self.state = "loading"
        self.game_type = "normal"

        self.slots = {}

        self.current_re = ""

        self.parties = {"re": set(), "kontra": set()}
        self.modifiers = {"re": [], "kontra": []}

        self.party = None

        self.cache = {}

        self._algo_tstart = 0

    @property
    def own_hand(self) -> CardStack:
        return self.ggs.card_hands[self.ggs.own_index]

    def get_card_color(self, card: Card) -> str:
        #return get_card_color(card, self.game_type, self.gamerules)
        return self.ggs.card_colors[card]

    def update_card_colors(self):
        for c in self.ggs.card_values:
            self.ggs.card_colors[c] = get_card_color(c, self.game_type, self.gamerules)

    def get_card_by_value(self, cardval: str, slot=None) -> Card:
        if slot is None:
            slot = self.cards.values()

        for card in slot:
            if card.card_value == cardval:
                return card
        else:
            raise ValueError(f"Could not find any card with value '{cardval}'")

    def find_cards_in_slot(self, cardval: str, slot: CardStack) -> Iterable[Card]:
        return filter(lambda c: c.card_value == cardval, slot)

    def update_party(self, player: Union[uuid.UUID, int], party: str) -> None:
        pid = self.players.index(player) if isinstance(player, uuid.UUID) else player
        self.parties[party].add(pid)
        self.ggs.parties[pid] = party
        if self.game_type in ["normal", "poverty", "ramsch", "wedding"]:
            counterparty = "re" if party == "kontra" else "kontra"
            if len(self.parties[party]) == 2:
                for p in range(4):
                    if p not in self.parties[party]:
                        self.parties[counterparty].add(p)
        else:
            if len(self.parties["re"]) == 1:
                for p in range(4):
                    if p not in self.parties["re"]:
                        self.parties["kontra"].add(pid)
            elif len(self.parties["kontra"]) == 3:
                for p in range(4):
                    if p not in self.parties["kontra"]:
                        self.parties["re"].add(pid)

    def add_move(self, player: Union[uuid.UUID, int], t: str, data: Any, datadata: Any = None):
        if isinstance(player, int):
            player = self.players[player]

        self.moves.append({uuidify(player): {t: data}})
        if datadata is not None:
            self.moves[-1][uuidify(player)]["data"] = datadata

    def init_round(self, data: Dict[str, Any]):
        self.players = uuidify(data["player_list"])

        self.cards = {}

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

        # Create card deck
        with9 = self.gamerules["dk.without9"]
        with9 = 0 if with9 == "without" else 4 if with9 == "with_four" else 8

        joker = self.gamerules["dk.joker"]
        joker = joker != "None"

        card_values = cgserver.game.card.create_dk_deck(with9=with9, joker=joker)
        card_values = [v.card_value for v in card_values.values()]
        card_values = list(set(card_values))

        self.ggs = GlobalGameState(
            card_hands=([], [], [], []),
            trick_slots=([], [], [], []),
            cards_played=([], [], [], []),
            points=(0, 0, 0, 0),
            player_missed_colors=([], [], [], []),
            cards_on_table=[],
            own_index=self.players.index(self.bot_id),
            own_party=None,
            current_player=0,
            game_type="normal",
            gamerules=self.gamerules,
            parties=[None, None, None, None],
            announces=([], []),
            current_trick=0,
            card_colors={},
            card_values=card_values
        )
        self.update_card_colors()

        self.state = "loading"
        self.game_type = "normal"

        self.current_re = ""

        self.parties = {"re": set(), "kontra": set()}
        self.modifiers = {"re": [], "kontra": []}

        self.party = None

        self.cache.clear()

    def get_current_state(self) -> GameState:
        gs = GameState(
            points=list(self.ggs.points[:]),
            card_hands=({}, {}, {}, {}),
            current_player=self.ggs.own_index,
            cards_on_table=list(map(lambda x: x.card_value, self.ggs.cards_on_table)),
            trick_depth=0,
            own_hand=list(map(lambda x: x.card_value, self.ggs.card_hands[self.ggs.own_index])),
            announces=tuple(l.copy() for l in self.ggs.announces),
            cards_played=[],
            current_trick=self.ggs.current_trick
        )
        self.update_probabilities(
            gs.card_hands,
        )
        return gs

    def announce(self, t: str, data: Any = None):
        # TODO: remove announces that the bot does not need anyway
        self.cg.debug(f"Announcing type {t} with data {data}")
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
                if data is None:
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
            if data is None:
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
            if data is None:
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
            if data is None:
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

    def _get_possible_reservations(self) -> List[str]:
        out = []

        # Check if throwing is possible
        # TODO: maybe announce throwing based on how good the cards are
        if self.gamerules.get("dk.throw", None) in ["throw", "reservation"]:
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
                out.append("throw")

        # Check if wedding is possible
        # TODO: maybe announce wedding based on how good our cards are
        if self.gamerules.get("dk.wedding", None) in ["3_trick", "wish_trick"]:
            if list(map(lambda x: x.card_value, self.own_hand)).count("cq") == 2:
                out.append("wedding")

        # Check if poverty is possible
        if self.gamerules.get("poverty", None) in ["sell", "circulate", "circulate_duty"]:
            trumps = []
            for c in self.own_hand:
                if c.color == "d" or c.value in ["j", "q"] or c.color == "j" or (
                        c.card_value == "h10" and self.gamerules.get("dk.heart10")):
                    trumps.append(c)
            if len(trumps) <= 3:
                out.append("poverty")

        return out

    def do_announce(self) -> None:
        """
        Makes whatever announcement is most appropriate at this time.

        Note that this method should only be used during the initializing phases of the game,
        not during the tricks phases.

        :return: None
        """
        # TODO: merge duplicated code from basic doppelkopf bots
        if self.state == "w_for_ready":
            # Throw if possible, otherwise announce readiness
            if self.gamerules.get("dk.throw", False) == "throw" and "throw" in self._get_possible_reservations():
                self.announce("throw")
            else:
                self.announce("ready")
        elif self.state == "reservation":
            # Announce a wedding or poverty if possible, otherwise reservation_no
            if len(self._get_possible_reservations()) > 0:
                self.announce("reservation_yes")
            else:
                self.announce("reservation_no")
        elif self.state == "solo":
            # TODO: Can the bot play a solo?
            self.announce("solo_no")
        elif self.state == "throw":
            if "throw" in self._get_possible_reservations():
                self.announce("throw_yes")
            else:
                self.announce("throw_no")
        elif self.state == "pigs":
            # Never announce pigs
            # TODO: find out if announcing pigs is mandatory
            self.announce("pigs_no")
        elif self.state == "superpigs":
            # Never announce superpigs
            # TODO: find out if announcing superpigs is mandatory
            self.announce("superpigs_no")
        elif self.state == "poverty":
            # Announce poverty if possible
            if "poverty" in self._get_possible_reservations():
                self.announce("poverty_yes")
            else:
                self.announce("poverty_no")
        elif self.state == "poverty_trump_choice":
            pass  # TODO: check if this can happen at all
        elif self.state == "poverty_accept":
            # Never accept a poverty
            self.announce("poverty_decline")  # TODO: maybe accept one if it is good
        elif self.state == "poverty_return_choice":
            pass  # TODO: check if this can happen at all
        elif self.state == "poverty_return_trumps":
            pass  # TODO: check if this can happen at all
        elif self.state == "wedding":
            # Announce a wedding if possible
            if "wedding" in self._get_possible_reservations():
                self.announce("wedding_yes")
            else:
                self.announce("wedding_no")
        elif self.state in ["tricks", "wedding_clarification_trick"]:
            self.cg.warning(f"do_announce() wrongly called during '{self.state}' phase, ignoring")
        elif self.state == "black_sow_solo":
            # TODO select the best solo
            solo = self.gamerules.get("dk.solos", [""])[0]
            if solo == "":
                self.cg.error(f"No possible solos to call, answer impossible")
            else:
                self.announce("black_sow_solo", {"type": solo})
        else:
            self.cg.error(f"do_announce() called during unsupported phase '{self.state}', ignoring")

    def do_move(self) -> None:
        if False:
            cProfile.runctx(
                "self._do_move()",
                locals=locals(),
                globals=globals(),
                filename=f"profiles/profile_{self.ggs.own_index}_{self.ggs.current_trick}.pyprof",
            )
        else:
            self._do_move()

    def _do_move(self) -> None:
        """
        Evaluate the best possible move and execute it.

        :return: None
        """
        # Normal algorithm doesn't work during initialization phases
        if self.state not in ["tricks", "wedding_clarification_trick"]:
            self.do_announce()
            return

        self._algo_tstart = time.monotonic()

        #self.update_probabilities()

        gs = self.get_current_state()

        # Initialize with worst case
        best_score: Optional[float] = None
        best_move: Optional[Move] = None

        moves = rules.get_sorted_valid_moves(self.ggs, gs)
        if len(moves) == 1:
            # If only one move is available at the top level, take it immediately
            best_move = moves[0]
        else:
            for move in moves:
                # No restrictions on branching at top level, only timeout
                if self._algo_tstart+self.ALGO_TIMEOUT <= time.monotonic():
                    self.cg.warning("Bot algorithm timed out, playing suboptimal move!")
                    break
                ngs = rules.apply_move(self.ggs, gs, move)
                self.update_probabilities(
                    ngs.card_hands,
                    ngs.cards_played,
                    ngs.own_hand,
                )
                score = self._evaluate_node(ngs)
                self.cg.info(f"Score: {score} for move {move}")
                if best_score is None or score > best_score:
                    best_score = score
                    best_move = move

        if best_move is None:
            self.cg.critical("Bot could not find any valid move! Game may hang")
            self.cg.info(f"Moves: {moves}")
            self.cg.info(f"Own hand: {gs.own_hand}")
            return

        t, score, data = best_move

        self.cg.info(f"Took {(time.monotonic()-self._algo_tstart):.4f}s to select move {best_move} for #{self.ggs.own_index}")

        # Wait a minimum amount of time
        tim = self.MIN_TIME-(time.monotonic()-self._algo_tstart)
        if tim > 0:
            time.sleep(tim)

        if t == "card":
            self.play_card(self.get_card_by_value(data, slot=self.own_hand))
        elif t == "announce":
            pass  # TODO: implement this
        else:
            self.cg.critical(f"Invalid move type '{t}', Game will hang!")

    def _evaluate_node(self, gs: GameState) -> float:
        """
        Evaluates a particular game state for the best possible move.

        Runs recursively up to the limit specified in :py:attr:`MAX_DEPTH`\\ .

        :param gs: Current game state
        :return: Best possible move at this game state
        """
        if gs.trick_depth >= self.MAX_DEPTH or gs.trick_depth + self.ggs.current_trick >= self.max_tricks:
            # Reached maximum depth, evaluate state and return it
            return rules.evaluate_state(self.ggs, gs)

        moves = rules.get_sorted_valid_moves(self.ggs, gs)

        best_score: Optional[float] = None

        for i, move in enumerate(moves):
            if i > self.MAX_BRANCHES:
                break
            elif move[1] < self.BRANCH_MIN_THRESHOLD:
                break
            elif self._algo_tstart+self.ALGO_TIMEOUT <= time.monotonic():
                break

            ngs = rules.apply_move(self.ggs, gs, move)
            self.update_probabilities(
                ngs.card_hands,
                ngs.cards_played,
                ngs.own_hand,
            )

            nscore = self._evaluate_node(ngs)

            if best_score is None:
                best_score = nscore
            elif gs.current_player == self.ggs.own_index:
                # We are playing ourselves, maximize
                best_score = min(best_score, nscore)
            elif self.ggs.own_party == self.ggs.parties[gs.current_player]:
                # Teammate is maximizing
                # TODO: properly check if teammate knows we are in the same party
                best_score = min(best_score, nscore)
            else:
                # TODO: figure out the best option for wedding clarification tricks
                best_score = max(best_score, nscore)

        return best_score if best_score is not None else 0

    def play_card(self, card: Card) -> None:
        """
        Plays a single card.

        Only basic plausibility checks are performed.

        Note that no errors will be raised if the card could not be played. This is due
        to the internal architecture. Rather, a status message will be sent.

        :param card: Card to be played, must be in correct slot
        :return: None
        """
        self.cg.debug(f"Bot playing card {card.card_id} with value {card.card_value}")

        if card not in self.own_hand:
            self.cg.warning(f"Bot trying to play card not in own hand")
            # Still try, just in case it is legal

        self.send_event("cg:game.dk.play_card",
                        {
                            "player": self.bot_id.hex,
                            "card": card.card_id.hex
                        },
                        )

    def update_probabilities(self,
                             target: Tuple[CardProbabilities, ...],
                             known: Optional[Iterable[str]] = None,
                             own: Optional[Iterable[str]] = None
                             ) -> None:
        """
        Updates the probabilities stored in the global game state.

        Calculates the probability for each player to have a certain card based on remaining
        not yet seen cards.

        The quality of the probabilities generated here has a direct influence on overall
        algorithm performance.

        :return: None
        """
        #t = time.monotonic_ns()
        c = collections.Counter(c.card_value for c in self.cards.values())
        if known is not None:
            c.update(known)

        if own is not None:
            oc = collections.Counter(own)
        else:
            oc = collections.Counter(c.card_value for c in self.own_hand)

        for card, apcs in c.items():
            # Known cards cannot be played, except when they are in our own hand
            # apcs is the amount of cards with this value that are known
            ascs = oc[card]  # Amount of cards with this value we have

            arcs = 2-apcs  # Amount of remaining cards we do not know about

            # Calculate how many players could have the card
            color = get_card_color(card, self.game_type, self.gamerules)
            pm = len([p for p in range(4) if color in self.ggs.player_missed_colors[p] and p != self.ggs.own_index])
            pr = 3-pm  # Number of players that could have this card

            po = 0
            if arcs == 1:
                po = 1/pr
            elif arcs == 2:
                if pr == 1:
                    po = 1
                elif pr == 2:
                    po = 3/4
                elif pr == 3:
                    po = 5/9

            # TODO: add advanced heuristics
            # TODO: consider CQ and poverty cards

            for p in range(4):
                if p == self.ggs.own_index:
                    target[p][card] = min(1, ascs)  # Probability we have it
                elif color in self.ggs.player_missed_colors[p]:
                    # Player cannot have a card of this color anymore
                    target[p][card] = 0.0
                else:
                    target[p][card] = po

        #t2 = time.monotonic_ns()
        #self.cg.info(f"Card probabilities took {(t2-t)/1000:06.4f}us")

    def serialize(self) -> Dict[str, Any]:
        return {
            # Basic bot data
            "uuid": self.bot_id.hex,
            "name": self.name,
            "type": self.BOT_NAME,
            "version": self.BOT_VERSION,

            # Game state data
            # TODO: implement game state saving
        }

    @classmethod
    def deserialize(cls, c: CardGame, lobby: uuid.UUID, data: Dict[str, Any]) -> "Bot":
        if data["type"] != cls.BOT_NAME:
            # Sanity check
            raise TypeError(f"Tried to deserialize '{data['type']}' bot as a '{cls.BOT_NAME}' bot")
        if data["version"] != cls.BOT_VERSION:
            raise TypeError(
                f"Tried to deserialize '{data['type']}' bot of version {data['version']}, but we are at version {cls.BOT_VERSION}!")
        if not isinstance(data["uuid"], uuid.UUID):
            data["uuid"] = uuidify(data["uuid"])

        bot = cls(c, data["uuid"], data["name"])

        # TODO: implement game state restoration

        return bot

    def initialize(self, data: Dict[str, Any]) -> None:
        self.gamerules = data["gamerules"]

        self.players = uuidify(data["player_list"])

        self.max_tricks = \
            12 if self.gamerules["dk.without9"] == "with_all" else \
            11 if self.gamerules["dk.without9"] == "with_four" else \
            10 if self.gamerules["dk.without9"] == "without" else 0

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

        # TODO: implement more of this
        if packet == "cg:game.start":
            self.initialize(data)
        elif packet == "cg:game.dk.question":
            self.on_question(data)
        elif packet == "cg:game.dk.card.transfer":
            self.on_card_transfer(data)
        elif packet == "cg:game.dk.turn":
            # TODO: store current player and call do_turn() if appropriate
            self.on_turn(data)
        elif packet == "cg:game.dk.scoreboard":
            self.on_scoreboard(data)
        elif packet == "cg:game.dk.round.change":
            self.on_round_change(data)
        elif packet == "cg:game.dk.announce":
            self.on_announce(data)
        elif packet == "cg:status.message":
            # TODO: do some error logging if an error occured
            # TODO: figure out what to do if a bot tries to play an invalid card
            self.on_status_message(data)
        elif packet in [
            "cg:game.save",
            "cg:lobby.change",
            "cg:status.user",
        ]:
            # Ignore these packets
            pass
        # Add more packets here
        else:
            self.cg.warn(f"Bot {self.bot_id} could not handle packet type {packet} with data {data}")

    @classmethod
    def supports_game(cls, game: str) -> bool:
        return game == "doppelkopf"

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
        elif data["type"] == "solo_yes":
            self.ggs.game_type = self.game_type = data["data"]["type"]

            self.update_party(player, "re")

            pid = self.players.index(player)
            for p in range(4):
                if p != pid:
                    self.update_party(p, "kontra")

            self.update_card_colors()
        elif data["type"] == "poverty_yes":
            self.cache["poverty_player"] = player
        elif data["type"] == "poverty_accept":
            self.cache["poverty_acceptant"] = player
        elif data["type"] == "wedding_yes":
            self.cache["wedding_player"] = player
            self.update_party(player, "re")
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

        if data["type"] in ["continue_yes", "adjourn_yes", "cancel_yes", "end_yes"]:
            if self.cache.get("continue_choice", "") != data["type"]:
                if self.cache.get("continue_choice", "") != "":
                    self.announce(self.cache["continue_choice"][:-4] + "_no")
                self.cache["continue_choice"] = data["type"]
                self.announce(self.cache["continue_choice"])

    def on_card_transfer(self, data: Dict) -> None:
        if data["to_slot"] not in self.slots:
            self.slots[data["to_slot"]] = []

        if data["from_slot"] is None:
            if data["card_value"] == "":
                color = value = ""
            else:
                color, value = data["card_value"][0], data["card_value"][1:]
            card = Card(color, value, uuidify(data["card_id"]), data["to_slot"])
            self.cards[card.card_id] = card

            if len(self.slots["stack"]) == self.max_tricks * 4 - 1:
                self.send_event("cg:game.dk.ready_to_deal", {
                    "player": self.bot_id.hex
                })
        else:
            card = self.cards[uuidify(data["card_id"])]
            if data["to_slot"] == "table":
                self.add_move(self.ggs.current_player, "card", card)
                if self.game_type in ["normal", "ramsch"]:
                    if card.card_value == "cq":
                        self.update_party(self.ggs.current_player, "re")
            if data["card_value"] != "":
                card.card_value = data["card_value"]

            if card.slot != data["from_slot"]:
                self.cg.warning(f"Bot received card transfer for card {card.card_value} from slot {data['from_slot']}, but it was in slot {card.slot}")
            card.slot = data["to_slot"]

            self.slots[data["from_slot"]].remove(card)

        # TODO: add missed color detection here

            if data["from_slot"].startswith("hand"):
                fslot = self.ggs.card_hands[int(data["from_slot"][-1])]
                fslot.remove(card)
                tslot = self.ggs.cards_played[int(data["from_slot"][-1])]
                tslot.append(card)
            elif data["from_slot"].startswith("tricks"):
                fslot = self.ggs.trick_slots[int(data["from_slot"][-1])]
                fslot.remove(card)
            elif data["from_slot"] == "table":
                self.ggs.cards_on_table.remove(card)

        if data["to_slot"].startswith("hand"):
            self.cg.debug(data)
            tslot = self.ggs.card_hands[int(data["to_slot"][-1])]
            tslot.append(card)
        elif data["to_slot"].startswith("tricks"):
            tslot = self.ggs.trick_slots[int(data["to_slot"][-1])]
            tslot.append(card)
        elif data["to_slot"] == "table":
            self.ggs.cards_on_table.append(card)

        self.slots[data["to_slot"]].append(card)

        self.cache["pigs_call_self"] = self.cache["superpigs_call_self"] = False

    def on_turn(self, data: Dict) -> None:
        self.ggs.current_player = self.players.index(uuidify(data["current_player"]))
        self.ggs.current_trick = data["current_trick"]

        if self.ggs.current_player == self.ggs.own_index:
            self.do_move()

    def on_scoreboard(self, data: Dict) -> None:
        if "wedding_find_trick" in self.cache:
            pid = self.players.index(uuidify(data["player"]))
            self.update_party(pid, "re")

            for i in range(4):
                if i != pid and i not in self.parties["re"]:
                    self.update_party(i, "kontra")

    def on_round_change(self, data: Dict) -> None:
        if "game_type" in data:
            self.game_type = data["game_type"]

            if data.get("phase", "") != "end":
                if self.game_type == "poverty":
                    self.update_party(self.cache["poverty_player"], "re")
                    self.update_party(self.cache["poverty_acceptant"], "re")
                elif self.game_type == "wedding":
                    self.update_party(self.cache["wedding_player"], "re")
                elif self.game_type not in ["normal", "ramsch", "black_sow"]:
                    self.update_party(uuidify(data["solist"]), "re")

        if "phase" in data:
            if data["phase"] == "loading":
                self.init_round(data)

            elif data["phase"] == "w_for_ready":
                self.state = "w_for_ready"
                self.do_announce()
                self.start_hand = self.own_hand.copy()

            elif data["phase"] == "tricks":
                self.state = "tricks"
                self.update_card_colors()

        if "rebtn_lbl" in data:
            self.current_re = data["rebtn_lbl"]
            if data["rebtn_lbl"] in ["re", "kontra"]:
                self.party = data["rebtn_lbl"]

        if "wedding_find_trick" in data:
            self.cache["wedding_find_trick"] = data["wedding_find_trick"]

    def on_status_message(self, data: Dict) -> None:
        self.cg.warn(f"Bot got status message {data['message']} of type {data['type']} with data {data.get('data', None)}")
