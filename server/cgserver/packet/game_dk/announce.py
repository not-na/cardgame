#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  announce.py
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
from cg.constants import STATE_GAME_DK
from cg.packet import CGPacket


class AnnouncePacket(CGPacket):
    state = STATE_GAME_DK
    required_keys = [
        "type"
    ]
    allowed_keys = [
        "type",
        "data",
        "announcer"
    ]

    def receive(self, msg, cid=None):
        t = msg["type"]

        if t in ["reservation_yes", "reservation_no"]:
            self.cg.send_event("cg:game.dk.reservation", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t
            })

        elif t in ["solo_yes", "solo_no"]:
            if t == "solo_yes":
                if "data" not in msg:
                    raise KeyError(f"cg:game.dk.announce packet with type 'solo_yes' must contain the key 'data'!")
                elif "type" not in msg["data"]:
                    raise KeyError(
                        f"cg:game.dk.announce packet with type 'solo_yes' must contain 'data' containing key 'type'!")

            self.cg.send_event("cg:game.dk.reservation_solo", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t,
                "data": msg["data"] if t == "solo_yes" else {}
            })

        elif t in ["throw_yes", "throw_no"]:
            self.cg.send_event("cg:game.dk.reservation_throw", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t
            })

        elif t in ["pigs_yes", "pigs_no"]:
            self.cg.send_event("cg:game.dk.reservation_pigs", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t
            })

        elif t in ["superpigs_yes", "superpigs_no"]:
            self.cg.send_event("cg:game.dk.reservation_superpigs", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t
            })

        elif t in ["poverty_yes", "poverty_no"]:
            self.cg.send_event("cg:game.dk.reservation_poverty", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t
            })

        elif t in ["poverty_accept", "poverty_decline"]:
            self.cg.send_event("cg:game.dk.reservation_poverty_accept", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t
            })

        elif t == "poverty_return":
            if "data" not in msg:
                raise KeyError(f"cg:game.dk.announce packet with type 'poverty_return' must contain the key 'data'!")
            elif "amount" not in msg["data"]:
                raise KeyError(
                    f"cg:game.dk.announce packet with type 'poverty_return' must contain 'data' containing key 'amount'!")

            self.cg.send_event("cg:game.dk.reservation_poverty_accept", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t,
                "data": msg["data"]
            })

        elif t in ["wedding_yes", "wedding_no"]:
            self.cg.send_event("cg:game.dk.reservation_wedding", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t
            })

        elif t == "wedding_clarification_trick":
            if "data" not in msg:
                raise KeyError(
                    f"cg:game.dk.announce packet with type 'wedding_clarification_trick' must contain the key 'data'!")
            elif "trick" not in msg["data"]:
                raise KeyError(
                    f"cg:game.dk.announce packet with type 'wedding_clarification_trick' must contain 'data' containing key 'trick'!")

            self.cg.send_event("cg:game.dk.reservation_wedding_clarification_trick", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t,
                "data": msg["data"]
            })

        elif t == "pigs":
            self.cg.send_event("cg:game.dk.call_pigs", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t
            })

        elif t == "superpigs":
            self.cg.send_event("cg:game.dk.call_superpigs", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t
            })

        elif t in ["re", "kontra"]:
            self.cg.send_event("cg:game.dk.call_re", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t
            })

        elif t in ["no90", "no60", "no30", "black"]:
            self.cg.send_event("cg:game.dk.call_denial", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t
            })

        elif t == "black_sow_solo":
            if "data" not in msg:
                raise KeyError(f"cg:game.dk.announce packet with type 'solo_yes' must contain the key 'data'!")
            elif "type" not in msg["data"]:
                raise KeyError(
                    f"cg:game.dk.announce packet with type 'solo_yes' must contain 'data' containing key 'type'!")

            self.cg.send_event("cg:game.dk.black_sow_solo", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t,
                "data": msg["data"]
            })

        elif t == "throw":
            self.cg.send_event("cg:game.dk.throw", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t,
            })

        elif t == "ready":
            self.cg.send_event("cg:game.dk.ready", {
                "player": self.peer.clients[cid].user.uuid.hex,
                "type": t,
            })

        else:
            self.cg.warn(f"Unknown announce of type {t} from client {self.peer.clients[cid].user.uuid}!")
