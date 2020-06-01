#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  game_load
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
from peng3dnet import SIDE_SERVER

from cg.constants import STATE_LOBBY, ROLE_ADMIN
from cg.packet import CGPacket
from cg.util import uuidify


class GameLoadPacket(CGPacket):
    state = STATE_LOBBY
    required_keys = [
        "game_id",
        "data",
    ]
    allowed_keys = [
        "game_id",
        "data",
    ]
    side = SIDE_SERVER

    def receive(self, msg, cid=None):
        u = self.peer.clients[cid].user
        lobby = self.cg.server.lobbies.get(u.lobby, None)
        if lobby is None:
            self.cg.warn("Received Lobby Change packet though the sender is in no lobby!")
            return

        data = msg["data"]
        if not ("type" in data and "creation_time" in data and "players" in data and "gamerules" in data and
                "round_num" in data and "buckrounds" in data and "scores" in data and "current_points" in data and
                "game_summaries" in data):
            self.cg.server.send_status_message(u, "warn", "cg:msg.lobby.load_game.invalid_data")
            return

        if lobby.user_roles[u.uuid] < ROLE_ADMIN:
            self.cg.server.send_status_message(u, "warn", "cg:msg.lobby.load_game.missing_rights")
            return

        players = [uuidify(p) for p in data["players"]]
        if not sorted(lobby.users) == sorted(players):
            self.cg.server.send_status_message(u, "warn", "cg:msg.lobby.load_game.users_not_identical")
            return

        else:
            lobby.game_data = msg["data"]
