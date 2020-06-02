#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  game_start.py
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

from peng3dnet import SIDE_CLIENT

from cg.constants import STATE_GAME_DK, STATE_LOBBY, STATE_ACTIVE
from cg.packet import CGPacket
from cg.util import uuidify


class GameStartPacket(CGPacket):
    state = [STATE_LOBBY, STATE_ACTIVE, STATE_GAME_DK]
    required_keys = [
        "game_type",
        "game_id",
        "player_list",
        "game_summaries",
    ]
    allowed_keys = [
        "game_type",
        "game_id",
        "player_list",
        "game_summaries",
    ]

    def receive(self, msg, cid=None):
        if msg["game_type"] == "doppelkopf":
            # First, set the new remote state
            self.peer.remote_state = STATE_GAME_DK

            # Then, instantiate the game class on the client
            self.cg.client.game = self.cg.client.game_reg["doppelkopf"](
                self.cg,
                uuidify(msg["game_id"]),
                [uuidify(p) for p in msg["player_list"]],
                self.cg.client.lobby
            )
            self.cg.client.game.start()

            self.cg.info(f"Joined game {self.cg.client.game.game_id} of type doppelkopf")

            # Init Scoreboard screen
            for summary in msg["game_summaries"]:
                self.cg.client.gui.ingame.gui_layer.s_scoreboard.add_round(**summary)

            # Switch the menu
            self.cg.client.gui.window.changeMenu("ingame")

            self.cg.client.gui.servermain.s_lobby.readybtn.pressed = False
            self.cg.client.gui.servermain.s_lobby.readybtn.redraw()
            for p in self.cg.client.lobby.users:
                self.cg.client.lobby.user_ready[p] = False
                self.cg.send_event("cg:lobby.player.ready", {
                    "player": p,
                    "ready": False
                })
        else:
            self.cg.crash(f"Unknown/Unsupported game type {msg['game_type']}")




