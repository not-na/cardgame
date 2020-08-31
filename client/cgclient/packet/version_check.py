#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  version_check.py
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

from peng3dnet import SIDE_SERVER

from cg.constants import STATE_VERSIONCHECK, STATE_AUTH
from cg.packet import CGPacket

import cgclient.version


class VersionCheckPacket(CGPacket):
    state = STATE_VERSIONCHECK
    required_keys = [
        "protoversion",
        "semver",
        "flavor",
    ]
    allowed_keys = [
        "protoversion",
        "semver",
        "flavor",
        "compatible",
    ]

    def receive(self, msg, cid=None):
        # TODO: check that this works when peng3dnet is updated
        if msg["compatible"]:
            self.cg.info(f"Version check succeeded. Server Version: {msg['semver']} ({msg['protoversion']}, {msg['flavor']})")
            self.peer.remote_state = STATE_AUTH
            return

        self.cg.error("Version incompatible with server, aborting connection")
        self.cg.info(f"Server Version Information: {msg['semver']} ({msg['protoversion']}, {msg['flavor']})")
        self.cg.client.gui.servermain.d_connerr.label_main = self.cg.client.gui.peng.tl(
            "cg:gui.menu.smain.connerr.version", data=msg,
        )
        self.cg.client.gui.servermain.d_connerr.activate()

