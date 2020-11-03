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
from .. import get_card_color, get_trick_winner, get_card_value
import cg


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
    valid_moves = []

    # For the bot himself
    if gs.current_player == ggs.own_index:
        # Cards
        # The bot plays first
        if len(gs.cards_on_table) == 0:
            for card in gs.own_hand:
                valid_moves.append(('card', 1, card))
        # If the player has to follow suit
        else:
            for card in gs.own_hand:
                if get_card_color(card, ggs.game_type, ggs.gamerules) ==\
                        get_card_color(gs.cards_on_table[0], ggs.game_type, ggs.gamerules):
                    valid_moves.append(('card', 1, card))
        # If the player doesn't have to follow suit
            if len(valid_moves) == 0:
                for card in gs.own_hand:
                    valid_moves.append(('card', 1, card))

        # Announcements
        if ggs.parties[gs.current_player] in ["re", "unknown"]:
            if "re" not in gs.announces[0] and gs.current_trick < 2:
                valid_moves.append(('announce', 0, 're'))
            elif "re" in gs.announces[0]:
                if "no90" not in gs.announces[0] and gs.current_trick < 3:
                    valid_moves.append(('announce', 0, 'no90'))
                elif "no90" in gs.announces[0]:
                    if "no60" not in gs.announces[0] and gs.current_trick < 4:
                        valid_moves.append(('announce', 0, 'no60'))
                    elif "no60" in gs.announces[0]:
                        if "no30" not in gs.announces[0] and gs.current_trick < 5:
                            valid_moves.append(('announce', 0, 'no30'))
                        elif "no30" in gs.announces[0]:
                            if "black" not in gs.announces[0] and gs.current_trick < 6:
                                valid_moves.append(('announce', 0, "black"))

        if ggs.parties[gs.current_player] in ["kontra", "unknown"]:
            if "kontra" not in gs.announces[1] and gs.current_trick < 2:
                valid_moves.append(('announce', 0, 'kontra'))
            elif "re" in gs.announces[1]:
                if "no90" not in gs.announces[1] and gs.current_trick < 3:
                    valid_moves.append(('announce', 0, 'no90'))
                elif "no90" in gs.announces[1]:
                    if "no60" not in gs.announces[1] and gs.current_trick < 4:
                        valid_moves.append(('announce', 0, 'no60'))
                    elif "no60" in gs.announces[1]:
                        if "no30" not in gs.announces[1] and gs.current_trick < 5:
                            valid_moves.append(('announce', 0, 'no30'))
                        elif "no30" in gs.announces[1]:
                            if "black" not in gs.announces[1] and gs.current_trick < 6:
                                valid_moves.append(('announce', 0, "black"))

                                # For other players

    # For other players
    else:
        # Cards
        for card, prob in filter(lambda c: c[1] != 0, gs.card_hands[gs.current_player].items()):
            valid_moves.append(('card', prob, card))

    #cg.c.debug(valid_moves)

    return valid_moves


def get_sorted_valid_moves(ggs: GlobalGameState, gs: GameState) -> List[Move]:
    """
    Same as :py:func:`get_valid_moves()`\\ , but returns a pre-sorted list instead.

    Moves with the highest score appear first.

    Duplicate moves will be removed, provided that all parts of them are exactly equal.

    :param ggs: Global game state
    :param gs: Current game state
    :return: Sorted list of valid moves
    """
    a = sorted(set(get_valid_moves(ggs, gs)), key=(lambda m: m[1]), reverse=True)

    #cg.c.debug(a)
    return a


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
    # TODO: Not supported gamerules: Pigs, superpigs
    new_gs = gs.__copy__()
    if move[0] == "announce":
        if ggs.parties[gs.current_player] == "re":
            new_gs.announces[0].append(move[2])
        elif ggs.parties[gs.current_player] == "kontra":
            new_gs.announces[1].append(move[2])

    elif move[0] == "card":
        # TODO calculate new probabilities
        if gs.current_player == ggs.own_index:
            new_gs.own_hand.remove(move[2])
        new_gs.cards_on_table.append(move[2])
        new_gs.cards_played.append(move[2])

        new_gs.current_player += 1
        new_gs.current_player %= 4

        if len(new_gs.cards_on_table) == 4:
            last_trick = len(new_gs.own_hand) == 0
            trick_winner = get_trick_winner(new_gs.cards_on_table, last_trick, ggs.game_type, ggs.gamerules)

            new_gs.current_player += trick_winner
            new_gs.current_player %= 4

            new_gs.points[new_gs.current_player] += sum(list(map(get_card_value, new_gs.cards_on_table)))

            new_gs.trick_depth += 1
            new_gs.current_trick += 1
            new_gs.cards_on_table = []

    return new_gs


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
    if ggs.own_party is None:
        return gs.points[ggs.own_index]

    total_score = 0
    for player_i, party in ggs.parties:
        if party is not None and not 'unknown':
            if party == ggs.own_party:
                total_score += gs.points[player_i]
            else:
                total_score -= gs.points[player_i]
    return total_score
