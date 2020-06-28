#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  lobby.py
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
from typing import Union, Dict, List, Any, Set, Optional

import uuid

import cgserver

import cg
from cg.constants import ROLE_REMOVE, ROLE_CREATOR, ROLE_ADMIN, ROLE_PLAYER


class Lobby(object):
    def __init__(self, c: cg.CardGame, u: Optional[uuid.UUID] = None):
        self.cg: cg.CardGame = c

        self.uuid: uuid.UUID = u if u is not None else uuid.uuid4()
        self.game: Union[str, None] = None

        self.game_data: Optional[Dict] = None

        self.users: List[uuid.UUID] = []
        self.user_roles: Dict[uuid.UUID, int] = {}
        self.user_ready: Dict[uuid.UUID, bool] = {}

        self.invitations: Set[uuid.UUID] = set()

        self.started: bool = False

        self.gamerules: Dict[str, Any] = {}
        # Debugging for Doppelkopf
        if cgserver.game.CGame.DEV_MODE:
            self.gamerules = {
                "dk.wedding": "None",
                "dk.pigs": "two_reservation",
                "dk.superpigs": "reservation",
                "dk.poverty": "sell",
                "dk.poverty_consequence": "black_sow",
            }

    def remove_user(self, user: uuid.UUID, left=False):
        if user not in self.users:
            self.cg.warn(f"Tried to remove user {user} from lobby {self.uuid}, but they are not a member")
            return

        self.cg.debug(f"Removing user {user} from lobby {self.uuid}")

        self.game_data = None

        del self.users[self.users.index(user)]
        del self.user_roles[user]
        del self.user_ready[user]

        admins = 0
        for i in self.user_roles.values():
            if i >= ROLE_ADMIN:
                admins += 1

        if admins == 0 and len(self.users) > 0:
            self.user_roles[self.users[0]] = ROLE_ADMIN

        if not left:
            self.cg.server.send_to_user(user, "cg:lobby.leave", {"lobby": self.uuid.hex})
            self.cg.server.users_uuid[user].lobby = None

        udat = {user.hex: {"role": ROLE_REMOVE}}
        for u in self.users:
            udat[u.hex] = {"index": self.users.index(u),
                           "role": self.user_roles[u]}

        self.send_to_all("cg:lobby.change", {
            "users": udat,
            "user_roles": {k.hex: v for k, v in self.user_roles.items()}
        })

        # Delete empty lobbies
        if len(self.users) == 0:
            self.cg.info(f"Deleting lobby {self.uuid}")
            del self.cg.server.lobbies[self.uuid]

    def add_user(self, user: cgserver.user.User, role: int):
        if user.uuid in self.users:
            self.cg.error(f"Tried to add user {user.username} to lobby {self.uuid}, but they are already a member")
            return

        self.game_data = None

        # Make sure all users know each other
        for u in self.users:
            # Send all existing users to the new user
            self.cg.server.send_user_data(u, user.uuid)

            # Send the new user to all existing users
            self.cg.server.send_user_data(user.uuid, u)

        user.lobby = self.uuid

        # Add user to internal DB
        self.users.append(user.uuid)
        self.user_roles[user.uuid] = role
        self.user_ready[user.uuid] = False

        self.cg.server.send_to_user(user, "cg:lobby.join", {
            "lobby": self.uuid.hex,
        })

        gamerule_validators = self.cg.server.game_reg.get(self.game, cgserver.game.CGame).GAMERULES

        self.cg.server.send_to_user(user, "cg:lobby.change", {
            "users": {u.hex: {
                "ready": self.user_ready[u],
                "role": self.user_roles[u],
                "index": self.users.index(u)
                }
                for u in self.users
            },
            "game": self.game,
            "gamerules": self.gamerules,
            "gamerule_validators": gamerule_validators,
            "supported_bots": [
                key for key in self.cg.server.bot_reg if self.cg.server.bot_reg[key].supports_game(self.game)
            ]
        })

        self.send_to_all("cg:lobby.change", {
            "users": {user.uuid.hex: {
                "ready": self.user_ready[user.uuid],
                "role": self.user_roles[user.uuid],
                "index": self.users.index(user.uuid)
            }},
        }, user)

        self.cg.info(f"Added user with name {user.username} to lobby {self.uuid} with role {role}")

    def add_bot(self, bot_type: str, from_user: cgserver.user.User) -> bool:
        if self.cg.server.game_reg[self.game].check_playercount(len(self.users), True):
            self.cg.server.send_status_message(from_user, "warning", "cg:msg.lobby.add_bot.lobby_full")
            return False

        if bot_type not in self.cg.server.bot_reg:
            self.cg.server.send_status_message(from_user, "warning", "cg:msg.lobby.add_bot.unknown_type")
            return False

        bot_cls = self.cg.server.bot_reg[bot_type]

        if not bot_cls.supports_game(self.game):
            self.cg.server.send_status_message(from_user, "warning", "cg:msg.lobby.add_bot.invalid_type")
            return False

        bot_id = uuid.uuid4()
        u = cgserver.user.BotUser(self.cg.server,
                                  self.cg,
                                  bot_cls.generate_name(
                                      blacklist=list(
                                          [self.cg.server.users_uuid[uid].username for uid in self.users]
                                      )
                                  ),
                                  {"uuid": bot_id},
                                  )
        self.cg.server.users_uuid[bot_id] = u

        bot = bot_cls(self.cg,
                      bot_id,
                      u.username,
                      )

        u.bot = bot

        self.add_user(u, ROLE_PLAYER)
        self.user_ready[u.uuid] = True

        # Update ready state immediately
        self.send_to_all("cg:lobby.change", {
            "users": {u.uuid.hex: {"ready": True}},
        })

        bot.start()

        self.cg.info(f"Successfully added bot of type '{bot_type}' to lobby {self.uuid}")
        self.check_ready()

        return True

    def restore_bot(self, data: Dict) -> bool:
        if self.cg.server.game_reg[self.game].check_playercount(len(self.users), True):
            self.cg.error(f"Could not restore bot because lobby was full")
            return False

        bot_type = data.get("type", None)

        if bot_type not in self.cg.server.bot_reg:
            self.cg.error(f"Could not restore bot because type is unknown")
            return False

        bot_cls = self.cg.server.bot_reg[bot_type]

        if bot_cls.BOT_VERSION != data.get("version", None):
            self.cg.error(f"Could not restore bot {data['type']} because version does not match")
            return False

        u = cgserver.user.BotUser(self.cg.server,
                                  self.cg,
                                  bot_cls.get("name", "<ERROR Bot>"),
                                  data,  # Only UUID necessary, but its simpler this way
                                  )
        self.cg.server.users_uuid[u.uuid] = u

        self.add_user(u, ROLE_PLAYER)

        self.user_ready[u.uuid] = True

        # Update ready state immediately
        self.send_to_all("cg:lobby.change", {
            "users": {u.uuid.hex: {"ready": True}},
        })

        self.check_ready()

        try:
            bot = bot_cls.deserialize(cg, self, data)
        except Exception:
            self.cg.critical(f"Could not deserialize bot")
            self.cg.exception(f"Exception while deserializing bot:")
            return False

        u.bot = bot
        bot.start()

        return True

    def check_ready(self):
        """
        Checks if the lobby is ready and calls :py:meth:`ready()` if it is.

        :return:
        """
        ready = all([self.user_ready[u] for u in self.users]) and self.game is not None

        ready = ready and self.cg.server.game_reg[self.game].check_playercount(len(self.users))

        if ready:
            self.ready()

        return ready

    def ready(self):
        """
        Starts the game from the lobby.

        Should only be called if all players are ready and the player count is correct.

        Note that no checks of this are performed.

        :return:
        """
        self.cg.info(f"All players of lobby {self.uuid} are ready, starting game '{self.game}'")

        self.cg.send_event("cg:lobby.ready", {"lobby": self.uuid})
        self.cg.send_event(f"cg:lobby.ready.{self.game}", {"lobby": self.uuid})

        if self.game_data is None:
            g = self.cg.server.game_reg[self.game](self.cg, self.uuid)
        else:
            g = self.cg.server.game_reg[self.game].deserialize(self.cg, self.uuid, self.game_data)
        self.cg.server.games[g.game_id] = g

        self.started = True

        for i in self.users:
            self.user_ready[i] = False
            self.cg.server.users_uuid[i].cur_game = g.game_id

            if isinstance(self.cg.server.users_uuid[i], cgserver.user.BotUser):
                self.cg.send_event(f"cg:bot.[{i.hex}].gamerules", {"gamerules": self.gamerules})

        g.start()

    def send_to_all(self, packet: str, data: dict, exclude=None):
        for u in self.users:
            if u != exclude:
                self.cg.server.send_to_user(u, packet, data)

    def set_gamerule(self, rule: str, value):
        if rule not in self.cg.server.game_reg[self.game].GAMERULES:
            # Ignore unknown rule
            return

        valid, out = cg.util.validate(value, self.cg.server.game_reg[self.game].GAMERULES[rule])
        # Ignore valid flag for now

        self.gamerules[rule] = out

        self.send_to_all("cg:lobby.change", {
            "gamerules": {rule: out},
        })

    def update_gamerules(self, new: Dict[str, Any]):
        ch = {}

        for rule, value in new.items():
            if rule not in self.cg.server.game_reg[self.game].GAMERULES:
                # Ignore unknown rule
                continue

            valid, out = cg.util.validate(value, self.cg.server.game_reg[self.game].GAMERULES[rule])
            # Ignore valid flag for now
            self.gamerules[rule] = out
            ch[rule] = out

        self.send_to_all("cg:lobby.change", {
            "gamerules": ch,
        })

    def set_variant(self, variant: str):
        self.cg.warn(f"Setting Variants is currently not implemented")
