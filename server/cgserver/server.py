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
import queue
import secrets
import socket
import sys
import time
import threading
import uuid
import heapq
from typing import Dict, Union, Type, Optional, Callable, List, Any, Tuple
from dataclasses import dataclass, field

import peng3dnet

import cg
import cgserver

from cg.constants import STATE_AUTH, MODE_CG, STATE_VERSIONCHECK
from cg.util import uuidify
from cg.util.serializer import msgpack


@dataclass(order=True)
class _ScheduledFunction:
    time: float
    func: Callable = field(compare=False)
    flags: int = field(compare=False)
    start_time: float = field(compare=False)
    args: Tuple[Any] = field(compare=False)
    kwargs: Dict[str, Any] = field(compare=False)


class CGServer(peng3dnet.ext.ping.PingableServerMixin, peng3dnet.net.Server):
    cg: cg.CardGame

    def getPingData(self, msg, cid):
        c = self.clients[cid]
        self.cg.info(f"Server Ping by Client #{cid} with IP Address {c.addr[0]}:{c.addr[1]}")

        return {
            "name": self.cg.get_config_option("cg:server.name"),
            "visiblename": self.cg.get_config_option("cg:server.visiblename"),
            "slogan": self.cg.get_config_option("cg:server.slogan"),
            "maxplayers": self.cg.get_config_option("cg:server.maxplayers"),
            #"canonical_address": socket.getfqdn(),
            "playercount": 0,  # TODO: implement player count
            "playerlist": [],  # TODO: implement player list
            "canlogon": True,  # TODO: implement properly
            "version": self.cg.get_proto_version(),
            "flavor": cgserver.version.FLAVOR,
            "timestamp": time.time(),
        }


class ClientOnCGServer(peng3dnet.net.ClientOnServer):
    user: Optional[cgserver.user.User] = None

    def on_handshake_complete(self):
        super().on_handshake_complete()

        self.state = STATE_VERSIONCHECK
        self.mode = MODE_CG
        self.user = None

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

        if self.user is not None:
            self.user.cid = None

            if self.user.lobby is not None:
                self.server.cg.info(f"Removing user {self.user.username} from lobby due to disconnect")
                self.server.cgserver.lobbies[self.user.lobby].remove_user(self.user.uuid, left=True)
                self.user.lobby = None

            if self.user.cur_game is not None:
                self.server.cg.warn(f"User {self.user.username} was still in a game on disconnect")
                # TODO: allow reconnect after disconnect

                # Check if the game is now "empty", and if so, delete it
                g = self.server.cgserver.games[self.user.cur_game]
                if not any([uid in self.server.cgserver.users_uuid and self.server.cgserver.users_uuid[uid].cid is not None for uid in g.players]):
                    # Delete the game
                    g.delete()
                    del self.server.cgserver.games[self.user.cur_game]
                    del g

                self.user.cur_game = None

        self.server.cg.info(f"Connection to client {self.cid} closed due to '{reason}'")

        self.server.cg.send_event("cg:network.server.closeconn",
                                  {
                                      "clientonserver": self,
                                      "server": self.server,
                                      "addr": self.addr,
                                      "conntype": self.conntype,
                                  }
                                  )


