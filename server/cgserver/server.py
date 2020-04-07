#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  server.py
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
import socket
import sys
import time
import threading
from typing import Dict

import peng3dnet

import cg
import cgserver


class CGServer(peng3dnet.ext.ping.PingableServerMixin, peng3dnet.net.Server):
    cg: cg.CardGame

    def getPingData(self, msg, cid):
        c = self.clients[cid]
        self.cg.info(f"Server Ping by Client #{cid} with IP Address {c.addr[0]}:{c.addr[1]}")

        return {
            "name": self.cg.get_config_option("cg:server.name"),
            "visiblename": self.cg.get_config_option("cg:server.visiblename"),
            "maxplayers": self.cg.get_config_option("cg:server.maxplayers"),
            "canonical_address": socket.getfqdn(),
            "playercount": 0,  # TODO: implement player count
            "playerlist": [],  # TODO: implement player list
            "canlogon": True,  # TODO: implement properly
            "version": self.cg.get_proto_version(),
            "timestamp": time.time(),
        }


class ClientOnCGServer(peng3dnet.net.ClientOnServer):

    def on_handshake_complete(self):
        super().on_handshake_complete()

        self.server.cg.send_event("cg:network.server.newconn",
                                  {
                                      "clientonserver": self,
                                      "server": self.server,
                                      "addr": self.addr,
                                      "conntype": self.conntype,
                                  }
                                  )

    def on_close(self, reason=None):
        super().on_close(reason)

        self.server.cg.send_event("cg:network.server.closeconn",
                                  {
                                      "clientonserver": self,
                                      "server": self.server,
                                      "addr": self.addr,
                                      "conntype": self.conntype,
                                  }
                                  )


class DedicatedServer(object):
    command_manager = cgserver.command.CommandManager

    def __init__(self, c: cg.CardGame, addr=None, port=None):
        self.cg = c

        self.command_manager = cgserver.command.CommandManager(self.cg)

        self.server = CGServer(
            addr=[
                self.cg.get_config_option("cg:server.address") if addr is None else addr,
                self.cg.get_config_option("cg:server.port") if port is None else port,
            ],
            clientcls=ClientOnCGServer,
        )
        self.server.cg = self.cg
        self.server.cgserver = self

        # Allow for last-minute changes and monkeypatches
        self.cg.send_event("cg:network.server.create", {"server": self, "peer": self})

        # Register all packets
        self.cg.send_event("cg:network.packets.register.do", {
            "reg": self.server.registry,
            "registrar": self.server.register_packet,
            "server": self,
            "mode": "server",
            "peer": self.server,
        })

        self.run_console = False
        self.interactive_thread = None

        self.register_event_handlers()

    def start(self):
        self.start_listening()

        self.run_interactive_console()

    def start_listening(self):
        self.server.runAsync()
        self.server.process_async()

    def start_interactive_console(self):
        self.interactive_thread = threading.Thread(name="Server Management Console Thread", target=self.run_interactive_console)
        self.interactive_thread.daemon = True
        self.interactive_thread.start()

    def run_interactive_console(self):
        self.run_console = True

        self.cg.info("Server Console is now available, type 'help' for help")

        while self.run_console:
            user_in = input()

            # Used by stop command to ensure that the console quits it a stop command is
            # received over the network
            if user_in == "__stop":
                return

            self.cg.debug(f"Got input from stdin: '{user_in}'")
            self.cg.send_event("cg:console.stdin.recvline", {"data": user_in, "pipename": sys.stdin, "pipe": sys.stdin})

            sys.stdout.flush()

    def load_server_data(self):
        pass  # TODO: implement load

    # Event Handlers
    def register_event_handlers(self):
        self.cg.add_event_listener("cg:command.stop.do", self.handler_commandstop, cg.event.F_RAISE_ERRORS)
        self.cg.add_event_listener("cg:console.stdin.recvline", self.handler_consolerecvline, cg.event.F_RAISE_ERRORS)

    def handler_commandstop(self, event: str, data: Dict):
        # TODO: implement server stop

        # Ensure that the server console loop exits if a stop command is issued via the network
        self.run_console = False
        # TODO: actually interrupt the console loop

    def handler_consolerecvline(self, event: str, data: Dict):
        if data["data"].startswith("/"):
            # Removes a leading extraneous slash, while leaving double-slashes intact
            data["data"] = data["data"][1:]

        self.command_manager.exec_command(data["data"], self.command_manager.local_ctx)
