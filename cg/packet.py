#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  packet.py
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
from typing import List, Union, Dict, Any

import peng3dnet
from peng3dnet.constants import SIDE_CLIENT, SIDE_SERVER, CONNTYPE_CLASSIC

import cg
from cg.constants import MODE_CG

MAX_IGNORE_RECV = 10
MAX_IGNORE_SEND = 10


class CGPacket(peng3dnet.net.packet.SmartPacket):
    _ignorecount_recv: int = 0
    _ignorecount_send: int = 0

    required_keys: List[str] = []
    allowed_keys: List[str] = []

    conntype: str = CONNTYPE_CLASSIC
    mode: Union[int, None] = MODE_CG
    side = None

    peer: Union[peng3dnet.net.Server, peng3dnet.net.Client]

    def __init__(self,
                 reg: peng3dnet.PacketRegistry,
                 peer: Union[peng3dnet.Server, peng3dnet.Client],
                 obj=None,
                 c: cg.CardGame = None,
                 ):
        super().__init__(reg, peer, obj)

        self.cg = c

    def _receive(self, msg: Dict, cid: Union[int, None] = None):
        d = {
            "msg": msg,
            "cid": cid,
            "type": self.reg.getName(self),
        }

        if cid is None and (self.side is None or self.side == SIDE_CLIENT):
            # On the Client
            #self.cg.info(f"State: {self.peer.remote_state} Mode: {self.peer.mode} Conntype: {self.peer.conntype}")
            if (
                    self.check(self.peer.remote_state, self.state)
                    and self.check(self.peer.mode, self.mode)
                    and self.check(self.peer.conntype, self.conntype)
                    and self.check_keys(msg, self.required_keys, self.allowed_keys)
                    ):
                self.cg.send_event("cg:network.packet.recv", d)
                self.cg.send_event(f"cg:network.packet.[{self.reg.getName(self)}].recv", d)
                self.cg.send_event("cg:network.packet.recv.client", d)
                self.cg.send_event(f"cg:network.packet.[{self.reg.getName(self)}].recv.server", d)

                self.receive(msg, cid)

                return True
        elif cid is not None and (self.side is None or self.side == SIDE_SERVER):
            # On the server
            if (
                    self.check(self.peer.clients[cid].state, self.state)
                    and self.check(self.peer.clients[cid].mode, self.mode)
                    and self.check(self.peer.clients[cid].conntype, self.conntype)
                    and self.check_keys(msg, self.required_keys, self.allowed_keys)
                    ):
                self.cg.send_event("cg:network.packet.recv", d)
                self.cg.send_event(f"cg:network.packet.[{self.reg.getName(self)}].recv", d)
                self.cg.send_event("cg:network.packet.recv.server", d)
                self.cg.send_event(f"cg:network.packet.[{self.reg.getName(self)}].recv.server", d)

                self.receive(msg, cid)

                return True

        # If the packet was valid, it would have been handled by now
        # A fall-through means that invalid_action has to be executed

        if self.invalid_action == "ignore":
            if self._ignorecount_recv < MAX_IGNORE_RECV:
                self.cg.warn(f"Packet {self.reg.getName(self)} with message {msg} ignored on recv due to SmartPacket mismatch")
                self._ignorecount_recv += 1

            self.cg.send_event("cg:network.packet.ignore", d)
            self.cg.send_event(f"cg:network.packet.[{self.reg.getName(self)}].ignore", d)
            self.cg.send_event("cg:network.packet.recv.ignore", d)
            self.cg.send_event(f"cg:network.packet.[{self.reg.getName(self)}].recv.ignore", d)
        elif self.invalid_action == "close":
            self.peer.close_connection(cid, "smartpacketinvalid")
        else:
            raise peng3dnet.errors.InvalidSmartPacketActionError(f"Invalid Action '{self.invalid_action}'")

        return False

    def _send(self, msg: Dict, cid: Union[int, None] = None):
        d = {
            "msg": msg,
            "cid": cid,
            "type": self.reg.getName(self),
        }

        if cid is None and (self.side is None or self.side == SIDE_SERVER):
            # On the Client
            if (
                    self.check(self.peer.remote_state, self.state)
                    and self.check(self.peer.mode, self.mode)
                    and (self.conntype is None or self.peer.conntype == self.conntype)
                    ):
                self.cg.send_event("cg:network.packet.send", d)
                self.cg.send_event(f"cg:network.packet.[{self.reg.getName(self)}].send", d)
                self.cg.send_event("cg:network.packet.send.client", d)
                self.cg.send_event(f"cg:network.packet.[{self.reg.getName(self)}].send.server", d)

                self.send(msg, cid)

                return True
        elif cid is not None and (self.side is None or self.side == SIDE_CLIENT):
            # On the server
            if (
                    self.check(self.peer.clients[cid].state, self.state)
                    and self.check(self.peer.clients[cid].mode, self.mode)
                    and self.check(self.peer.clients[cid].conntype, self.conntype)
                    ):
                self.cg.send_event("cg:network.packet.send", d)
                self.cg.send_event(f"cg:network.packet.[{self.reg.getName(self)}].send", d)
                self.cg.send_event("cg:network.packet.send.server", d)
                self.cg.send_event(f"cg:network.packet.[{self.reg.getName(self)}].send.server", d)

                self.send(msg, cid)

                return True

        # If the packet was valid, it would have been handled by now
        # A fall-through means that invalid_action has to be executed

        if self.invalid_action == "ignore":
            if self._ignorecount_recv < MAX_IGNORE_RECV:
                self.cg.warn(f"Packet {self.reg.getName(self)} ignored on send due to SmartPacket mismatch")
                self._ignorecount_recv += 1

            self.cg.send_event("cg:network.packet.ignore", d)
            self.cg.send_event(f"cg:network.packet.[{self.reg.getName(self)}].ignore", d)
            self.cg.send_event("cg:network.packet.send.ignore", d)
            self.cg.send_event(f"cg:network.packet.[{self.reg.getName(self)}].send.ignore", d)
        elif self.invalid_action == "close":
            self.peer.close_connection(cid, "smartpacketinvalid")
        else:
            raise peng3dnet.errors.InvalidSmartPacketActionError(f"Invalid Action '{self.invalid_action}'")

        return False

    @staticmethod
    def check_keys(d: dict, required: list, allowed: list) -> bool:
        """
        Checks if all required keys and only allowed keys are present.

        If ``allowed`` is empty, it will be ignored.

        :param dict d:
        :param list required: List of required keys, may be empty
        :param list allowed: List of allowed keys, may be empty
        :return:
        """
        # TODO: implement logging of why this check failed

        for k in required:
            if k not in d.keys():
                return False

        if len(allowed) > 0:
            for k in d.keys():
                if k not in allowed:
                    return False

        return True

    @staticmethod
    def check(current: Any, allowed: Union[Any, List[Any]]) -> bool:
        """
        Helper method to check if a criteria is met.

        If ``allowed`` is a list, ``current`` must be in it. If it is not a list, ``allowed``
        must be either ``None`` or equal to ``current``\ .

        :param current: Current value
        :param allowed: Allowed value(s)
        :return: bool
        """
        if isinstance(allowed, list):
            return current in allowed
        else:
            return allowed is None or current == allowed