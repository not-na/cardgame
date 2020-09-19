#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  auth.py
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
import re
import uuid

from cg.constants import STATE_AUTH, STATE_ACTIVE
from cg.packet import CGPacket

import cgserver.user


USER_PATTERN = re.compile("[a-zA-Z][a-zA-Z0-9_]{2,15}")

# Required to prevent excessive collisions when hashing
# Should be long enough, even for password managers
MAX_PWD_LENGTH = 128


class AuthPacket(CGPacket):
    state = [STATE_AUTH, STATE_ACTIVE]
    required_keys = []
    allowed_keys = [
        "pwd",
        "create",
        "username",
        "uuid",
        "status",
        "serverid",
    ]

    def receive(self, msg, cid=None):
        username = msg["username"]

        if msg.get("create", False):
            if not self.cg.server.settings["allow_new_accounts"]:
                self.peer.send_message("cg:auth",
                                       {
                                           "status": "register_disabled",
                                           "username": username.lower(),
                                       }, cid)
                return

            if username.lower() in self.cg.server.users:
                # User already exists
                self.peer.send_message("cg:auth", {
                    "status": "user_exists",
                    "username": username.lower(),
                }, cid)
                return
            else:
                if not USER_PATTERN.fullmatch(username) or username.lower().startswith("bot"):
                    # Invalid username
                    self.peer.send_message("cg:auth", {
                       "status": "wrong_credentials",
                    })
                    return
                if "pwd" not in msg or len(msg["pwd"]) >= MAX_PWD_LENGTH:
                    # Invalid password
                    self.peer.send_message("cg:auth", {
                        "status": "wrong_credentials",
                    })
                    return

                # User does not exist, create it
                self.cg.info(f"Creating new account with name '{username}'")
                u = cgserver.user.User(self.cg.server, self.cg, username, {
                    "pwd": msg["pwd"],
                    # No uuid necessary, will be created automatically
                })
                self.cg.server.users[username.lower()] = u
                self.cg.server.users_uuid[u.uuid] = u

                self.cg.server.save_server_data()

                self.peer.clients[cid].user = u
                self.peer.clients[cid].state = STATE_ACTIVE

                u.cid = cid

                self.cg.server.send_user_data(u.uuid, cid)

                self.cg.send_event("cg:network.client.register", {"client": cid})
                self.cg.send_event("cg:network.client.login", {"client": cid})

                self.peer.send_message("cg:auth", {
                    "status": "logged_in",
                    "username": u.username,
                    "uuid": u.uuid.hex,
                    "pwd": u.pwd,
                    "serverid": self.cg.server.serverid.hex,
                }, cid)
        else:
            if username.lower() not in self.cg.server.users:
                # User does not exist
                self.peer.send_message("cg:auth", {
                    "status": "wrong_credentials",
                }, cid)
                return
            elif self.cg.server.users[username.lower()].check_password(msg.get("pwd", "")):
                u = self.cg.server.users[username.lower()]

                if u.uuid.hex in self.cg.server.settings["blocklist"]:
                    self.peer.send_message("cg:auth", {
                        "status": "blocked",
                        "username": username.lower()
                    }, cid)
                    return

                # Correct password, log in
                self.cg.info(f"User {username} logged in")

                self.peer.clients[cid].user = u
                self.peer.clients[cid].state = STATE_ACTIVE

                u.cid = cid

                self.cg.server.send_user_data(u.uuid, cid)

                self.cg.send_event("cg:network.client.login", {"client": cid})

                self.peer.send_message("cg:auth", {
                    "status": "logged_in",
                    "username": u.username,
                    "uuid": u.uuid.hex,
                    "pwd": u.pwd,
                    "serverid": self.cg.server.serverid.hex,
                }, cid)
            else:
                # Incorrect credentials
                self.peer.send_message("cg:auth", {
                    "status": "wrong_credentials",
                }, cid)
                return