class DedicatedServer(object):
    PROCESS_TIMEOUT = 0.01

    command_manager = cgserver.command.CommandManager

    def __init__(self, c: cg.CardGame, addr=None, port=None):
        self.cg = c

        self.cg.set_channel_from_file("channel.txt")
        cg.util.print_version_information(self.cg, cgserver.version)
        self.cg.check_for_updates()

        self.register_event_handlers()

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

        self.cg.debug(f"Packet Registry: {dict(self.server.registry.reg_int_str.inv)}")

        self.game_reg: Dict[str, cgserver.game.CGame] = {}

        self.cg.send_event("cg:game.register.do", {
            "registrar": self.register_game,
        })

        self.bot_reg: Dict[str, cgserver.game.bot.Bot] = {}

        self.cg.send_event("cg:bot.register.do", {
            "registrar": self.register_bot,
        })

        self.secret: Optional[str] = None

        self.lobbies: Dict[uuid.UUID, cgserver.lobby.Lobby] = {}

        self.serverid: Union[None, uuid.UUID] = None

        self.games: Dict[uuid.UUID, cgserver.game.CGame] = {}

        self.users: Dict[str, cgserver.user.User] = {}
        self.users_uuid: Dict[uuid.UUID, cgserver.user.User] = {}

        self.run_console = False
        self.interactive_thread = None

        self.process_thread: Optional[threading.Thread] = None

        self.scheduled_events: List[_ScheduledFunction] = []
        self.event_queue = queue.Queue()
        self.process_lock = threading.Lock()

    def start(self):
        self.start_listening()

        self.run_interactive_console()

    def start_listening(self):
        self.server.runAsync()
        #self.server.process_async()

        self.process_thread = threading.Thread(name="Network Processing Thread", target=self.run_process)
        self.process_thread.daemon = True
        self.process_thread.start()

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

    def run_process(self):
        while self.server.run:
            self.server.process(wait=True, timeout=self.PROCESS_TIMEOUT)

            if not self.event_queue.empty():
                try:
                    event, data = self.event_queue.get_nowait()
                except queue.Empty:
                    pass
                else:
                    self.cg.send_event(event, data)

            sched_func = None
            with self.process_lock:
                if len(self.scheduled_events) > 0 and self.scheduled_events[0].time <= time.time():
                    sched_func = heapq.heappop(self.scheduled_events)

            if sched_func is not None:
                try:
                    sched_func.func(time.time() - sched_func.start_time, *sched_func.args, **sched_func.kwargs)
                except Exception:
                    self.cg.error(f"Error while calling scheduled function:")
                    self.cg.exception("Exception within scheduled function")

            self.cg.process_async_events()

    def schedule_function(self, func: Callable, delay: float, flags=0, *args, **kwargs):
        with self.process_lock:
            sched_func = _ScheduledFunction(time.time()+delay, func, flags, time.time(), args, kwargs)
            heapq.heappush(self.scheduled_events, sched_func)

    def load_server_data(self):
        fname = self.cg.get_settings_path("serverdat.csd")

        # First, check if the data file exists and is a file
        if not (os.path.exists(fname) and os.path.isfile(fname)):
            self.cg.warn("Generating new server data because serverdat.csd was not found")
            self.gen_server_data()
            return

        # Try to open it safely
        try:
            with open(fname, "rb") as f:
                data = msgpack.load(f)
        except Exception:
            self.cg.error("Could not load server data from file, probably broken")
            self.cg.exception("Exception during server data load:")
            self.gen_server_data()
            return

        # Check if the data is valid
        if "serverid" not in data or "users" not in data:
            self.cg.warn("Generating new server identity because necessary data is missing")
            self.cg.info(f"Old Server Data: {data}")
            self.gen_server_data()
            return

        self.serverid = uuidify(data["serverid"])

        if "secret" not in data:
            self.secret = secrets.token_bytes(self.cg.get_config_option("cg:server.secret_length"))
        else:
            self.secret = data["secret"]

        for user, udat in data["users"].items():
            u = cgserver.user.User(self, self.cg, user, udat)
            self.users[user] = u
            self.users_uuid[u.uuid] = u

        self.cg.info(f"Successfully loaded server data! {len(data['users'])} Users found")

    def gen_server_data(self):
        self.serverid = uuid.uuid4()
        self.secret = secrets.token_bytes(self.cg.get_config_option("cg:server.secret_length"))

        self.save_server_data()

    def save_server_data(self):
        self.cg.info("Saving server data")

        users = {}
        for name, u in self.users.items():
            if isinstance(u, cgserver.user.BotUser):
                continue
            users[u.username] = u.serialize()

        fname = self.cg.get_settings_path("serverdat.csd")
        data = {
            "serverid": self.serverid.hex,
            "secret": self.secret,
            "users": users,
        }

        with open(fname, "wb") as f:
            msgpack.dump(data, f)

    def register_game(self, name: str, cls: Type[cgserver.game.CGame]):
        self.game_reg[name] = cls

    def register_bot(self, name: str, cls: Type[cgserver.game.bot.Bot]):
        self.bot_reg[name] = cls

    def send_user_data(self, user: Union[uuid.UUID, str], client: Union[int, uuid.UUID, cgserver.user.User]):
        if isinstance(user, uuid.UUID):
            if user not in self.users_uuid:
                self.cg.warn(f"Could not find user with UUID {user}")
                return
            u = self.users_uuid[user]
        else:
            if user not in self.users:
                self.cg.warn(f"Could not find user with name {user}")
                return
            u = self.users[user]

        self.send_to_user(client, "cg:status.user", {
            "username": u.username,
            "uuid": u.uuid.hex,
            "profile_img": u.profile_img,

            "status": "offline",  # TODO: implement correctly
        })

    def send_to_user(self, user: Union[uuid.UUID, cgserver.user.User, int], packet: str, data: dict):
        if isinstance(user, uuid.UUID):
            if user not in self.users_uuid:
                self.cg.error(f"Could not send packet {packet} to user {user} because it does not exist")
                return
            user = self.users_uuid[user]
        elif isinstance(user, int):
            return self.server.send_message(packet, data, user)

        if isinstance(user, cgserver.user.BotUser):
            self.cg.send_event(f"cg:bot.[{user.uuid.hex}].packet.recv", {"packet": packet, "data": data})
            return

        if user.cid is None:
            self.cg.error(f"Could not send packet {packet} to user {user.username} because they are not connected")

        self.server.send_message(packet, data, user.cid)

    def send_status_message(self, user: Union[uuid.UUID, cgserver.user.User], t: str, msg: str, data: Optional[Dict] = None):
        if data is None:
            data = {}

        self.cg.info(f"Send status message to {user} with type {t} and message {msg} ({data})")
        self.send_to_user(user, "cg:status.message", {
            "type": t,
            "message": msg,
            "data": data,
        })

    # Event Handlers
    def register_event_handlers(self):
        self.cg.add_event_listener("cg:command.stop.do", self.handler_commandstop)
        self.cg.add_event_listener("cg:event.delay", self.handler_eventdelay)
        self.cg.add_event_listener("cg:console.stdin.recvline", self.handler_consolerecvline)

        self.cg.add_event_listener("cg:network.packets.register.do", self.handler_dopacketregister)
        self.cg.add_event_listener("cg:network.client.login", self.handler_netclientlogin)

        self.cg.add_event_listener("cg:game.register.do", self.handler_dogameregister)
        self.cg.add_event_listener("cg:bot.register.do", self.handler_dobotregister)

        self.cg.add_event_listener("cg:stats.game.new", self.handler_statsnew)

    def handler_commandstop(self, event: str, data: Dict):
        # Ensure that the server console loop exits if a stop command is issued via the network
        self.run_console = False
        # TODO: actually interrupt the console loop

    def handler_eventdelay(self, event: str, data: Dict):
        # Schedule event to be run later
        self.schedule_function(
            self._send_event,
            data["delay"],
            0,
            event=data["event"],
            data=data["data"],
        )

    def handler_consolerecvline(self, event: str, data: Dict):
        if data["data"].startswith("/"):
            # Removes a leading extraneous slash, while leaving double-slashes intact
            data["data"] = data["data"][1:]

        self.command_manager.exec_command(data["data"], self.command_manager.local_ctx)

    def handler_dopacketregister(self, event: str, data: Dict):
        cgserver.packet.register_default_packets(data["reg"], data["peer"], self.cg, data["registrar"])

    def handler_netclientlogin(self, event: str, data: Dict):
        pass

    def handler_dogameregister(self, event: str, data: Dict):
        cgserver.game.register_games(data["registrar"])

    def handler_dobotregister(self, event: str, data: Dict):
        cgserver.game.bot.register_bots(data["registrar"])

    def handler_statsnew(self, event: str, data: Dict):
        statdir = self.cg.get_settings_path("gamestats")
        statdir = os.path.join(statdir, data["game_type"])

        # Ensure directory exists
        os.makedirs(statdir, exist_ok=True)

        fname = os.path.join(statdir, f"{data['game_id']}.cgs")

        self.cg.info(f"Saving statistics for game {data['game_id']}")

        if os.path.exists(fname):
            self.cg.warn(f"Overwriting old statistics for game {data['game_id']}")

        with open(fname, "wb") as f:
            msgpack.dump(data, f)

    def _send_event(self, dt, event, data):
        self.cg.send_event(event, data)
