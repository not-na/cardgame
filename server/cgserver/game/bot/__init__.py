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
import collections
import queue
import random
import threading
import uuid
from typing import Dict, Any, Optional, Callable, List, Type

import cg


def register_bots(reg: Callable):
    from . import doppelkopf
    from .doppelkopf import dumb  # TODO: make this better
    from .doppelkopf import advanced
    reg("dk_dumb", doppelkopf.dumb.DumbDoppelkopfBot)
    reg("dk_advanced", doppelkopf.advanced.AdvancedDKBot)


class Bot(object, metaclass=abc.ABCMeta):
    """
    Base class for all :term:`bots <bot>`\\ .

    This class implements common functionality shared by all bots such as a separate worker
    thread. A separate thread allows the bot code to take its time when deciding on a move
    without compromising on response time for other users.

    To make full use of the built-in multithreading and prevent race conditions, bot code
    should only ever use methods defined in this class or its subclasses and not access
    the :py:attr:`cg` attribute directly. Event registration and sending are possible
    through the appropriate proxies that handle the cross-thread communication.

    Note that bots are instantiated the moment they are added to a lobby. A single bot
    object will persist over several rounds and sometimes even games. This should be
    taken into consideration when designing the architecture of a bot.

    Note that this class is partially abstract and must be subclassed to be useful.
    """

    bot_id: uuid.UUID
    """
    :term:`UUID` of the bot.
    
    This is also the UUID of the fake player the bot created.
    """

    gamerules: Dict[str, Dict]
    """
    Gamerules that the bot should consider.
    
    Automatically updated whenever the gamerules change.
    """

    BOT_NAME: str
    """
    Canonical name of the bot type.
    
    This should be identical to the name used when registering the bot class.
    
    It is used when serializing and deserializing bot data.
    """

    BOT_VERSION: int
    """
    Version of the bot.

    Used to ensure that old saved bot states are not loaded.
    """

    NAME_POOL: List[str]
    """
    Pool of names to choose from.
    
    When adding a bot to a lobby, random names will be drawn from this pool.
    
    To ensure that users cannot confuse bots with real players, these names should always
    contain either the prefix ``Bot`` or end with ``(Bot)`` to signal that they are a bot.
    
    The signup handler will prevent a user from registering an account that starts with
    ``bot`` or contains non-alphanumerical characters.
    """

    def __init__(self, c: cg.CardGame, bot_id: uuid.UUID, name: str):
        self.cg = c

        self.bot_id = bot_id
        self.name = name

        self.lock = threading.Lock()

        self._bot_thread: Optional[threading.Thread] = None
        self.task_queue = queue.Queue()

        self.should_run: bool = True

        self.gamerules = {}

        self._event_handlers: Dict[str, List[Callable]] = {}

    def start(self):
        """
        Starts the main loop of the bot in a separate thread.

        There is usually no need to call this manually, it will be called by the lobby
        when adding a bot.

        :return:
        """

        if self._bot_thread is not None:
            self.cg.error(f"Bot {self.bot_id} of type {self.BOT_NAME} has already been started!")
            return

        self._bot_thread = threading.Thread(name=f"Bot Thread for bot {self.bot_id}", target=self.run)
        self._bot_thread.daemon = True
        self._bot_thread.start()

        self.register_event_handlers()

    def run(self):
        """
        Actual main loop of the bot.

        Should never be called directly, as it will block until the bot is done.

        :return:
        """
        while self.should_run:
            try:
                t, *dat = self.task_queue.get(timeout=1)
            except queue.Empty:
                continue

            with self.lock:
                if t == "event":
                    event, data = dat[0]
                    if event in self._event_handlers:
                        for handler in self._event_handlers[event]:
                            try:
                                handler(event, data)
                            except Exception:
                                self.cg.exception(f"Exception while handling bot event for bot {self.bot_id}: ")
                elif t == "stop":
                    reason = dat[0]
                    self.cg.info(f"Bot thread for bot {self.bot_id} stopping because {reason}")
                    self.should_run = False
                    break
                else:
                    self.cg.error(f"Invalid bot task type '{t}'")

            self.task_queue.task_done()

        self.cg.info(f"Thread for bot {self.bot_id} finished")

    def stop(self, reason="stop() was called"):
        """
        Stops the bot thread as soon as possible.

        Note that some events may still be processed before the stop event arrives.

        The given reason will be printed when the bot exits.

        :param reason: Reason to print when exiting
        :return: None
        """
        self.task_queue.put(["stop", reason])

    @abc.abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """
        Serializes the state of the bot for later deserialization.

        The returned dictionary must be JSON and msgpack encodable.

        :return: Dict containing bot state
        """
        pass

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, cg, lobby: uuid.UUID, data: Dict[str, Any]) -> "Bot":
        """
        Called to reconstruct the bot from serialized data.

        :param cg: CG singleton
        :param lobby: UUID of the lobby that the bot should re-join
        :param data: Data obtained from a previous serialize() call
        :return: Fully initialized and restored bot object
        """
        pass

    @abc.abstractmethod
    def initialize(self, data: Dict[str, Any]) -> None:
        """
        Called when the game begins.

        May be called multiple times if the bot is kept in the lobby across multiple games.

        :param data: Raw data from the cg:game.start packet
        :return:
        """
        pass

    @abc.abstractmethod
    def on_packet(self, packet: str, data: Dict) -> None:
        """
        Called whenever a packet would have been sent to the bot.

        This uses special hooks to redirect all packets sent via :py:meth:`send_to_user()`
        to the UUID of this bot.

        Note that this only works after :py:meth:`start()` has been called.

        :param packet: Name of the received packet
        :param data: Packet payload
        :return: None
        """
        pass

    @classmethod
    def generate_name(cls, blacklist=None) -> str:
        """
        Generate a new name for this bot.

        By default, a random name is chosen from :py:attr:`NAME_POOL`\\ .

        :return: User-friendly name
        """
        if blacklist is None or len(blacklist) == 0:
            return random.choice(cls.NAME_POOL)
        else:
            # TODO: find a more time and memory efficient approach
            return random.choice([n for n in cls.NAME_POOL if n not in blacklist])

    @classmethod
    @abc.abstractmethod
    def supports_game(cls, game: str) -> bool:
        """
        Called to check if this bot class supports a specific game.

        Should be overridden by subclasses to implement proper logic.

        :param game: Game to check for
        :return: whether or not the game is supported
        """
        pass

    def send_event(self, event: str, data):
        """
        Send an event from within the bot's thread.

        Executed asynchronously by the server main loop.

        Note that errors caused by event handlers may appear out-of-order in log files in
        relation to logging occuring from within bot code.

        :param event: Name of the event
        :param data: Arbitrary event data
        :return:
        """
        self.cg.server.event_queue.put((event, data,))

    def add_event_listener(self, event: str, handler: Callable[[str, Dict], None]):
        """
        Adds an event listener that will always be called in the bot's thread.

        Internally adds a proxy handler.

        It is strongly recommended to not send events from the bot to itself, as there will
        be a rather long delay. This is because the bot will first enqueue the event for
        the server to be processed. The server will then, when processing it, enqueue the
        event again for processing by the bot.

        Also ensures that the event handlers are properly removed when the bot is deleted.

        :param event:
        :param handler:
        :return:
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []

        self._event_handlers[event].append(handler)
        self.cg.add_event_listener(event, self._receive_event, group=self.bot_id)

    def register_event_handlers(self):
        """
        Registers default event handlers.

        Subclasses are recommended to override this when adding event handlers, but
        should always remember to call the overridden functionality to ensure that
        common features still work.

        :return:
        """

        self.add_event_listener(f"cg:bot.[{self.bot_id.hex}].packet.recv", self.handle_recvpacket)
        self.add_event_listener(f"cg:bot.[{self.bot_id.hex}].gamerules", self.handle_gamerules)

    def handle_recvpacket(self, event: str, data: Dict):
        self.on_packet(data["packet"], data["data"])

    def handle_gamerules(self, event: str, data: Dict):
        self.gamerules = data["gamerules"]

    def _receive_event(self, event, data):
        self.task_queue.put(["event", (event, data)])

    def delete(self):
        self.should_run = False
        self.cg.event_manager.del_group(self.bot_id)

        del self.cg.server.users_uuid[self.bot_id].bot
        del self.cg.server.users_uuid[self.bot_id]
