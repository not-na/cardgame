#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  state.py
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
This module contains state classes and custom type definitions.
"""

__all__ = [
    "Card",
    "CardStack", "CardProbabilities", "Move",
    "GlobalGameState", "GameState",
]

import uuid
from dataclasses import dataclass
from typing import Tuple, List, Dict, Any, Optional


class Card(object):
    __slots__ = [
        "card_id",
        "color",
        "value",
        "slot",
    ]

    # The slot of the card is only valid directly from the bot code, it is not simulated!

    def __init__(self, color: str, value: str, uid: uuid.UUID, slot: str):
        self.card_id: uuid.UUID = uid

        self.color = color
        self.value = value

        self.slot = slot

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

    @property
    def eyes(self):
        if self.card_value in ["", "j0", "j1", "j2"]:
            return 0
        elif self.value == "9":
            return 0
        elif self.value == "j":
            return 2
        elif self.value == "q":
            return 3
        elif self.value == "k":
            return 4
        elif self.value == "10":
            return 10
        elif self.value == "a":
            return 11


CardStack = List[Card]
"""
Ordered list of cards.

The order is typically determined by the insertion order of the cards.
"""

CardValueList = List[str]
"""
Ordered list of card values.

Similar to CardStack, but instead of containing card objects, it only contains their values
"""

CardProbabilities = Dict[str, float]
"""
Probability of each card existing in this context, usually a hand.

The dictionary keys are classic shorthands. The values are floats between zero and one.

A value of zero means that a card cannot exist in this context. A value of one means that
a card definitely exists in this context.
"""

Move = Tuple[str, float, Any]
"""
A 3-tuple of ``(type, score, data)`` describing a particular move.

Only valid moves should be generated, though their validity is usually bound to their context.
"""

Party = Optional[str]
"""
String, either ``re`` or ``kontra`` if clear from the bot's perspective, otherwise ``unknown``. None if not even clear
for the concerned player.

Specifies a player's party from the bot's perspective.
"""


@dataclass
class GlobalGameState:
    """
    Data class for storing the global state of the game.

    This class is mostly used to record which cards are held by which player and what
    the teams are.
    """

    game_type: str
    """
    Game type.
    
    Will be updated after all reservations have been handled.
    """

    gamerules: Dict
    """
    Game rules after which is played.
    
    Remain constant during the complete game.
    """

    points: Tuple[int, int, int, int]
    """
    Current points all players would have if the game was ended at this moment in time.
    
    The order of the players follows the player order for the game itself.
    
    The sum of this tuple should always be below or equal to 240.
    """

    card_hands: Tuple[CardStack, ...]
    """
    Cards held by all players.
    
    Note that the values of cards of all other players should always be an empty string
    since we cannot see them.
    """

    card_hands_probabilities: Tuple[CardProbabilities, ...]
    """
    Current probabilities that a player has a certain card.
    
    A value of zero indicates that the player cannot have that card, as all instances of
    it have already been played or are in the hand visible to the bot.
    """

    trick_slots: Tuple[CardStack, ...]
    """
    Cards in the trick slots of all players.
    
    Note that all values should be populated, even though they are technically not visible.
    This is possible since we should see all card in these slots at least once.
    """

    cards_played: Tuple[CardStack, ...]
    """
    Cards already played by each player.
    
    These cards should all have values.
    """

    cards_on_table: CardStack
    """
    Cards currently on the table.
    """

    own_index: int
    """
    Index of the own player.
    
    Should always be between 0 and 3.
    """

    own_party: Party
    """
    Own party.
    
    None if not clear yet and either ``re`` or ``kontra`` otherwise.
    """

    parties: List[Party]
    """
    Current distribution of parties from the bot's perspective.
    """

    current_player: int
    """
    Index of the player whose turn it is.
    
    Should always be between 0 and 3.
    """

    player_missed_colors: Tuple[List[str], ...]
    """
    Tuple storing which colors have been missed by which player.
    
    Important for calculating more accurate probabilities of cards.
    """

    announces: Tuple[List[str], ...]
    """
    List containing all announces that have been made.
    
    Contains one list for re announcements and one for kontra announcements.
    """

    current_trick: int
    """
    Current number of tricks that have been completed.
    """
    # TODO: add more stuff for weddings


@dataclass
class GameState:
    """
    Data Class for storing the state of the game at one specific moment of time.

    Always represents the state just after a player has played a card, but after the trick
    has been collected.
    """

    points: List[int]
    """
    Current points all players would have if the game was ended at this moment in time.
    
    The order of the players follows the player order for the game itself.
    
    The sum of this tuple should always be below or equal to 240.
    """

    card_hands: Tuple[CardProbabilities, ...]
    """
    Current probabilities that a player has a certain card.
    
    A value of zero indicates that the player cannot have that card, as all instances of
    it have already been played or are in the hand visible to the bot.
    """

    own_hand: CardValueList
    """
    All the cards the bot himself possesses.
    """

    current_player: int
    """
    Index of the player whose turn it is.
    
    Always between 0 and 3.
    """

    cards_on_table: CardValueList
    """
    Cards currently on the table.
    """

    trick_depth: int
    """
    Current trick depth.
    
    Stores how many tricks were completed for this state to be reached.
    """

    current_trick: int
    """
    Current number of tricks that have been completed.
    """

    announces: Tuple[List[str], ...]
    """
    List containing all announces that have been made.

    Contains one list for re announcements and one for kontra announcements.
    """

    cards_played: CardValueList
    """
    List containing all cards that have been played since the simulation's creation
    """

    def __copy__(self):
        return GameState(self.points.copy(), tuple(d.copy() for d in self.card_hands), self.own_hand.copy(),
                         self.current_player, self.cards_on_table.copy(),
                         self.trick_depth, self.current_trick, tuple(l.copy() for l in self.announces),
                         self.cards_played.copy())
