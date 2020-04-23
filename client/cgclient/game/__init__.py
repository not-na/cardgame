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
import uuid
from typing import Callable, List

import cgclient

import cg


def register_games(reg: Callable):
    from . import doppelkopf
    reg("doppelkopf", doppelkopf.DoppelkopfGame)


class CGame(object):
    def __init__(self, c: cg.CardGame, game_id: uuid.UUID, player_list: List[uuid.UUID]):
        self.cg: cg.CardGame = c

        self.game_id = game_id
        self.player_list = player_list

        # Ensure all players exist in the local database
        for p in player_list:
            if p not in self.cg.client.users_uuid:
                # This is unlikely to happen if the server is implemented correctly
                # But it can happen if a game is not implemented properly
                self.cg.warn(f"Player {p} is not yet in client user database, requesting more information")
                self.cg.client.send_message("cg:status.user", {"uuid": p.hex})

    def start(self):
        pass

