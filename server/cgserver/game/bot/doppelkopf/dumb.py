#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dumb.py
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
from typing import Dict, Any

from . import DoppelkopfBot


class DumbDoppelkopfBot(DoppelkopfBot):
    NAME_POOL = [
        # Example name schemes:
        # "BotGLaDOS",
        # "Somebody (Bot)",
        # TODO: add more names
    ]

    # Required for serialization and deserialization
    BOT_NAME = "dk_dumb"

    def select_move(self):
        super().select_move()
        return self.get_valid_moves()[0]

    def serialize(self) -> Dict[str, Any]:
        sdat = super().serialize()

        data = {
            # TODO
        }

        # Allows overwriting data from the parent class
        sdat.update(data)
        return sdat

    @classmethod
    def deserialize(cls, cg, lobby, data) -> "DumbDoppelkopfBot":
        bot = super(DumbDoppelkopfBot, cls).deserialize(cg, lobby, data)

        # TODO

        # PyCharm is stupid here and does not consider that "cls" is instantiated
        return bot
