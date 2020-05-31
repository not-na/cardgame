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
import threading
import time
import uuid
from typing import Dict, Optional, Type, List

import peng3dnet
import pyglet

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

        self.cg.send_event("cg:network.client.conn_establish", {
            "ref": self.cg.client.server_ref,
            "peer": self,
        })

    def on_close(self, reason=None):
        super().on_close(reason)

        if reason in ["packetregmismatch", "socketclose", "smartpacketinvalid"]:
            self.cg.error(f"Connection closed due to '{reason}'")
        else:
            self.cg.info(f"Connection closed due to '{reason}'")

        self.cg.send_event("cg:network.client.close_conn", {"reason": reason})

        pyglet.app.exit()


class Client(object):
    gui: cgclient.gui.PengGUI

    def __init__(self, cg: cg.CardGame, username=None, pwd=None, default_server=None):
        self.cg = cg

        self.gui: Optional[cgclient.gui.PengGUI] = None

        self._client: Optional[CGClient] = None
        self.server = None

        self.default_server = default_server if default_server is not None else ""

        self.username: Optional[str] = username
        self.pwd: Optional[str] = pwd

        self.user_id: Optional[uuid.UUID] = None

        self.users: Dict[str, cgclient.user.User] = {}
        self.users_uuid: Dict[uuid.UUID, cgclient.user.User] = {}

        self.game_reg: Dict[str, cgclient.game.CGame] = {}
        self.game: Optional[cgclient.game.CGame] = None

        self.lobby: Optional[cgclient.lobby.Lobby] = None
        self.lobby_invitation: List[uuid.UUID] = []  # (inviter, lobby_id)

        self.server_ref: Optional[str] = None

        self._pingcount = 1
        self._pinglock = threading.Lock()

        self.register_event_handlers()

        self.cg.send_event("cg:game.register.do", {
            "registrar": self.register_game,
        })

    def init_gui(self):
        self.gui = cgclient.gui.PengGUI(self, self.cg)
        self.gui.init()

    def connect_to(self, addr, ref=None):
        self.cg.info(f"Connecting to server {addr}")

        self.server = peng3dnet.util.normalize_addr_socketstyle(addr,
                                                                self.cg.get_config_option("cg:network.default_port"))
        self.cg.debug(f"Normalized address {self.server[0]}:{self.server[1]}")
        self.server_ref = ref

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

    def get_user_name(self, user_id: uuid.UUID):
        if user_id not in self.users_uuid:
            return "<UNKNOWN>"
        else:
            return self.users_uuid[user_id].username

    def get_profile_img(self, user_id: uuid.UUID):
        if user_id not in self.users_uuid:
            return "default"
        else:
            return self.users_uuid[user_id].profile_img

    def register_game(self, name: str, cls: Type[cgclient.game.CGame]):
        self.game_reg[name] = cls

    def get_user(self, uuid: uuid.UUID):
        user = self.users_uuid.get(uuid, None)

        if user is not None:
            return user

        else:
            self.cg.warn(f"User with uuid {uuid} is unknown to the client!")
            user = cgclient.user.User(self.cg, {"username": "<unknown>",
                                                "uuid": uuid,
                                                "status": "unknown"})
            self.users_uuid[uuid] = user
            self.cg.client.send_message("cg:status.user", {
                "uuid": uuid.hex
            })
            return user

    def ping_server(self, server, ref=None):
        # Synchronous, see async_ping_server() for async variant
        self.cg.info(f"Starting ping to server '{server}'")

        server_addr = peng3dnet.util.normalize_addr_socketstyle(server, self.cg.get_config_option("cg:network.default_port"))
        try:
            # Request handled synchronously
            rdata = peng3dnet.ext.ping.pingServer(
                self.gui.peng,
                server_addr,
                data={"user": ""},  # TODO: send UUID to server
            )

            # Sanitize data
            ndata = {
                "name": rdata.get("name", "A CardGame Server"),
                "visiblename": rdata.get("visiblename", ""),
                "slogan": rdata.get("slogan", "A CG Server"),
                "maxplayers": int(rdata.get("maxplayers", 10)),
                "canonical_address": rdata.get("canonical_address", server_addr),
                "playercount": int(rdata.get("playercount", len(rdata.get("playerlist", [])))),
                "playerlist": rdata.get("playerlist", []),
                "canlogon": bool(rdata.get("canlogon", True)),
                "version": int(rdata.get("version", -1)),
                "timestamp": float(rdata.get("timestamp", -1)),
            }

            rdata.update(ndata)
            data = rdata

        except Exception:
            self.cg.exception(f"Exception during server ping of '{server}'")
            data = {
                "name": "A CardGame Server",
                "visiblename": "",
                "slogan": "A CG Server",
                "maxplayers": 10,
                "canonical_address": server_addr,
                "playercount": 0,
                "playerlist": [],
                "canlogon": False,
                "version": -1,
                "delay": -1,
                "timestamp": -1,
            }

            self.cg.send_event("cg:client.ping.error", {"server": server, "data": data, "ref": ref})
        else:
            self.cg.send_event("cg:client.ping.complete", {"server": server, "data": data, "ref": ref})
            self.cg.debug(f"Raw Ping Response from server: {data}")
            self.cg.info(
                f"Ping to '{server}' finished, {data['delay'] * 1000:.2f}ms latency with name '{data['name']}'")

        return data

    def async_ping_server(self, *args, **kwargs):
        # asynchronously, notifies via events only
        with self._pinglock:
            t = threading.Thread(name=f"Ping Thread #{self._pingcount}", target=self.ping_server, args=args,
                                 kwargs=kwargs)
            self._pingcount += 1

            t.daemon = True
            t.start()

    # Event Handlers

    def register_event_handlers(self):
        self.cg.add_event_listener("cg:network.client.conn_establish", self.handler_connestablish)

        self.cg.add_event_listener("cg:network.packets.register.do", self.handler_dopacketregister)
        self.cg.add_event_listener("cg:game.register.do", self.handler_dogameregister)

    def handler_connestablish(self, event: str, data: dict):
        self.cg.info(f"Connection established after {(time.time() - data['peer'].start_time) * 1000:.2f}ms!")

    def handler_dopacketregister(self, event: str, data: dict):
        cgclient.packet.register_default_packets(data["reg"], data["peer"], self.cg, data["registrar"])

    def handler_dogameregister(self, event: str, data: Dict):
        cgclient.game.register_games(data["registrar"])
