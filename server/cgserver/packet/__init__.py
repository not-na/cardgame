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


def register_default_packets(reg, peer, cg, add):
    cg.info("Registering packets")
    # AUTH CONNECTION STATE

    from . import auth_precheck
    # Auth Precheck Packet
    add("cg:auth.precheck",
        auth_precheck.AuthPrecheckPacket(
            reg, peer, c=cg,
        )
        )

    from . import auth
    # Auth Packet
    add("cg:auth",
        auth.AuthPacket(
            reg, peer, c=cg,
        )
        )

    # STATUS PACKETS

    from . import status_user
    # Status User Packet
    add("cg:status.user",
        status_user.StatusUserPacket(
            reg, peer, c=cg,
        )
        )

