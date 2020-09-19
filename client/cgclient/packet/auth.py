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

from cg.constants import STATE_AUTH, STATE_ACTIVE
from cg.packet import CGPacket
from cg.util import uuidify


class AuthPacket(CGPacket):
    state = STATE_AUTH
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
        status = msg.get("status", "error")

        if status == "logged_in":
            self.cg.info("Logged in!")

            self.peer.remote_state = STATE_ACTIVE
            self.cg.client.gui.servermain.d_create_acc.exitDialog()
            self.cg.client.gui.servermain.changeSubMenu("main")
            self.cg.client.user_id = uuidify(msg["uuid"])
            self.cg.client.pwd = msg["pwd"]

            if "serverid" in msg:
                self.cg.client.server_id = uuidify(msg["serverid"])

            self.cg.send_event("cg:network.client.login", {"client": self.cg.client})
        elif status == "wrong_credentials":
            self.cg.info("Wrong credentials, redirecting to login")
            self.cg.client.gui.servermain.changeSubMenu("login")
            self.cg.client.gui.servermain.d_login_err.label_main = self.cg.client.gui.peng.tl(
                "cg:gui.menu.smain.loginerr.wrongcred"
            )
            self.cg.client.gui.servermain.d_login_err.activate()
        elif status == "user_exists":
            self.cg.info("User exists, redirecting to login")
            self.cg.client.gui.servermain.changeSubMenu("login")
            self.cg.client.gui.servermain.d_login_err.label_main = self.cg.client.gui.peng.tl(
                "cg:gui.menu.smain.loginerr.userexists"
            )
            self.cg.client.gui.servermain.d_login_err.activate()
        elif status == "register_disabled":
            self.cg.error("Registration is disabled, redirecting to login")
            self.cg.client.gui.servermain.changeSubMenu("login")
            self.cg.client.gui.servermain.d_login_err.label_main = self.cg.client.gui.peng.tl(
                "cg:gui.menu.smain.loginerr.registerdisabled"
            )
            self.cg.client.gui.servermain.d_login_err.activate()
        elif status == "blocked":
            self.cg.error("User is blocked, redirecting to login")
            self.cg.client.gui.servermain.changeSubMenu("login")
            self.cg.client.gui.servermain.d_login_err.label_main = self.cg.client.gui.peng.tl(
                "cg:gui.menu.smain.loginerr.blocked"
            )
            self.cg.client.gui.servermain.d_login_err.activate()
        elif status == "logged_out":
            self.cg.error("logged_out auth status not yet supported")
        else:
            pass
