#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  create.py
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
import cgserver
from peng3dnet import SIDE_SERVER

from cg.constants import STATE_ACTIVE, ROLE_CREATOR, STATE_LOBBY
from cg.packet import CGPacket


class CreatePacket(CGPacket):
    state = STATE_ACTIVE
    required_keys = []
    allowed_keys = [
        "game",
        "variant",
    ]
    side = SIDE_SERVER

    def receive(self, msg, cid=None):
        u = self.peer.clients[cid].user

        if u.lobby is not None:
            self.cg.warn(f"User {u.username} tried to create a lobby, but is already in one")
            return

        l = cgserver.lobby.Lobby(self.cg)
        self.cg.server.lobbies[l.uuid] = l
        self.cg.send_event(f"cg:lobby.create", {"uuid": l.uuid, "lobby": l, "creator": u})

        self.cg.info(f"Created lobby with UUID {l.uuid} on behalf of user {u.username}")

        if msg.get("game", None) is not None:
            self.cg.info(f"Game for lobby {l.uuid} is {msg['game']} with variant {msg.get('variant', 'c')}")
            l.game = msg["game"]
            self.cg.send_event("cg:lobby.game.change", {"old": None, "lobby": l})
            self.cg.send_event(f"cg:lobby.game.change.{l.game}", {"old": None, "lobby": l})

            l.set_variant(msg.get('variant', 'c'))

            self.cg.warn("Invite of other players of party is not yet implemented")
        else:
            self.cg.info(f"Game for lobby {l.uuid} not yet set, delaying user invite")
            # Other party members are not yet invited
            # They will be invited once the game has been set

        # Let user itself "join" the lobby
        l.add_user(u, ROLE_CREATOR)


