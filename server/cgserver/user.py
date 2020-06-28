#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  user.py
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
import hashlib
import hmac
import secrets
import uuid
from typing import Union, Optional, Dict, Any

import cg


class User(object):
    def __init__(self, server, c: cg.CardGame, user: str, udat: dict, auth=True):
        """
        User object representing a single user on the server.

        Note that not all users are humans, some may be bots. This can be best checked
        using ```instanceof(user, BotUser)```\\ .

        :param server: server object the user belongs to
        :param c: cg Singleton
        :param user: username as a string
        :param udat: saved user data as a dictionary, all keys optional
        :param auth: whether this user supports authentication
        """
        self.server = server
        self.cg = c

        self.username: str = user
        self.pwd: bytes = udat.get("pwd", "")
        if isinstance(self.pwd, str):
            self.pwd = self.pwd.encode()
        self.pwd_type: str = udat.get("pwd_type", "plaintext")
        if not auth:
            self.pwd_salt = None
        elif "pwd_salt" not in udat:
            self.pwd_salt = secrets.token_bytes(self.cg.get_config_option("cg:server.secret_length"))
        else:
            self.pwd_salt = udat["pwd_salt"]
        self.pwd_iterations: int = udat.get("pwd_iterations", self.get_pwd_iterations()) if auth else -1

        # Auto-upgrade plaintext passwords
        if auth and self.pwd_type == "plaintext":
            self.set_pwd(self.pwd)

        self.uuid: uuid.UUID = cg.util.uuidify(udat.get("uuid", uuid.uuid4()))

        self.profile_img = udat.get("profile_img", "default")

        self.cid: Optional[int] = None
        self.lobby: Optional[uuid.UUID] = None

        self.cur_game: Optional[uuid.UUID] = None

        # TODO: add more user data here

    def serialize(self) -> Dict[str, Any]:
        return {
            "pwd": self.pwd,
            "pwd_type": self.pwd_type,
            "pwd_salt": self.pwd_salt,
            "pwd_iterations": self.pwd_iterations,
            "uuid": self.uuid.hex,
            "profile_img": self.profile_img,
        }

    @property
    def state(self) -> str:
        return self.server.server.clients[self.cid].state

    def check_password(self, password: bytes, update=True) -> bool:
        if isinstance(password, str):
            password = password.encode()

        if self.pwd_type == "plaintext":
            if secrets.compare_digest(password, self.pwd):
                # Success!
                # Upgrade password automatically
                if update:
                    self.set_pwd(password)

                return True

            self.cg.info(f"Failed login attempt of {self.uuid.hex} with {self.pwd_type}")
            return False
        elif self.pwd_type == "pbkdf2_hmac-sha256":
            phash = hashlib.pbkdf2_hmac("sha256", password, self.pwd_salt, self.pwd_iterations)

            if hmac.compare_digest(phash.hex(), self.pwd.hex()):
                # Success!
                # Upgrade password automatically
                if update:
                    self.set_pwd(password)

                return True

            self.cg.info(f"Failed login attempt of {self.uuid.hex} with {self.pwd_type}")
            return False
        else:
            self.cg.error(f"Unknown password type {self.pwd_type} for user {self.username} with UUID {self.uuid.hex}")
            return False

    def set_pwd(self, password):
        self.pwd_type = "pbkdf2_hmac-sha256"
        self.pwd_iterations = self.get_pwd_iterations()

        phash = hashlib.pbkdf2_hmac("sha256", password, self.pwd_salt, self.pwd_iterations)

        self.pwd = phash

        self.cg.server.save_server_data()

    @staticmethod
    def get_pwd_iterations() -> int:
        # As of 2020, this should be "good enough"
        # TODO: dynamically increase this
        return 150000


class BotUser(User):
    def __init__(self, server, c: cg.CardGame, user: str, udat: dict):
        super().__init__(server, c, user, udat, auth=False)

        self.bot = None
        self.profile_img = "default"  # TODO: add different icons for different bots

    def check_password(self, password: bytes, update=True) -> bool:
        # Just in case, prevent anybody from logging in as a bot
        return False

    @property
    def state(self):
        return "bot"

    def set_pwd(self, password):
        raise RuntimeError("Cannot set password on bot user")

    def serialize(self):
        raise RuntimeError("Cannot serialize a bot user")
