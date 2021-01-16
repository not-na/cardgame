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
import time
import uuid
from typing import Any, Union, Tuple, Dict, Callable, List, Optional

import cgserver
import jwt

from . import card
from . import bot

import cg


def register_games(reg: Callable):
    from . import doppelkopf
    reg("doppelkopf", doppelkopf.DoppelkopfGame)


class CGame(object, metaclass=abc.ABCMeta):
    DEV_MODE = cgserver.DEV_MODE and False
    GAMERULES: Dict[str, Dict[str, Any]] = {}
    """
    Dictionary defining all valid gamerules for the given game.
    
    Each entry defines a separate gamerule, with the key used as the name of the rule.
    
    The value must be a dictionary like follows:
    
    ``type`` defines the type of gamerule. This may be one of ``bool``\\ , ``number``\\ ,
    ``select``\\ , ``active`` or ``str``\\ .
    
    ``default`` defines the default value to be used in case the validation fails. It is also
    used as a placeholder if a rule has not been defined.
    
    ``requirements`` is a mapping of gamerule to a list of valid options for that gamerule.
    The given gamerule is only able to be changed if all requirements are fulfilled.
    
    Note that the requirements are not actually verified on the server. They are only used
    to disable options on the client.
    
    Depending on the type, several other fields are expected.
    
    For ``bool`` there are no additional fields.
    
    For ``number``\\ , additional fields include ``min``\\ , ``max`` and ``step``\\ .
    Note that ``min`` and ``max`` are inclusive limits. Steps are counted from ``min``\\ .
    
    For ``select``\\ , there is only the list ``options`` that lists all valid strings.
    Note that these are usually internal names and must be added to translation keys for
    proper display. Note that ``default`` should be on this list.
    
    For ``active``\\ , there is only the list ``options`` that lists all valid options.
    Any number of these can be activated and thus the ``default`` should be a list.
    
    For ``str`` there are two additional fields, ``minlen`` and ``maxlen``\\ . They are
    inclusive limits.
    """

    GAME_VERSION = 1

    def __init__(self, c: cg.CardGame, lobby: uuid.UUID, id: uuid.UUID = None):
        self.cg: cg.CardGame = c

        self.game_id = uuid.uuid4() if id is None else id

        self.creation_time = time.time()

        self.lobby_id = lobby
        self.lobby: cgserver.lobby.Lobby = self.cg.server.lobbies[self.lobby_id]

        self.players: List[uuid.UUID] = self.lobby.users.copy()

        self.register_event_handlers()

        for p in self.players:
            self.cg.server.users_uuid[p].cur_game = self.game_id

        self.gamerules = {}

        for rule, value in self.lobby.gamerules.items():
            if rule not in self.GAMERULES:
                self.cg.warn(f"Gamerules {rule} is not valid for the current game")
            else:
                valid, out = self.check_gamerule(rule, value)
                if not valid:
                    self.cg.warn(f"Gamerule {rule} had an invalid value on game start, resetting it")
                self.gamerules[rule] = out

        for rule in self.GAMERULES:
            if rule not in self.gamerules:
                self.gamerules[rule] = self.GAMERULES[rule]["default"]

    def cancel_game(self, notify=True):
        self.lobby.started = False
        self.lobby.game_data = None

        for p in self.players:
            if isinstance(self.cg.server.users_uuid[p], cgserver.user.BotUser):
                continue

            self.cg.server.users_uuid[p].cur_game = None
            self.cg.server.send_to_user(p, "cg:game.end", {
                "next_state": "lobby",
            })

        if notify:
            self.send_to_all("cg:status.message", {"type": "notice", "message": "cg:msg.game.cancel"})

        self.delete()
        del self.cg.server.games[self.game_id]

    def send_to_all(self, packet: str, data: dict, exclude: Optional[List[uuid.UUID]] = None):
        if exclude is None:
            exclude = []

        for u in self.players:
            if u not in exclude:
                self.send_to_user(u, packet, data)

    def send_to_user(self, user: uuid.UUID, packet: str, data: dict):
        self.cg.server.send_to_user(user, packet, data)

        if packet != "cg:game.dk.card.transfer":
            self.cg.info(f"sent packet {packet} with content {data} to user {user}")

    @abc.abstractmethod
    def start(self):
        pass

    @classmethod
    def check_gamerule(cls, name: str, value: Union[float, bool, str]) -> Tuple[bool, Union[float, bool, str]]:
        return cg.util.validate(value, cls.GAMERULES[name])

    @classmethod
    def check_requirements(cls, name: str, value: Union[float, bool, str], gamerules: Dict):
        for req, valid in cls.GAMERULES[name]["requirements"].items():
            value = gamerules.get(req, cls.GAMERULES[req]["default"])
            if value not in valid:
                return False
        return True

    @classmethod
    @abc.abstractmethod
    def check_playercount(cls, count: int, ignore_devmode=False):
        pass

    @abc.abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize the game to a dictionary.

        Typically used by :py:meth:`adjourn()` to save game state.

        At least the keys ``id``\\ , ``type``\\ , ``creation_time`` and ``players`` should exist.

        ``players`` should be a list of hex'd UUIDs of the players that participated in the game.

        All other keys depend on the game. They should be loadable with :py:meth:`deserialize()`\\ .

        :return:
        """
        pass

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, cg, lobby, data) -> "CGame":
        """
        Creates a working game instance from a stored game.

        :param cg: An instance of :py:class:`CardGame`
        :param lobby: UUID of a lobby containing all players of the game
        :param data: Dictionary returned by calling :py:meth:`serialize()`
        :return:
        """
        pass

    def adjourn(self) -> None:
        """
        Serializes and stores a game on the client.

        Game saves are stored using JSON Web Tokens (JWT) and thus do not require any storage
        on the client.

        :return: None
        """

        self.cg.info(f"Adjourning game {self.game_id.hex}")

        data = self.serialize()

        jwtok = jwt.encode({
            "data": data,
            "iss": self.cg.server.serverid.hex,
            "iat": time.time(),
        }, key=self.cg.server.secret,
        )

        self.send_to_all("cg:game.save", {"game_id": self.game_id.hex, "data": jwtok})

    def register_event_handlers(self):
        pass

    def delete(self):
        # Delete all event handlers belonging to the game
        self.cg.event_manager.del_group(self.game_id)

        # Delete all bot players and their corresponding threads
        for pid in self.players:
            p = self.cg.server.users_uuid[pid]
            if isinstance(p, cgserver.user.BotUser):
                # Stop and delete the bot
                p.bot.stop()
                p.bot.delete()
                # del self.cg.server.users_uuid[pid]
