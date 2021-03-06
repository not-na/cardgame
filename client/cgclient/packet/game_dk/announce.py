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
from cg.util import uuidify


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
        if self.cg.client.game is None:
            self.cg.error("Received announce packet although not being in a game!")
            return
        if "announcer" not in msg:
            self.cg.warn("Received AnnouncePacket on client without announcer!")
            return
        self.cg.info(f"Announce: {msg}")

        if msg["type"] == "continue_yes":
            self.cg.client.game.player_decisions["continue"].add(msg["announcer"])

            label = "cg:gui.menu.ingame.scoreboard.continuebtn.label"
            data = {}
            if len(self.cg.client.game.player_decisions["continue"]) > 0:
                label = "cg:gui.menu.ingame.scoreboard.continuebtn.label2"
                data = {"amount": len(self.cg.client.game.player_decisions["continue"])}

            self.cg.client.gui.ingame.gui_layer.s_scoreboard.continuebtn.label = self.cg.client.gui.peng.tl(
                label, data
            )
        elif msg["type"] == "continue_no":
            self.cg.client.game.player_decisions["continue"].discard(msg["announcer"])

            label = "cg:gui.menu.ingame.scoreboard.continuebtn.label"
            data = {}
            if len(self.cg.client.game.player_decisions["continue"]) > 0:
                label = "cg:gui.menu.ingame.scoreboard.continuebtn.label2"
                data = {"amount": len(self.cg.client.game.player_decisions["continue"])}

            self.cg.client.gui.ingame.gui_layer.s_scoreboard.continuebtn.label = self.cg.client.gui.peng.tl(
                label, data
            )
        elif msg["type"] == "adjourn_yes":
            self.cg.client.game.player_decisions["adjourn"].add(msg["announcer"])

            label = "cg:gui.menu.ingame.scoreboard.adjournbtn.label"
            data = {}
            if len(self.cg.client.game.player_decisions["adjourn"]) > 0:
                label = "cg:gui.menu.ingame.scoreboard.adjournbtn.label2"
                data = {"amount": len(self.cg.client.game.player_decisions["adjourn"])}

            self.cg.client.gui.ingame.gui_layer.s_scoreboard.adjournbtn.label = self.cg.client.gui.peng.tl(
                label, data
            )
        elif msg["type"] == "adjourn_no":
            self.cg.client.game.player_decisions["adjourn"].discard(msg["announcer"])

            label = "cg:gui.menu.ingame.scoreboard.adjournbtn.label"
            data = {}
            if len(self.cg.client.game.player_decisions["adjourn"]) > 0:
                label = "cg:gui.menu.ingame.scoreboard.adjournbtn.label2"
                data = {"amount": len(self.cg.client.game.player_decisions["adjourn"])}

            self.cg.client.gui.ingame.gui_layer.s_scoreboard.adjournbtn.label = self.cg.client.gui.peng.tl(
                label, data
            )
        elif msg["type"] == "end_yes":
            self.cg.client.game.player_decisions["end"].add(msg["announcer"])

            label = "cg:gui.menu.ingame.scoreboard.quitbtn.label"
            data = {}
            if len(self.cg.client.game.player_decisions["end"]) > 0:
                label = "cg:gui.menu.ingame.scoreboard.quitbtn.label2"
                data = {"amount": len(self.cg.client.game.player_decisions["end"])}

            self.cg.client.gui.ingame.gui_layer.s_scoreboard.quitbtn.label = self.cg.client.gui.peng.tl(
                label, data
            )
        elif msg["type"] == "end_no":
            self.cg.client.game.player_decisions["end"].discard(msg["announcer"])

            label = "cg:gui.menu.ingame.scoreboard.quitbtn.label"
            data = {}
            if len(self.cg.client.game.player_decisions["end"]) > 0:
                label = "cg:gui.menu.ingame.scoreboard.quitbtn.label2"
                data = {"amount": len(self.cg.client.game.player_decisions["end"])}

            self.cg.client.gui.ingame.gui_layer.s_scoreboard.quitbtn.label = self.cg.client.gui.peng.tl(
                label, data
            )
        elif msg["type"] == "cancel_yes":
            self.cg.client.game.player_decisions["cancel"].add(msg["announcer"])

            label = "cg:gui.menu.ingame.scoreboard.cancelbtn.label"
            data = {}
            if len(self.cg.client.game.player_decisions["cancel"]) > 0:
                label = "cg:gui.menu.ingame.scoreboard.cancelbtn.label2"
                data = {"amount": len(self.cg.client.game.player_decisions["cancel"])}

            self.cg.client.gui.ingame.gui_layer.s_scoreboard.cancelbtn.label = self.cg.client.gui.peng.tl(
                label, data
            )
        elif msg["type"] == "cancel_no":
            self.cg.client.game.player_decisions["cancel"].discard(msg["announcer"])

            label = "cg:gui.menu.ingame.scoreboard.cancelbtn.label"
            data = {}
            if len(self.cg.client.game.player_decisions["cancel"]) > 0:
                label = "cg:gui.menu.ingame.scoreboard.cancelbtn.label2"
                data = {"amount": len(self.cg.client.game.player_decisions["cancel"])}

            self.cg.client.gui.ingame.gui_layer.s_scoreboard.cancelbtn.label = self.cg.client.gui.peng.tl(
                label, data
            )

        if msg["type"] == "ready":
            if uuidify(msg["announcer"]) == self.cg.client.user_id:
                self.cg.client.gui.ingame.gui_layer.s_ingame.readybtn.visible = False
                self.cg.client.gui.ingame.gui_layer.s_ingame.throwbtn.visible = False
        elif msg["type"] == "pigs":
            if self.cg.client.lobby.gamerules["dk.superpigs"] in ["on_pig", "on_play"]:
                self.cg.client.gui.ingame.gui_layer.s_ingame.pigsbtn.visible = True
                self.cg.client.gui.ingame.gui_layer.s_ingame.pigsbtn.purpose = "superpigs"
                self.cg.client.gui.ingame.gui_layer.s_ingame.pigsbtn.label = self.cg.client.gui.peng.tl(
                    "cg:gui.menu.ingame.ingamegui.pigsbtn.superpigs")
            else:
                self.cg.client.gui.ingame.gui_layer.s_ingame.pigsbtn.visible = False
                self.cg.client.gui.ingame.gui_layer.s_ingame.pigsbtn.purpose = "None"
        elif msg["type"] == "pigs_yes":
            if self.cg.client.lobby.gamerules["dk.superpigs"] in ["on_pig", "on_play"]:
                self.cg.client.gui.ingame.gui_layer.s_ingame.pigsbtn.should_visible = True
                self.cg.client.gui.ingame.gui_layer.s_ingame.pigsbtn.purpose = "superpigs"
                self.cg.client.gui.ingame.gui_layer.s_ingame.pigsbtn.label = self.cg.client.gui.peng.tl(
                    "cg:gui.menu.ingame.ingamegui.pigsbtn.superpigs")
            else:
                self.cg.client.gui.ingame.gui_layer.s_ingame.pigsbtn.visible = False
                self.cg.client.gui.ingame.gui_layer.s_ingame.pigsbtn.purpose = "None"
        elif msg["type"] == "superpigs":
            self.cg.client.gui.ingame.gui_layer.s_ingame.pigsbtn.visible = False
            self.cg.client.gui.ingame.gui_layer.s_ingame.pigsbtn.purpose = "None"

        if msg["type"] in ["poverty_decline", "poverty_yes"]:
            # Set the poverty slot to be in front of the next player

            nname = self.cg.client.game.uuid_to_side(uuidify(msg["announcer"]), 1)

            self.cg.client.game.poverty_pos = nname

            for c in self.cg.client.game.slots["poverty"]:
                c.start_anim("poverty", "poverty")

        nname = self.cg.client.game.uuid_to_side(uuidify(msg["announcer"]))
        if msg["type"] in [
            "reservation_yes",
            "reservation_no",
            "solo_yes",
            "solo_no",
            "throw_yes",
            "throw_no",
            "pigs_yes",
            "pigs_no",
            "superpigs_yes",
            "superpigs_no",
            "poverty_yes",
            "poverty_no",
            "poverty_accept",
            "poverty_decline",
            "poverty_return",
            "wedding_yes",
            "wedding_no",
            "wedding_clarification_trick",
            "pigs",
            "superpigs",
            "re",
            "kontra",
            "no90",
            "no60",
            "no30",
            "black",
            "black_sow_solo",
            "throw",
            "ready",
        ]:
            # Display the announce on-screen
            peng = self.cg.client.gui.peng
            i18n = peng.i18n

            # Black sow solo
            if msg['type'] == "black_sow_solo":
                msg['type'] = "solo_yes"

            # Check if the key exists and fall back otherwise
            if f"announce.{msg['type']}.key" not in i18n.cache[i18n.lang]["cg"]:
                key = f"cg:announce.{msg['type']}"
            else:
                key = str(peng.tl(f"cg:announce.{msg['type']}.key", data=msg.get("data", {})))

            self.cg.client.gui.ingame.hud_layer.s_main.announces[nname].set_announce(key, msg.get("data", {}))
