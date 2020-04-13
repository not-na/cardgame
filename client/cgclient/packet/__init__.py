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

    def r(name: str, packet):
        add(name, packet(reg, peer, c=cg))

    # AUTH CONNECTION STATE

    from . import auth_precheck
    # Auth Precheck Packet
    r("cg:auth.precheck", auth_precheck.AuthPrecheckPacket)

    from . import auth
    # Auth Packet
    r("cg:auth", auth.AuthPacket)

    # STATUS PACKETS

    from . import status_user
    # Status User Packet
    r("cg:status.user", status_user.StatusUserPacket)

    # LOBBY PACKETS
    from . import lobby

    # Lobby Create Packet
    r("cg:lobby.create", lobby.create.CreatePacket)

    # Lobby Join Packet
    r("cg:lobby.join", lobby.join.JoinPacket)

    # Lobby Change Packet
    r("cg:lobby.change", lobby.change.ChangePacket)

    # Lobby Ready Packet
    r("cg:loby.ready", lobby.ready.ReadyPacket)
