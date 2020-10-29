#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  rules.py
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

__all__ = [
    "get_valid_moves", "get_sorted_valid_moves",
    "apply_move",
    "evaluate_state",
]

from typing import List

import cgserver
from .state import *


def get_valid_moves(ggs: GlobalGameState, gs: GameState) -> List[Move]:
    """
    Returns a list of valid moves that could be taken at this point of the game.

    A move in the sense of this function is a 3-tuple of the form ``(type, score, data)``
    where ``type`` is one of ``announce`` or ``card``\\ , ``score`` how good the move is considered to be
    and ``data`` any additional data, like announcement type or card to play.

    Note that the returned list is not sorted yet, it must be manually sorted by the caller.

    It is guaranteed that all moves returned by this function could actually be executed
    (barring wrong guesses as to the cards of other players).

    :param ggs: Global game state
    :param gs: Current game state
    :return: List of valid moves
    """
    # Reservations are not handled here, only announcements that could be made at any time
    # after the actual game has started
    # TODO: implement this
    pass


def get_sorted_valid_moves(ggs: GlobalGameState, gs: GameState) -> List[Move]:
    """
    Same as :py:func:`get_valid_moves()`\\ , but returns a pre-sorted list instead.

    Moves with the highest score appear first.

    Duplicate moves will be removed, provided that all parts of them are exactly equal.

    :param ggs: Global game state
    :param gs: Current game state
    :return: Sorted list of valid moves
    """
    return sorted(set(get_valid_moves(ggs, gs)), key=(lambda m: m[1]), reverse=True)


def apply_move(ggs: GlobalGameState, gs: GameState, move: Move) -> GameState:
    """
    Execute the specified move on the given :py:class:`GameState` and return the resulting
    game state.

    Note that none of the arguments (or their attributes) are modified by this function.
    It has no side-effects.

    Behaviour is undefined if an invalid move is passed.

    :param ggs: Global game state
    :param gs: Game state
    :param move: 3-tuple of ``(type, score, data)``
    :return: Resulting :py:class:`GameState`
    """
    # TODO: implement this
    pass


def evaluate_state(ggs: GlobalGameState, gs: GameState) -> float:
    """
    Evaluate the given game state for a total score.

    The score consists of all points captured by the own team with all points captured
    by the other team (excluding players with unknown affiliation) subtracted.

    A higher score is better.

    :param ggs: Global game state
    :param gs: Game state
    :return: Score of game state
    """
    # TODO: implement this
    pass
