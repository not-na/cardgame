#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  status_user.py
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

from cg.constants import STATE_ACTIVE, STATE_GAME_DK, STATE_LOBBY, STATE_AUTH
from cg.packet import CGPacket
from cg.util import uuidify


class StatusUserPacket(CGPacket):
    state = [STATE_AUTH, STATE_ACTIVE, STATE_LOBBY, STATE_GAME_DK]
    required_keys = [
    ]
    allowed_keys = [
        "username",
        "uuid",
        "status",
        "pwd",
        "profile_img",
    ]

    def receive(self, msg, cid=None):
        if "uuid" in msg:
            u = self.peer.clients[cid].user

            # Request of an other player's user data by uuid
            if uuidify(msg["uuid"]) != u.uuid:
                self.cg.server.send_user_data(uuidify(msg["uuid"]), cid)

            # Updating of the own user data
            else:
                if "username" in msg:
                    if msg["username"] in self.cg.server.users:
                        self.cg.server.send_status_message(u, "warn", "cg:msg.status.user.username_not_available")
                        return
                    else:
                        del self.cg.server.users[u.username]
                        u.username = msg["username"]
                        self.cg.server.users[u.username] = u
                        self.cg.server.save_server_data()
                        # TODO Send not to everyone
                        for user in self.cg.server.users.values():
                            if user.cid is not None:
                                self.cg.server.send_user_data(u.uuid, user.uuid)

                if "pwd" in msg:
                    oldpwd = msg["pwd"][0]
                    newpwd = msg["pwd"][0]

                    if not u.check_password(oldpwd, update=False):
                        self.cg.server.send_status_message(u, "warn", "cg:msg.status.user.wrong_pwd")
                        return
                    u.set_pwd(newpwd.encode())
                    # if msg["pwd"][0] != u.pwd:
                    #     self.cg.server.send_status_message(u, "warn", "cg:msg.status.user.wrong_pwd")
                    #     return
                    # else:
                    #     u.pwd = msg["pwd"][1]
                    #     self.cg.server.save_server_data()
                    #     self.peer.send_message("cg:status.user", {
                    #         "uuid": u.uuid.hex,
                    #         "pwd": u.pwd
                    #     }, u.cid)

                if "profile_img" in msg:
                    if msg["profile_img"].strip() == "":
                        self.cg.server.send_status_message(u, "warn", "cg:msg.status.user.empty_img")
                        return
                    if len(msg["profile_img"]) > 64:
                        self.cg.server.send_status_message(u, "warn", "cg:msg.status.user.img_name_long")
                        return
                    u.profile_img = msg["profile_img"]
                    self.cg.server.save_server_data()

                    # TODO Send not to everyone
                    for user in self.cg.server.users.values():
                        if user.cid is not None:
                            self.cg.server.send_to_user(user, "cg:status.user", {
                                "uuid": u.uuid.hex,
                                "profile_img": u.profile_img
                            })

        # Request of an other player's user data by username
        elif "username" in msg:
            self.cg.server.send_user_data(msg["username"], cid)
        else:
            self.cg.error("Received cg:status.user packet with neither username nor uuid, ignoring")
            return
