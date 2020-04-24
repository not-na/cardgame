#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  doppelkopf.py
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
from typing import List

import cgclient

from . import CGame


class DoppelkopfGame(CGame):
    SLOT_NAMES: List[str] = [
        "stack",
        "poverty",
        "table",
        "hand0",
        "hand1",
        "hand2",
        "hand3",
        "tricks0",
        "tricks1",
        "tricks2",
        "tricks3",
    ]
    menu: cgclient.gui.ingame.IngameMenu

    def start(self):
        self.menu = self.cg.client.gui.ingame

        self.menu.game_layer.reinit()
