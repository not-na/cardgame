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
import uuid
from typing import Dict, List, Any

import cg
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
        return self.color+self.value


class DoppelkopfBot(Bot):
    """
    Base class for all bots for the Doppelkopf game.

    Note that this class is abstract and thus cannot be used directly as a bot.

    This class implements common Doppelkopf-related utilities. These utilities should be
    used by subclasses to simplify bot development.
    """

    BOT_VERSION: int = 1

    def __init__(self, c: cg.CardGame, bot_id: uuid.UUID, name: str):
        super().__init__(c, bot_id, name)

        self.slots: Dict[str, List[Card]] = {}
        # TODO: add more required internal state here

    def play_card(self, card: Card) -> None:
        """
        Plays a single card.

        Only basic plausibility checks are performed.

        Note that no errors will be raised if the card could not be played. This is due
        to the internal architecture. Rather, a status message will be sent.

        :param card: Card to be played, must be in correct slot
        :return: None
        """
        # TODO: implement this via self.send_event...
        # Only checks if it's our turn and if we even have the card
        pass

    def play_poverty_cards(self, cards: List[Card], t: str) -> None:
        """
        Plays the specified cards as a poverty intent.

        :param cards: List of cards to play
        :param t: Intent to use. See proto spec for more details
        :return: None
        """
        # TODO: implement this
        pass

    def initialize(self, data: Dict[str, Any]) -> None:
        # TODO: implement this
        pass

    def get_valid_moves(self) -> List[Card]:
        """
        Returns a list of cards that could be played.

        :return: List of cards
        """
        # TODO: implement this
        pass

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
            raise TypeError(f"Tried to deserialize '{data['type']}' bot of version {data['version']}, but we are at version {cls.BOT_VERSION}!")

        bot = cls(cg, data["uuid"], data["name"])

        # TODO: implement game state restoration

        return bot

    @classmethod
    def supports_game(cls, game: str) -> bool:
        return game == "dk"

    @abc.abstractmethod
    def do_turn(self) -> None:
        """
        Called when a card should be played.

        Only called when the player is actually allowed to play.

        Note that this method is not called in some special circumstances when cards
        should be played, like poverties. These special events are handled by the event
        handlers below.

        :return: None
        """
        pass

    # The event handlers below are not marked as abstract, since that would require all
    # subclasses to implement them, even if they are unneccessary for the bot
    # Thus, we simply define placeholders here

    def on_question(self, data: Dict) -> None:
        pass

    def on_announce(self, data: Dict) -> None:
        pass

    def on_card_transfer(self, data: Dict) -> None:
        pass

    def on_turn(self, data: Dict) -> None:
        pass

    def on_scoreboard(self, data: Dict) -> None:
        pass

    def on_round_change(self, data: Dict) -> None:
        pass

    def on_status_message(self, data: Dict) -> None:
        pass




