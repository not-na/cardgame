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
import time
import uuid
from typing import Union, Dict, Optional

import peng3dnet

import cg

import cgclient
import cgclient.gui

from cg.constants import STATE_AUTH, MODE_CG


class CGClient(peng3dnet.net.Client):
    def __init__(self, c: cg.CardGame, cgc, *args, **kwargs):
        self.start_time = time.time()
        super().__init__(*args, **kwargs)

        self.cg = c
        self.cgclient = cgc

    def on_handshake_complete(self):
        super().on_handshake_complete()

        self.remote_state = STATE_AUTH
        self.mode = MODE_CG

        self.cg.info("Handshake with server complete, proceeding to login")

        self.cg.client.gui.servermain.changeSubMenu("login")

        self.conntype = peng3dnet.CONNTYPE_CLASSIC

    def on_close(self, reason=None):
        super().on_close(reason)

        if reason in ["packetregmismatch", "socketclose", "smartpacketinvalid"]:
            self.cg.error(f"Connection closed due to '{reason}'")
        else:
            self.cg.info(f"Connection closed due to '{reason}'")

        self.cg.send_event("cg:network.client.close_conn", {"reason": reason})


class Client(object):
    gui: cgclient.gui.PengGUI

    def __init__(self, cg: cg.CardGame, username=None, pwd=None, default_server=None):
        self.cg = cg

        self.gui: [cgclient.gui.PengGUI, None] = None

        self._client: Union[CGClient, None] = None
        self.server = None

        self.default_server = default_server if default_server is not None else ""

        self.username = username
        self.pwd = pwd

        self.user_id: Optional = None

        self.users: Dict[str, cgclient.user.User] = {}
        self.users_uuid: Dict[uuid.UUID, cgclient.user.User] = {}

        self.lobby: Union[None, cgclient.lobby.Lobby] = None

        # TODO: implement async ping

        self.register_event_handlers()

    def init_gui(self):
        self.gui = cgclient.gui.PengGUI(self, self.cg)
        self.gui.init()

    def connect_to(self, addr, ref=None):
        self.cg.info(f"Connecting to server {addr}")

        self.server = peng3dnet.util.normalize_addr_socketstyle(addr, self.cg.get_config_option("cg:network.default_port"))
        self.cg.debug(f"Normalized address {self.server[0]}:{self.server[1]}")
        # TODO: save the last server we connected to

        self._client = CGClient(self.cg, self, self.gui.peng, self.server)

        # For last-minute changes and monkeypatches
        self.cg.send_event("cg:network.client.create", {"client": self, "peer": self._client, "ref": ref})

        # Register all packets
        self.cg.send_event("cg:network.packets.register.do", {
            "reg": self._client.registry,
            "registrar": self._client.register_packet,
            "server": self.server,
            "mode": "client",
            "peer": self._client,
        })

        self.cg.debug(f"Packet Registry: {dict(self._client.registry.reg_int_str.inv)}")

        # Start the network loop
        self.cg.debug("Starting main networking loop in separate thread")
        self.cg.send_event("cg:network.client.startloop", {"client": self, "peer": self._client, "ref": ref})
        self._client.runAsync()

        self.cg.send_event("cg:network.client.startproc", {"client": self, "peer": self._client, "ref": ref})
        self.cg.send_event("cg:network.client.waitforconn", {"client": self, "peer": self._client, "ref": ref})

    def send_message(self, ptype, data: dict):
        self._client.send_message(ptype, data)

    # Event Handlers

    def register_event_handlers(self):
        self.cg.add_event_listener("cg:network.client.conn_establish", self.handler_connestablish)

        self.cg.add_event_listener("cg:network.packets.register.do", self.handler_dopacketregister)

    def handler_connestablish(self, event: str, data: dict):
        self.cg.info(f"Connection established after {(time.time()-data['peer'].start_time)*1000:.2f}ms!")

    def handler_dopacketregister(self, event: str, data: dict):
        cgclient.packet.register_default_packets(data["reg"], data["peer"], self.cg, data["registrar"])
