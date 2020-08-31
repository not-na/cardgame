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

import cgserver.version


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
        compatible = not (msg["protoversion"] != cgserver.version.PROTO_VERSION or
                          msg["semver"] != cgserver.version.SEMVER or
                          msg["flavor"] != cgserver.version.FLAVOR
                          )

        self.peer.send_message(
            "cg:version.check",
            {
                "protoversion": cgserver.version.PROTO_VERSION,
                "semver": cgserver.version.SEMVER,
                "flavor": cgserver.version.FLAVOR,
                "compatible": compatible,
            },
            cid
        )

        if compatible:
            self.peer.clients[cid].state = STATE_AUTH
        else:
            # Will not really work, since peng3dnet immediately closes the connection
            # Update of peng3dnet required
            # TODO: check that this actually works when peng3dnet is updated
            self.peer.close_connection(cid, "versionmismatch")
