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


USER_PATTERN = re.compile("[a-zA-Z][a-zA-Z0-9_]+")


class AuthPacket(CGPacket):
    state = [STATE_AUTH, STATE_ACTIVE]
    required_keys = [
        "username",
    ]
    allowed_keys = [
        "pwd",
        "create",
        "username",
        "uuid",
        "status",
    ]

    def receive(self, msg, cid=None):
        username = msg["username"]

        if msg.get("create", False):
            if username.lower() in self.cg.server.users:
                # User already exists
                self.peer.send_message("cg:auth", {
                    "status": "user_exists",
                    "username": username.lower(),
                }, cid)
                return
            else:
                # User does not exist, create it
                self.cg.info(f"Creating new account with name '{username}'")
                u = cgserver.user.User(self.cg.server, self.cg, username, {
                    "pwd": msg.get("pwd", None),
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
                }, cid)
        else:
            if username.lower() not in self.cg.server.users:
                # User does not exist
                self.peer.send_message("cg:auth", {
                    "status": "wrong_credentials",
                }, cid)
                return
            elif msg.get("pwd", None) == self.cg.server.users[username.lower()].pwd:
                # Correct password, log in
                self.cg.info(f"User {username} logged in")

                u = self.cg.server.users[username.lower()]
                self.peer.clients[cid].user = u
                self.peer.clients[cid].state = STATE_ACTIVE

                u.cid = cid

                self.cg.server.send_user_data(u.uuid, cid)

                self.cg.send_event("cg:network.client.login", {"client": cid})

                self.peer.send_message("cg:auth", {
                    "status": "logged_in",
                    "username": u.username,
                    "uuid": u.uuid.hex,
                }, cid)
            else:
                # Incorrect credentials
                self.peer.send_message("cg:auth", {
                    "status": "wrong_credentials",
                }, cid)
                return

