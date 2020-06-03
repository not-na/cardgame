#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  game_save.py
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
import os

import jwt
from peng3dnet import SIDE_CLIENT

import cg
from cg.constants import STATE_GAME_DK
from cg.packet import CGPacket
from cg.util.serializer import msgpack


class GameSavePacket(CGPacket):
    state = STATE_GAME_DK
    required_keys = [
        "game_id",
        "data",
    ]
    allowed_keys = [
        "game_id",
        "data",
    ]
    side = SIDE_CLIENT

    def receive(self,msg,cid=None):
        base_dir = os.path.join(cg.config.get_settings_path("cardgame"), "adjourned-games")

        # Ensure the directory exists
        os.makedirs(base_dir, exist_ok=True)

        fname = os.path.join(base_dir, f"{msg['game_id']}.cgg")

        self.cg.info(f"Saving game with ID {msg['game_id']} to file {fname}")

        # Sanity check
        if os.path.exists(fname):
            self.cg.warn(f"Game with ID {msg['game_id']} already exists, overwriting it")

        sdat = msg["data"]

        # Decode data, since we need some keys
        ddat = jwt.decode(sdat, verify=False)["data"]

        data = {
            "id": ddat["id"],
            "creation_time": ddat["creation_time"],
            "players": ddat["players"],
            "type": ddat["type"],
            "data": sdat,
        }

        # Save using msgpack
        with open(fname, "wb") as f:
            msgpack.dump(data, f)
