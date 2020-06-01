#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ready.py
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

from cg.constants import STATE_LOBBY
from cg.packet import CGPacket


class ReadyPacket(CGPacket):
    state = STATE_LOBBY
    required_keys = [
        "ready",
    ]
    allowed_keys = [
        "ready",
    ]
    side = SIDE_SERVER

    def receive(self, msg, cid=None):
        if self.peer.clients[cid].user.lobby is None:
            self.cg.error(f"User {self.peer.clients[cid].user.username} tried to signal readiness, but is in no lobby")
            return

        user: cgserver.user.User = self.peer.clients[cid].user
        l = self.cg.server.lobbies[user.lobby]
        l.user_ready[user.uuid] = msg["ready"]

        self.cg.send_event("cg:lobby.user.ready", {"lobby": user.lobby, "user": user, "ready": msg["ready"]})

        l.send_to_all("cg:lobby.change", {
            "users": {user.uuid.hex: {"ready": msg["ready"]}}
        })

        self.cg.debug(f"Player {user.username} of lobby {user.lobby} changed readiness: {msg['ready']}")

        ready = all([l.user_ready[u] for u in l.users]) and l.game is not None

        ready = ready and self.cg.server.game_reg[l.game].check_playercount(len(l.users))

        if ready:
            self.cg.info(f"All players of lobby {user.lobby} are ready, starting game '{l.game}'")

            self.cg.send_event("cg:lobby.ready", {"lobby": user.lobby})
            self.cg.send_event(f"cg:lobby.ready.{l.game}", {"lobby": user.lobby})

            if l.game_data is None:
                g = self.cg.server.game_reg[l.game](self.cg, user.lobby)
            else:
                g = self.cg.server.game_reg[l.game].deserialize(self.cg, user.lobby, l.game_data)
            self.cg.server.games[g.game_id] = g

            l.started = True
            g.start()

            for i in l.users:
                l.user_ready[i] = False
