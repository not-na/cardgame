#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  auth_precheck.py
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

from cg.constants import STATE_AUTH
from cg.packet import CGPacket


class AuthPrecheckPacket(CGPacket):
    state = STATE_AUTH
    required_keys = [
        "username",
    ]
    allowed_keys = [
        "username",
        "valid",
        "exists",
        "key",
    ]

    def receive(self, msg, cid=None):
        if msg.get("key", "") != "":
            self.cg.error(f"Received non-empty key with cg:auth.precheck, currently not allowed")
            return

        # Check whether we could log in
        valid = msg.get("valid", False)
        exists = msg.get("exists", False)

        if valid and exists:
            # Account valid, try to log in
            self.peer.send_message("cg:auth", {
                "username": self.cg.client.gui.servermain.s_login.user.text.strip(),
                "pwd": self.cg.client.gui.servermain.s_login.pwd.text,
                "create": False,
            })
        elif valid and not exists:
            # Cannot log in, but we can create the account
            self.cg.client.gui.servermain.d_create_acc.activate()
        else:
            # Account totally invalid, show error
            # TODO: implement error message
            pass
