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
import jwt
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
            self.cg.warn("Received Game Load packet, but the sender is not in a lobby!")
            return

        try:
            payload = jwt.decode(
                msg["data"],
                key=self.cg.server.secret,
                issuer=self.cg.server.serverid.hex,
                algorithms=["HS256"],
            )
            self.cg.info(f"Received game load request for game {msg['game_id']}")
        except jwt.exceptions.InvalidSignatureError:
            self.cg.error(f"Received game load request with invalid signature!")
            self.cg.server.send_status_message(u, "warn", "cg:msg.lobby.load_game.invalid_signature")
            return
        except Exception:
            self.cg.exception(f"Unknown error during game load request:")
            return

        data = payload["data"]

        if data["version"] != self.cg.server.game_reg[lobby.game].GAME_VERSION:
            # To prevent very old games from being loaded
            self.cg.server.send_status_message(u, "warn", "cg:msg:lobby.load_game.oldversion")
            return

        if not ("type" in data and "creation_time" in data and "players" in data and "gamerules" in data and
                "round_num" in data and "buckrounds" in data and "scores" in data and "current_points" in data and
                "game_summaries" in data):
            self.cg.server.send_status_message(u, "warn", "cg:msg.lobby.load_game.invalid_data")
            return

        if lobby.user_roles[u.uuid] < ROLE_ADMIN:
            self.cg.server.send_status_message(u, "warn", "cg:msg.lobby.load_game.missing_rights")
            return

        players = [uuidify(p) for p in data["players"]]
        if not sorted(map(uuidify, lobby.users)) == sorted(map(uuidify, players)):
            self.cg.server.send_status_message(u, "warn", "cg:msg.lobby.load_game.users_not_identical")
            return
        else:
            lobby.update_gamerules(data["gamerules"])
            lobby.game_data = data

            self.cg.server.send_status_message(u, "notice", "cg:msg.lobby.load_game.success")
            self.cg.info(f"Game data applied")