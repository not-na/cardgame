#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  client.py
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
from typing import Union

import peng3dnet

import cg

import cgclient
import cgclient.gui


class CGClient(peng3dnet.net.Client):
    pass


class Client(object):
    def __init__(self, cg: cg.CardGame, username=None, pwd=None, default_server=None):
        self.cg = cg

        self.gui: [cgclient.gui.PengGUI, None] = None

        self._client: Union[CGClient, None] = None
        self.server = None

        self.username = username
        self.pwd = pwd
        # TODO: implement default_server

        # TODO: implement async ping

        self.register_event_handlers()

    def init_gui(self):
        self.gui = cgclient.gui.PengGUI(self, self.cg)
        self.gui.init()

    # Event Handlers

    def register_event_handlers(self):
        pass
