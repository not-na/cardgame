#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  servermain.py
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
import glob
import math
import re
import time
from typing import Tuple, Union, Dict

import peng3d

import cgclient.gui
import pyglet
from pyglet.window.mouse import LEFT

from cg.constants import ROLE_ADMIN

GAMES = [
    "sk",  # Skat
    "dk",  # Doppelkopf
    "rm",  # Romme
    "cn",  # Canasta
]

GAME_VARIANTS = [
    "c",  # Custom
    "m",  # Modified
    "s",  # Standard
]

ALLOWED_GAMES = [
    "dkc",
]

GAME_TO_NAME = {
    "sk": "skat",
    "dk": "doppelkopf",
    "rm": "romme",
    "cn": "canasta",
}


class ServerMainMenu(peng3d.gui.GUIMenu):
    def __init__(self, name, window, peng, gui):
        super().__init__(name, window, peng,
                         font="Times New Roman",
                         font_size=25,
                         font_color=[255, 255, 255, 100],
                         )
        self.gui = gui
        self.cg = gui.cg

        self.register_event_handlers()

        self.setBackground(peng3d.gui.button.FramedImageBackground(
            peng3d.gui.FakeWidget(self),
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )
        self.bg.vlist_layer = -1

        # Loading Screen
        self.d_load = peng3d.gui.TextSubMenu(
            "load", self, self.window, self.peng,
            label_main=self.peng.tl("cg:gui.menu.smain.load.load"),
            timeout=-1
        )
        self.addSubMenu(self.d_load)

        # Create Account Dialog
        self.d_create_acc = peng3d.gui.menus.ConfirmSubMenu(
            "create_acc", self, self.window, self.peng,
            label_confirm=self.peng.tl("cg:gui.menu.smain.create_acc.confirm"),
            label_cancel=self.peng.tl("cg:gui.menu.smain.create_acc.cancel"),
            label_main=self.peng.tl("cg:gui.menu.smain.create_acc.label_main"),
        )
        self.d_create_acc.wbtn_confirm.setBackground(peng3d.gui.FramedImageBackground(
            self.d_create_acc.wbtn_confirm,
            bg_idle=("cg:img.btn.btn_idle", "gui"),
            bg_hover=("cg:img.btn.btn_hov", "gui"),
            bg_pressed=("cg:img.btn.btn_press", "gui"),
            frame=[[249, 502, 249], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        )
        )
        self.d_create_acc.wbtn_cancel.setBackground(peng3d.gui.FramedImageBackground(
            self.d_create_acc.wbtn_cancel,
            bg_idle=("cg:img.btn.btn_idle", "gui"),
            bg_hover=("cg:img.btn.btn_hov", "gui"),
            bg_pressed=("cg:img.btn.btn_press", "gui"),
            frame=[[249, 502, 249], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        )
        )
        self.d_create_acc.wbtn_confirm.pos = lambda sw, sh, bw, bh: (sw / 2 - bw - 5, sh / 2 - bh * 2)
        self.d_create_acc.wbtn_confirm.size = lambda sw, sh: (sw / 5, 64)
        self.d_create_acc.wbtn_cancel.pos = lambda sw, sh, bw, bh: (sw / 2 + 5, sh / 2 - bh * 2)
        self.d_create_acc.wbtn_cancel.size = lambda sw, sh: (sw / 5, 64)
        self.addSubMenu(self.d_create_acc)

        def f():
            self.cg.client.send_message("cg:auth", {
                "username": self.s_login.user.text.strip(),
                "pwd": self.s_login.pwd.text,
                "create": True,
            })

        self.d_create_acc.addAction("confirm", f)

        def f():
            self.d_create_acc.prev_submenu = "login"

        self.d_create_acc.addAction("cancel", f)

        # Error Dialog
        self.d_login_err = peng3d.gui.menus.DialogSubMenu(
            "login_err", self, self.window, self.peng,
            label_main=self.peng.tl("cg:gui.menu.smain.loginerr.unknown"),
            label_ok=self.peng.tl("cg:gui.menu.smain.loginerr.ok"),
        )
        self.d_login_err.wbtn_ok.setBackground(peng3d.gui.FramedImageBackground(
            self.d_login_err.wbtn_ok,
            bg_idle=("cg:img.btn.btn_idle", "gui"),
            bg_hover=("cg:img.btn.btn_hov", "gui"),
            bg_pressed=("cg:img.btn.btn_press", "gui"),
            frame=[[249, 502, 249], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True,
            repeat_center=True,
        )
        )
        self.addSubMenu(self.d_login_err)

        # Lobby Invitation Dialog
        self.d_lobby_inv = peng3d.gui.menus.ConfirmSubMenu(
            "lobby_inv", self, self.window, self.peng,
            label_confirm=self.peng.tl("cg:gui.menu.smain.lobby_inv.confirm"),
            label_cancel=self.peng.tl("cg:gui.menu.smain.lobby_inv.cancel"),
            label_main=self.peng.tl("cg:gui.menu.smain.lobby_inv.label_main"),
        )
        self.d_lobby_inv.wbtn_confirm.setBackground(peng3d.gui.FramedImageBackground(
            self.d_lobby_inv.wbtn_confirm,
            bg_idle=("cg:img.btn.btn_idle", "gui"),
            bg_hover=("cg:img.btn.btn_hov", "gui"),
            bg_pressed=("cg:img.btn.btn_press", "gui"),
            frame=[[249, 502, 249], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        )
        )
        self.d_lobby_inv.wbtn_cancel.setBackground(peng3d.gui.FramedImageBackground(
            self.d_lobby_inv.wbtn_cancel,
            bg_idle=("cg:img.btn.btn_idle", "gui"),
            bg_hover=("cg:img.btn.btn_hov", "gui"),
            bg_pressed=("cg:img.btn.btn_press", "gui"),
            frame=[[249, 502, 249], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        )
        )
        self.d_lobby_inv.wbtn_confirm.pos = lambda sw, sh, bw, bh: (sw / 2 - bw - 5, sh / 2 - bh * 2)
        self.d_lobby_inv.wbtn_confirm.size = lambda sw, sh: (sw / 5, 64)
        self.d_lobby_inv.wbtn_cancel.pos = lambda sw, sh, bw, bh: (sw / 2 + 5, sh / 2 - bh * 2)
        self.d_lobby_inv.wbtn_cancel.size = lambda sw, sh: (sw / 5, 64)
        self.addSubMenu(self.d_lobby_inv)

        def f():
            self.cg.client.send_message("cg:lobby.invite.accept", {
                "accepted": True,
                "lobby_id": self.cg.client.lobby_invitation[1].hex,
                "inviter": self.cg.client.lobby_invitation[0].hex,
            })

        self.d_lobby_inv.addAction("confirm", f)

        def f():
            self.cg.client.send_message("cg:lobby.invite.accept", {
                "accepted": False,
                "lobby_id": self.cg.client.lobby_invitation[1].hex,
                "inviter": self.cg.client.lobby_invitation[0].hex,
            })

        self.d_lobby_inv.addAction("cancel", f)

        # Status Message Menu
        self.d_status_message = peng3d.gui.menus.DialogSubMenu(
            "status_msg", self, self.window, self.peng
        )
        self.d_status_message.label_ok = self.peng.tl("cg:gui.menu.status_msg.okbtn.label")
        self.d_status_message.wbtn_ok.setBackground(peng3d.gui.FramedImageBackground(
            self.d_status_message.wbtn_ok,
            bg_idle=("cg:img.btn.btn_idle", "gui"),
            bg_hover=("cg:img.btn.btn_hov", "gui"),
            bg_pressed=("cg:img.btn.btn_press", "gui"),
            frame=[[249, 502, 249], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        )
        )
        self.addSubMenu(self.d_status_message)

        def f():
            self.peng.cg.send_event("cg:status.message.close")

        self.d_status_message.wbtn_ok.addAction("click", f)

        # Login Menu
        self.s_login = LoginSubMenu("login", self, self.window, self.peng)
        self.addSubMenu(self.s_login)

        # Main Menu
        self.s_main = MainSubMenu("main", self, self.window, self.peng)
        self.addSubMenu(self.s_main)

        # Lobby Menu
        self.s_lobby = LobbySubMenu("lobby", self, self.window, self.peng)
        self.addSubMenu(self.s_lobby)

        # Template Menu
        self.s_template = TemplateSubMenu("template", self, self.window, self.peng)
        self.addSubMenu(self.s_template)

        # Gamerule Menu
        self.s_gamerule = GameruleSubMenu("gamerules", self, self.window, self.peng)
        self.addSubMenu(self.s_gamerule)

        self.changeSubMenu("load")

    def register_event_handlers(self):
        self.cg.add_event_listener("cg:status.message.open", self.status_message_open)
        self.cg.add_event_listener("cg:status.message.close", self.status_message_close)

    def status_message_open(self, event: str, data: dict):
        self.changeSubMenu("status_msg")
        self.d_status_message.label_main = self.peng.tl(data["message"], data["data"])

    def status_message_close(self, event: str, data: dict):
        self.d_status_message.exitDialog()


class LoginSubMenu(peng3d.gui.SubMenu):
    menu: ServerMainMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [3, 16], [0, 15])

        # Username Field
        default_user = self.menu.cg.client.username if self.menu.cg.client.username is not None else ""
        self.user = cgclient.gui.CGTextInput(
            "user", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 9], [1, 1]),
            text=default_user,
            font_size=20
        )
        self.addWidget(self.user)

        # Password Field
        # TODO: use an actual password field
        default_pwd = self.menu.cg.client.pwd if self.menu.cg.client.pwd is not None else ""
        self.pwd = cgclient.gui.CGTextInput(
            "pwd", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 8], [1, 1]),
            text=default_pwd,
            font_size=20
        )
        self.addWidget(self.pwd)

        # OK Button
        self.okbtn = cgclient.gui.CGButton(
            "okbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 6], [1, 2]),
            label=self.peng.tl("cg:gui.menu.smain.login.okbtn.label"),
        )
        self.addWidget(self.okbtn)

        def f():
            if self.pwd.text.strip() != "" and self.user.text.strip() != "":
                self.menu.cg.client.send_message("cg:auth.precheck", {
                    "username": self.user.text.strip(),
                })

                self.menu.changeSubMenu("load")
                self.menu.d_load.label_main = self.peng.tl("cg:gui.menu.smain.load.login")

        self.okbtn.addAction("click", f)


class MainSubMenu(peng3d.gui.SubMenu):
    menu: ServerMainMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.register_event_handlers()

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [3, 8], [60, 30])

        # Background
        self.setBackground(peng3d.gui.FramedImageBackground(
            self,
            bg_idle=("cg:img.bg.bg", "bg"),
            frame=[[0, 1, 0], [0, 1, 0]],
            scale=(.5, .5),
            repeat_edge=True, repeat_center=True,
        )
        )
        self.bg.vlist_layer = -2

        # Left sidebar (background)
        self.sidebar = peng3d.gui.Widget(
            "sidebar", self, self.window, self.peng,
            pos=(0, 0),
            size=(lambda sw, sh: (sw / 3, sh)),
        )
        self.sidebar.setBackground(peng3d.gui.FramedImageBackground(
            self.sidebar,
            bg_idle=("cg:img.bg.sidebar", "gui"),
            frame=[[1, 1, 10], [0, 1, 0]],
            scale=(.3, 0),
        )
        )
        self.sidebar.bg.vlist_layer = -1
        self.sidebar.clickable = False
        self.addWidget(self.sidebar)

        # Screen Edge
        self.screen_edge = peng3d.gui.Widget(
            "screen_edge", self, self.window, self.peng,
            pos=(0, 0),
            size=(lambda sw, sh: (sw, sh))
        )
        self.screen_edge.setBackground(peng3d.gui.FramedImageBackground(
            self.screen_edge,
            bg_idle=("cg:img.bg.bg_trans", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )
        self.screen_edge.clickable = False
        self.addWidget(self.screen_edge)

        def f1(button):
            # Reset the previously pressed button
            self.profile_label.pressed = self.profile_label._pressed
            for btn in self.togglebuttons:
                if btn != button and btn.pressed:
                    btn.pressed = False
                    btn.doAction("press_up")
                    btn.redraw()
            self.profile_label._pressed = self.profile_label.pressed

        self.subgrid_1 = peng3d.gui.layout.GridLayout(self.peng, self.grid.get_cell([0, 5], [1, 3]),
                                                      [4, 4], [60, 20])

        pos_x = self.subgrid_1.get_cell([1, 1], [2, 3], "center", "center").pos[0] / self.window.width
        pos_y = self.subgrid_1.get_cell([1, 1], [2, 3], "center", "center").pos[1] / self.window.height
        sy = self.subgrid_1.get_cell([1, 1], [2, 3]).size[1] / self.window.height

        # Profile Image
        self.profile_img = peng3d.gui.ToggleButton(
            "profileimg", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw * pos_x - (bw / 2), sh * pos_y - (bh / 2))),
            size=(lambda sw, sh: (sh * sy, sh * sy)),
            label="",
        )
        self.profile_img.setBackground(peng3d.gui.ImageBackground(
            self.profile_img,
            bg_idle=("cg:profile.default", "gui"),
        ))
        self.addWidget(self.profile_img)

        def f():
            self.c_profile_img.visible = True

        self.profile_img.addAction("press_down", f1, self.profile_img)
        self.profile_img.addAction("press_down", f)

        def f():
            self.c_profile_img.visible = False

        self.profile_img.addAction("press_up", f)

        # Profile Label
        self.profile_label = peng3d.gui.Label(
            "profilelbl", self, self.window, self.peng,
            pos=self.subgrid_1.get_cell([0, 0], [4, 1]),
            label="<unknown>",  # This should be the username
            anchor_x="center",
            anchor_y="center",
        )
        self.addWidget(self.profile_label)
        self.profile_label._pressed = False

        def f():
            if self.profile_label._pressed:
                self.profile_label.doAction("press_up")
                self.profile_label._pressed = False
            else:
                self.profile_label.doAction("press_down")
                self.profile_label._pressed = True

        self.profile_label.addAction("click", f)

        def f():
            self.c_upwd.visible = True

        self.profile_label.addAction("press_down", f1, self.profile_label)
        self.profile_label.addAction("press_down", f)

        def f():
            self.c_upwd.visible = False

        self.profile_label.addAction("press_up", f)

        # Play Button
        # This button opens the play_select container
        self.playbtn = peng3d.gui.ToggleButton(
            "playbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 4], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.main.playbtn.label"),
        )
        self.playbtn.setBackground(peng3d.gui.FramedImageBackground(
            self.playbtn,
            bg_idle=("cg:img.btn.btn_idle", "gui"),
            bg_hover=("cg:img.btn.btn_hov", "gui"),
            bg_pressed=("cg:img.btn.btn_press", "gui"),
            bg_disabled=("cg:img.btn.btn_disabled", "gui"),
            frame=[[1, 2, 1], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        ))

        def f():
            self.c_play.visible = True

        self.playbtn.addAction("press_down", f1, self.playbtn)
        self.playbtn.addAction("press_down", f)

        def f():
            self.c_play.visible = False

        self.playbtn.addAction("press_up", f)
        self.addWidget(self.playbtn)

        # Create Party Button
        # This button opens the party container
        self.partybtn = peng3d.gui.ToggleButton(
            "partybtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 3], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.main.partybtn.label")
        )
        self.partybtn.setBackground(peng3d.gui.FramedImageBackground(
            self.partybtn,
            bg_idle=("cg:img.btn.btn_idle", "gui"),
            bg_hover=("cg:img.btn.btn_hov", "gui"),
            bg_pressed=("cg:img.btn.btn_press", "gui"),
            bg_disabled=("cg:img.btn.btn_disabled", "gui"),
            frame=[[1, 2, 1], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        ))

        self.partybtn.addAction("press_down", f1, self.partybtn)
        self.addWidget(self.partybtn)
        self.partybtn.enabled = False

        # Leaderboards Button
        # This button opens the leaderboard container
        self.lbbtn = peng3d.gui.ToggleButton(
            "lbbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 2], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.main.lbbtn.label")
        )
        self.lbbtn.setBackground(peng3d.gui.FramedImageBackground(
            self.lbbtn,
            bg_idle=("cg:img.btn.btn_idle", "gui"),
            bg_hover=("cg:img.btn.btn_hov", "gui"),
            bg_pressed=("cg:img.btn.btn_press", "gui"),
            bg_disabled=("cg:img.btn.btn_disabled", "gui"),
            frame=[[1, 2, 1], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        ))

        self.lbbtn.addAction("press_down", f1, self.lbbtn)
        self.addWidget(self.lbbtn)
        self.lbbtn.enabled = False

        # Settings Button
        # This button switches to the settings submenu
        self.settingsbtn = cgclient.gui.CGButton(
            "settingsbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 1], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.main.settingsbtn.label"),
        )
        self.addWidget(self.settingsbtn)

        def f():
            self.window.changeMenu("settings")
            self.window.menu.prev_menu = "servermain"

        self.settingsbtn.addAction("click", f)

        # Exit Button
        # This button switches to the settings submenu
        self.exitbtn = cgclient.gui.CGButton(
            "exitbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.main.exitbtn.label"),
        )
        self.addWidget(self.exitbtn)

        def f():
            self.peng.cg.client._client.close_connection(reason="exit")
            pyglet.app.exit()

        self.exitbtn.addAction("click", f)

        self.togglebuttons = [self.profile_img, self.profile_label, self.playbtn, self.partybtn, self.lbbtn]

        # Play Container
        self.c_play = PlayContainer("play", self, self.window, self.peng,
                                    pos=(lambda sw, sh, bw, bh: (sw / 3, 0)),
                                    size=(lambda sw, sh: (sw * 2 / 3, sh))
                                    )
        self.addWidget(self.c_play)

        # Party Container

        # Leaderboard Container

        # Profile Containers
        self.c_upwd = ProfileContainer("profile", self, self.window, self.peng,
                                       pos=(lambda sw, sh, bw, bh: (sw * 2 / 3 - bw / 2, sh / 2 - bh / 2)),
                                       size=(lambda sw, sh: (sw / 3, sh / 5))
                                       )
        self.addWidget(self.c_upwd)

        self.c_profile_img = ProfileImageChangeContainer(
            "profile_img_change", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw / 3, 0)),
            size=(lambda sw, sh: (sw * 2 / 3, sh))
        )
        self.addWidget(self.c_profile_img)

    def on_exit(self, new):
        super().on_exit(new)
        # Reset toggle buttons
        for btn in self.togglebuttons:
            btn.pressed = False
            btn.doAction("press_up")

    def register_event_handlers(self):
        self.menu.cg.add_event_listener("cg:user.update", self.handler_userupdate)
        self.menu.cg.add_event_listener("cg:network.client.login", self.handler_login)

    def handler_userupdate(self, event: str, data: dict):
        if data["uuid"] == self.menu.cg.client.user_id:
            self.profile_label.label = self.menu.cg.client.users_uuid[self.menu.cg.client.user_id].username

            profile_img = self.peng.cg.client.users_uuid[self.peng.cg.client.user_id].profile_img
            if profile_img not in self.peng.cg.client.gui.discover_profile_images():
                profile_img = "default"
            self.profile_img.bg.bg_texinfo = self.peng.resourceMgr.normTex(f"cg:profile.{profile_img}", "gui")
            self.profile_img.bg.bg_hover = self.profile_img.bg.bg_pressed = self.profile_img.bg.bg_texinfo

            self.profile_label.redraw()
            self.profile_img.redraw()

    def handler_login(self, event: str, data: dict):
        self.profile_label.label = self.menu.cg.client.users_uuid[self.menu.cg.client.user_id].username

        profile_img = self.peng.cg.client.users_uuid[self.peng.cg.client.user_id].profile_img
        if profile_img not in self.peng.cg.client.gui.discover_profile_images():
            profile_img = "default"
        self.profile_img.bg.bg_texinfo = self.peng.resourceMgr.normTex(f"cg:profile.{profile_img}", "gui")
        self.profile_img.bg.bg_hover = self.profile_img.bg.bg_pressed = self.profile_img.bg.bg_texinfo

        self.profile_label.redraw()
        self.profile_img.redraw()


class LobbySubMenu(peng3d.gui.SubMenu):
    menu: ServerMainMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.register_event_handlers()

        self.setBackground(peng3d.gui.button.FramedImageBackground(
            peng3d.gui.FakeWidget(self),
            bg_idle=("cg:img.bg.bg_dark_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [9, 18], [60, 30])

        # Upper Bar
        self.w_upper_bar = peng3d.gui.Widget(
            "upper_bar", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 15], [9, 3], border=0),
        )
        self.w_upper_bar.setBackground(peng3d.gui.FramedImageBackground(
            self.w_upper_bar,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3)
        ))
        self.w_upper_bar.clickable = False
        self.addWidget(self.w_upper_bar)

        # Lower Bar
        self.w_lower_bar = peng3d.gui.Widget(
            "lower_bar", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [9, 4], border=0),
        )
        self.w_lower_bar.setBackground(peng3d.gui.FramedImageBackground(
            self.w_lower_bar,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3)
        ))
        self.w_lower_bar.clickable = False
        self.addWidget(self.w_lower_bar)

        # Game Label
        self.game_label = peng3d.gui.Label("lobby_game_label", self, self.window, self.peng,
                                           pos=(lambda sw, sh, bw, bh: (sw / 2, sh * 19 / 24)),
                                           # TODO Make this adjusting to the font size
                                           size=(lambda sw, sh: (0, sh / 6)),
                                           label=self.peng.tl("None"),  # This will be changed later
                                           font_size=40,
                                           )
        self.game_label.clickable = False
        self.addWidget(self.game_label)

        # Invite Player Button
        self.invitebtn = cgclient.gui.CGButton(
            "invitebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 2], [3, 2]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.invitebtn.label")
        )
        self.addWidget(self.invitebtn)

        def f():
            self.c_invite.visible = True

        self.invitebtn.addAction("click", f)

        # Leave Button
        self.leavebtn = cgclient.gui.CGButton(
            "leavebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([6, 2], [3, 2]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.leavebtn.label")
        )
        self.addWidget(self.leavebtn)

        def f():
            self.menu.cg.client.send_message("cg:lobby.leave", {
                "lobby": self.menu.cg.client.lobby.uuid.hex
            })
            for btn in self.player_buttons.values():
                btn.player = None

        self.leavebtn.addAction("click", f)

        # Game Button
        self.gamebtn = cgclient.gui.CGButton(
            "gamebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [3, 2]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.gamebtn.label")
        )
        self.gamebtn.enabled = False
        self.addWidget(self.gamebtn)

        # TODO Implement changing games

        def f():
            pass

        self.gamebtn.addAction("click", f)

        # Gamerule Button
        self.gamerulebtn = cgclient.gui.CGButton(
            "gamerulebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([6, 0], [3, 2]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.gamerulebtn.label"),
        )
        self.addWidget(self.gamerulebtn)

        def f():
            self.menu.changeSubMenu("gamerules")

        self.gamerulebtn.addAction("click", f)

        # Ready Button
        self.readybtn = peng3d.gui.ToggleButton(
            "readybtn", self, self.window, self.peng,
            pos=self.grid.get_cell([3, 2], [3, 2]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.readybtn.label"),
        )
        self.readybtn.setBackground(cgclient.gui.CGButtonBG(self.readybtn))
        self.addWidget(self.readybtn)

        def f():
            self.menu.cg.client.send_message("cg:lobby.ready", {"ready": True})

        self.readybtn.addAction("press_down", f)

        def f():
            self.menu.cg.client.send_message("cg:lobby.ready", {"ready": False})

        self.readybtn.addAction("press_up", f)

        # Load Game Button
        self.loadgamebtn = cgclient.gui.CGButton(
            "loadgamebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([3, 0], [3, 2]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.loadgamebtn.label")
        )
        self.loadgamebtn.enabled = False
        self.addWidget(self.loadgamebtn)

        # TODO implement adjourning games

        # Player list
        self.player_buttons = {}
        for i in range(4):
            btn = PlayerButton(
                f"player{i}btn", self, self.window, self.peng,
                pos=(lambda sw, sh, bw, bh, x=i: (3, sh * (2 / 9 + 3 - x * 11 / 72))),
                size=(lambda sw, sh: (sw - 6, sh * 11 / 72)),
                player=None
            )
            self.addWidget(btn)
            self.player_buttons[i] = btn

        self.c_invite = InviteDialog(
            "c_invite", self, self.window, self.peng,
            pos=self.grid.get_cell([3, 6], [3, 6]),
            size=None
        )
        self.addWidget(self.c_invite)

        self.c_kick = KickDialog(
            "c_kick", self, self.window, self.peng,
            pos=self.grid.get_cell([3, 6], [3, 6]),
            size=None
        )
        self.addWidget(self.c_kick)

    def register_event_handlers(self):
        self.menu.cg.add_event_listener("cg:lobby.game.change", self.handle_game_change)

    def handle_game_change(self, event: str, data: dict):
        self.game_label.label = self.peng.tl(f"cg:game.{data['game']}")
        self.menu.s_gamerule.heading.label = self.peng.tl(
            "cg:gui.menu.smain.gamerule.heading",
            {"game": self.peng.tl(f"cg:game.{data['game']}")}
        )


class GameruleSubMenu(peng3d.gui.SubMenu):
    menu: ServerMainMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [12, 6], [60, 30])

        # Upper Bar
        self.w_upper_bar = peng3d.gui.Widget(
            "upper_bar", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 5], [12, 1], border=0),
        )
        self.w_upper_bar.setBackground(peng3d.gui.FramedImageBackground(
            self.w_upper_bar,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3)
        ))
        self.w_upper_bar.clickable = False
        self.addWidget(self.w_upper_bar)

        # Lower Bar
        self.w_lower_bar = peng3d.gui.Widget(
            "lower_bar", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [12, 1], border=0),
        )
        self.w_lower_bar.setBackground(peng3d.gui.FramedImageBackground(
            self.w_lower_bar,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3)
        ))
        self.w_lower_bar.clickable = False
        self.addWidget(self.w_lower_bar)

        # Gamerules Heading
        self.heading = peng3d.gui.Label("gamerules_heading", self, self.window, self.peng,
                                        pos=(lambda sw, sh, bw, bh: (sw / 2, sh * 19 / 24)),
                                        # TODO Make this adjusting to the font size
                                        size=(lambda sw, sh: (0, sh / 6)),
                                        label=self.peng.tl("None"),  # This will be changed later
                                        font_size=40,
                                        )
        self.heading.clickable = False
        self.addWidget(self.heading)

        # Back Button
        self.backbtn = cgclient.gui.CGButton(
            "backbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [4, 1]),
            label=self.peng.tl("cg:gui.menu.smain.gamerule.backbtn.label"),
        )
        self.addWidget(self.backbtn)

        def f():
            self.menu.changeSubMenu("lobby")

        self.backbtn.addAction("click", f)

        # Load Template Button
        self.loadtmplbtn = cgclient.gui.CGButton(
            "loadtmplbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([4, 0], [4, 1]),
            label=self.peng.tl("cg:gui.menu.smain.gamerule.loadtmplbtn.label"),
        )
        self.addWidget(self.loadtmplbtn)

        def f():
            self.menu.changeSubMenu("template")

        self.loadtmplbtn.addAction("click", f)

        # Save Template Button
        self.savetmplbtn = cgclient.gui.CGButton(
            "savetmplbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([8, 0], [4, 1]),
            label=self.peng.tl("cg:gui.menu.smain.gamerule.savetmplbtn.label"),
        )
        self.addWidget(self.savetmplbtn)

        def f():
            self.c_save.visible = True

        self.savetmplbtn.addAction("click", f)

        # Previous Page Button
        self.prevpagebtn = cgclient.gui.CGButton(
            "prevpagebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 5], [3, 1]),
            label=self.peng.tl("cg:gui.menu.smain.gamerule.prevpagebtn.label"),
        )
        self.addWidget(self.prevpagebtn)
        self.prevpagebtn.enabled = False

        def f():
            self.gamerule_containers[self.current_page].visible = False
            self.current_page -= 1
            self.gamerule_containers[self.current_page].visible = True
            if self.current_page == 0:
                self.prevpagebtn.enabled = False
            self.nextpagebtn.enabled = True

        self.prevpagebtn.addAction("click", f)

        # Next Page Button
        self.nextpagebtn = cgclient.gui.CGButton(
            "nextpagebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([9, 5], [3, 1]),
            label=self.peng.tl("cg:gui.menu.smain.gamerule.nextpagebtn.label"),
        )
        self.addWidget(self.nextpagebtn)

        def f():
            self.gamerule_containers[self.current_page].visible = False
            self.current_page += 1
            self.gamerule_containers[self.current_page].visible = True
            if self.current_page == len(self.gamerule_containers) - 1:
                self.nextpagebtn.enabled = False
            self.prevpagebtn.enabled = True

        self.nextpagebtn.addAction("click", f)

        # Gamerule Containers
        self.gamerule_containers = {}
        self.rule_buttons = {}
        self.current_page = 0

        self.c_save = TemplateSaveDialog(
            "c_save", self, self.window, self.peng,
            pos=self.grid.get_cell([4, 2], [4, 2]),
            size=None
        )
        self.addWidget(self.c_save, 10)

    def on_enter(self, old):
        if old == "template" and self.menu.submenus["template"].exit_mode == "back":
            self.gamerule_containers[self.current_page].visible = True
        else:
            self.current_page = 0
            self.nextpagebtn.enabled = True
            self.prevpagebtn.enabled = False
            self.gamerule_containers[self.current_page].visible = True

    def on_exit(self, new):
        self.gamerule_containers[self.current_page].visible = False


class TemplateSubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.chosen_save = ""

        self.exit_mode = "back"

        self.setBackground(peng3d.gui.FramedImageBackground(
            peng3d.gui.FakeWidget(self),
            bg_idle=("cg:img.bg.bg_dark_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3)
        ))

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [12, 18], [60, 30])

        # Upper Bar
        self.w_upper_bar = peng3d.gui.Widget(
            "upper_bar", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 15], [12, 3], border=0),
        )
        self.w_upper_bar.setBackground(peng3d.gui.FramedImageBackground(
            self.w_upper_bar,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3)
        ))
        self.w_upper_bar.clickable = False
        self.addWidget(self.w_upper_bar)

        # Lower Bar
        self.w_lower_bar = peng3d.gui.Widget(
            "lower_bar", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [12, 3], border=0),
        )
        self.w_lower_bar.setBackground(peng3d.gui.FramedImageBackground(
            self.w_lower_bar,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3)
        ))
        self.w_lower_bar.clickable = False
        self.addWidget(self.w_lower_bar)

        # Gamerules Heading
        self.heading = peng3d.gui.Label("template_load_heading", self, self.window, self.peng,
                                        pos=(lambda sw, sh, bw, bh: (sw / 2, sh * 19 / 24)),
                                        # TODO Make this adjusting to the font size
                                        size=(lambda sw, sh: (0, sh / 6)),
                                        label=self.peng.tl("cg:gui.menu.smain.template.heading"),
                                        font_size=40,
                                        )
        self.heading.clickable = False
        self.addWidget(self.heading)

        # Back Button
        self.backbtn = cgclient.gui.CGButton(
            "backbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [4, 3]),
            label=self.peng.tl("cg:gui.menu.smain.template.backbtn.label"),
        )
        self.addWidget(self.backbtn)

        def f():
            self.exit_mode = "back"
            self.menu.changeSubMenu("gamerules")

        self.backbtn.addAction("click", f)

        # Load Template Button
        self.loadtmplbtn = cgclient.gui.CGButton(
            "loadtmplbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([4, 0], [4, 3]),
            label=self.peng.tl("cg:gui.menu.smain.template.loadtmplbtn.label"),
        )
        self.addWidget(self.loadtmplbtn)

        def f():
            self.peng.cg.client.send_message("cg:lobby.change", {
                "gamerules": self.saves[self.chosen_save]
            })

            self.exit_mode = "load"
            self.menu.changeSubMenu("gamerules")

        self.loadtmplbtn.addAction("click", f)

        # Delete Template Button
        self.deletebtn = cgclient.gui.CGButton(
            "deletebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([8, 0], [4, 3]),
            label=self.peng.tl("cg:gui.menu.smain.template.deletebtn.label"),
        )
        self.addWidget(self.deletebtn)

        def f():
            _saves = self.saves
            del _saves[self.chosen_save]
            self.saves = _saves

            _save_opts = self.save_opts
            _save_opts.remove(self.chosen_save)
            self.save_opts = _save_opts

            self.on_enter("template")

        self.deletebtn.addAction("click", f)

        self.save_btns = []
        for i in range(6):
            for j in range(3):
                btn = peng3d.gui.ToggleButton(
                    f"button{j}:{i}", self, self.window, self.peng,
                    pos=self.grid.get_cell([j * 4, 13 - 2 * i], [4, 2]),
                    label="",
                )
                btn.setBackground(peng3d.gui.FramedImageBackground(
                    btn,
                    bg_idle=("cg:img.btn.btn_idle", "gui"),
                    bg_hover=("cg:img.btn.btn_hov", "gui"),
                    bg_pressed=("cg:img.btn.btn_press", "gui"),
                    bg_disabled=("cg:img.btn.btn_disabled", "gui"),
                    frame=[[1, 2, 1], [0, 1, 0]],
                    scale=(None, 0),
                    repeat_edge=True, repeat_center=True,
                ))
                self.addWidget(btn)
                self.save_btns.append(btn)
                btn.visible = False

                def f(button):
                    for b in self.save_btns:
                        if b != button:
                            b.pressed = False
                            b.redraw()
                    self.chosen_save = button.label
                    self.loadtmplbtn.enabled = True
                    self.deletebtn.enabled = True

                btn.addAction("press_down", f, btn)

                def f():
                    self.chosen_save = ""
                    self.loadtmplbtn.enabled = False
                    self.deletebtn.enabled = False

                btn.addAction("press_up", f)

    @property
    def save_opts(self):
        return self.peng.cg.config_manager.get_config_option("cg:templates.options")

    @save_opts.setter
    def save_opts(self, value):
        self.peng.cg.config_manager.set_config_option("cg:templates.options", value)

    @property
    def saves(self):
        return {opt: self.peng.cg.config_manager.get_config_option(f"cg:templates.{opt}") for opt in self.save_opts}

    @saves.setter
    def saves(self, value):
        for key, data in value.items():
            self.peng.cg.config_manager.set_config_option(f"cg:templates.{key}", data)

    def on_enter(self, old):
        for i, btn in enumerate(self.save_btns):
            if i < len(self.save_opts):
                self.save_btns[i].label = self.save_opts[i]
                self.save_btns[i].visible = True
                self.save_btns[i].pressed = False
            else:
                self.save_btns[i].label = ""
                self.save_btns[i].visible = False
                self.save_btns[i].pressed = False

        self.deletebtn.enabled = False
        self.loadtmplbtn.enabled = False


class PlayContainer(peng3d.gui.Container):
    submenu: MainSubMenu

    def __init__(self, name, submenu, window, peng, pos, size):
        super().__init__(name, submenu, window, peng,
                         pos, size,
                         font_size=20)

        self.visible = False

        self.grid = peng3d.gui.GridLayout(self.peng, self, [4, 3], [60, 60])

        self.bg_widget = peng3d.gui.Widget("container_bg", self, self.window, self.peng,
                                           pos=(0, 0),
                                           size=(lambda sw, sh: (sw, sh)))
        self.bg_widget.setBackground(peng3d.gui.button.FramedImageBackground(
            self.bg_widget,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )
        self.bg_widget.bg.vlist_layer = -1
        self.bg_widget.clickable = False
        self.addWidget(self.bg_widget)

        self.playbtns = {}

        for game in GAMES:
            for variant in GAME_VARIANTS:
                pbtn = GameSelectButton(
                    f"{game}{variant}_btn", self, self.window, self.peng,
                    game, variant,
                    pos=self.grid.get_cell([GAMES.index(game), GAME_VARIANTS.index(variant)], [1, 1]),
                )
                self.addWidget(pbtn)
                self.playbtns[f"{game}{variant}"] = pbtn

                pbtn.enabled = f"{game}{variant}" in ALLOWED_GAMES
                pbtn.doAction("statechanged")


class ProfileContainer(peng3d.gui.Container):
    submenu: MainSubMenu

    def __init__(self, name, submenu, window, peng, pos, size):
        super().__init__(name, submenu, window, peng, pos, size)

        self.visible = False

        self.grid = peng3d.gui.GridLayout(self.peng, self, [2, 2], [60, 20])

        self.bg_widget = peng3d.gui.Widget("container_bg", self, self.window, self.peng,
                                           pos=(0, 0),
                                           size=(lambda sw, sh: (sw, sh)))
        self.bg_widget.setBackground(peng3d.gui.button.FramedImageBackground(
            self.bg_widget,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )
        self.bg_widget.bg.vlist_layer = -1
        self.bg_widget.clickable = False
        self.addWidget(self.bg_widget)

        # Change username button
        self.unamechangebtn = cgclient.gui.CGButton(
            "unamechangebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 1], [2, 1]),
            label=self.peng.tl("cg:gui.menu.smain.profile.unamechangebtn.label")
        )
        self.addWidget(self.unamechangebtn)

        def f():
            self.unamechangebtn.visible = False
            self.pwdchangebtn.visible = False

            self.uname_field.visible = True
            self.uname_commit.visible = True
            self.uname_cancel.visible = True

        self.unamechangebtn.addAction("click", f)

        # Change Username Input field
        self.uname_field = cgclient.gui.CGTextInput(
            "uname_field", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 1], [2, 1]),
        )
        self.addWidget(self.uname_field)
        self.uname_field.visible = False

        # Commit Username Change Button
        self.uname_commit = cgclient.gui.CGButton(
            "uname_commit", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.profile.uname_commit.label")
        )
        self.addWidget(self.uname_commit)
        self.uname_commit.visible = False

        def f():
            if self.uname_field.text != "":
                self.peng.cg.client.send_message("cg:status.user", {
                    "username": self.uname_field.text,
                    "uuid": self.peng.cg.client.user_id.hex
                })

                self.uname_field.text = ""
                self.uname_field.visible = False
                self.uname_commit.visible = False
                self.uname_cancel.visible = False

                self.unamechangebtn.visible = True
                self.pwdchangebtn.visible = True

                self.visible = False
                self.submenu.profile_label._pressed = False

        self.uname_commit.addAction("click", f)

        # Cancel Username Change Button
        self.uname_cancel = cgclient.gui.CGButton(
            "uname_cancel", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.profile.uname_cancel.label")
        )
        self.addWidget(self.uname_cancel)
        self.uname_cancel.visible = False

        def f():
            self.uname_field.text = ""
            self.uname_field.visible = False
            self.uname_commit.visible = False
            self.uname_cancel.visible = False

            self.unamechangebtn.visible = True
            self.pwdchangebtn.visible = True

            self.visible = False
            self.submenu.profile_label._pressed = False

        self.uname_cancel.addAction("click", f)

        # Change Password Button
        self.pwdchangebtn = cgclient.gui.CGButton(
            "pwdchangebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [2, 1]),
            label=self.peng.tl("cg:gui.menu.smain.profile.pwdchangebtn.label")
        )
        self.addWidget(self.pwdchangebtn)

        def f():
            self.pwdchangebtn.visible = False
            self.unamechangebtn.visible = False

            self.old_pwd_field.visible = True
            self.new_pwd_field.visible = True
            self.confirm_pwd_field.visible = True
            self.pwd_commit.visible = True
            self.pwd_cancel.visible = True

            self.size = (lambda sw, sh: (sw / 3, sh / 2.5))
            self.grid.res = [2, 4]

        self.pwdchangebtn.addAction("click", f)

        # Old Password Field
        self.old_pwd_field = cgclient.gui.CGTextInput(
            "old_pwd_field", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 3], [2, 1]),
            default=self.peng.tl("cg:gui.menu.smain.profile.old_pwd_field.default"),
            font_color_default=[255, 255, 255, 50]
        )
        self.addWidget(self.old_pwd_field)
        self.old_pwd_field.visible = False

        # New Password Field
        self.new_pwd_field = cgclient.gui.CGTextInput(
            "new_pwd_field", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 2], [2, 1]),
            default=self.peng.tl("cg:gui.menu.smain.profile.new_pwd_field.default"),
            font_color_default=[255, 255, 255, 50]
        )
        self.addWidget(self.new_pwd_field)
        self.new_pwd_field.visible = False

        # Confirm Password Field
        self.confirm_pwd_field = cgclient.gui.CGTextInput(
            "confirm_pwd_field", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 1], [2, 1]),
            default=self.peng.tl("cg:gui.menu.smain.profile.confirm_pwd_field.default"),
            font_color_default=[255, 255, 255, 50]
        )
        self.addWidget(self.confirm_pwd_field)
        self.confirm_pwd_field.visible = False

        # Commit Password Change Button
        self.pwd_commit = cgclient.gui.CGButton(
            "pwd_commit", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.profile.pwd_commit.label")
        )
        self.addWidget(self.pwd_commit)
        self.pwd_commit.visible = False

        def f():
            if self.new_pwd_field.text == self.confirm_pwd_field.text:
                self.peng.cg.client.send_message("cg:status.user", {
                    "uuid": self.peng.cg.client.user_id.hex,
                    "pwd": [self.old_pwd_field.text, self.new_pwd_field.text]
                })

                self.old_pwd_field.text = ""
                self.new_pwd_field.text = ""
                self.confirm_pwd_field.text = ""

                self.old_pwd_field.visible = False
                self.new_pwd_field.visible = False
                self.confirm_pwd_field.visible = False
                self.pwd_commit.visible = False
                self.pwd_cancel.visible = False

                self.size = (lambda sw, sh: (sw / 3, sh / 5))
                self.grid.res = [2, 2]

                self.pwdchangebtn.visible = True
                self.unamechangebtn.visible = True

                self.visible = False
                self.submenu.profile_label._pressed = False

        self.pwd_commit.addAction("click", f)

        # Cancel Password Change Button
        self.pwd_cancel = cgclient.gui.CGButton(
            "pwd_cancel", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.profile.pwd_cancel.label")
        )
        self.addWidget(self.pwd_cancel)
        self.pwd_cancel.visible = False

        def f():
            self.old_pwd_field.text = ""
            self.new_pwd_field.text = ""
            self.confirm_pwd_field.text = ""

            self.old_pwd_field.visible = False
            self.new_pwd_field.visible = False
            self.confirm_pwd_field.visible = False
            self.pwd_commit.visible = False
            self.pwd_cancel.visible = False

            self.size = (lambda sw, sh: (sw / 3, sh / 5))
            self.grid.res = [2, 2]

            self.pwdchangebtn.visible = True
            self.unamechangebtn.visible = True

            self.visible = False
            self.submenu.profile_label._pressed = False

        self.pwd_cancel.addAction("click", f)


class ProfileImageChangeContainer(peng3d.gui.Container):
    submenu: MainSubMenu

    def __init__(self, name, submenu, window, peng, pos, size):
        super().__init__(name, submenu, window, peng, pos, size)

        self.visible = False

        # Background
        self.setBackground(peng3d.gui.button.FramedImageBackground(
            self,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )

        # Profile image file names
        self.profile_imgs = sorted(self.peng.cg.client.gui.discover_profile_images())
        if "default" in self.profile_imgs:
            self.profile_imgs.remove("default")
            self.profile_imgs.append("default")
        self.profile_btns = {}

        # Determine Grid size
        long = math.ceil(math.sqrt(len(self.profile_imgs)))
        short = math.ceil(len(self.profile_imgs) / long)
        res = [short, long]
        if self.size[0] > self.size[1]:
            res.reverse()
        self.grid = peng3d.gui.GridLayout(self.peng, self, res, [20, 20])

        def size(sw, sh):
            cell = self.grid.get_cell([0, 0], [1, 1])
            return 2 * [min(cell.size[0], cell.size[1])]

        for i, img_name in enumerate(self.profile_imgs):
            if i == len(self.profile_imgs):
                break
            btn = peng3d.gui.ImageButton(
                img_name, self, self.window, self.peng,
                pos=self.lambda_pos(i),
                size=size,
                label="",
                bg_idle=(f"cg:profile.{img_name}", "profile"),
            )
            self.addWidget(btn)
            self.profile_btns[img_name] = btn

            def f(button):
                self.peng.cg.client.send_message("cg:status.user", {
                    "uuid": self.peng.cg.client.user_id.hex,
                    "profile_img": button.name
                })
                self.visible = False
                self.submenu.profile_img.pressed = False

            btn.addAction("click", f, btn)

    def lambda_pos(self, i):
        res = self.grid.res

        def pos(sw, sh, bw, bh):
            base_pos = self.grid.get_cell(
                [i % res[0], res[1] - 1 - i // res[0]],
                [1, 1],
                anchor_x="center", anchor_y="center"
            ).pos
            base_pos = [base_pos[0] - self.grid.pos[0], base_pos[1] - self.grid.pos[1]]
            return base_pos[0] - bw / 2, base_pos[1] - bh / 2

        return pos


class GameSelectButton(peng3d.gui.LayeredWidget):
    submenu: PlayContainer

    def __init__(self, name, submenu, window, peng,
                 game, variant,
                 pos=None, size=None,
                 ):
        super().__init__(name, submenu, window, peng,
                         pos=pos, size=size,
                         )

        self.game = game
        self.variant = variant

        self.bg_layer = peng3d.gui.FramedImageWidgetLayer(
            "bg_layer", self, 1,
            imgs={
                "idle": ("cg:img.bg.rbg_idle", "gui"),
                "hover": ("cg:img.bg.rbg_hov", "gui"),
                "pressed": ("cg:img.bg.rbg_press", "gui"),
                "disabled": ("cg:img.bg.rbg_disab", "gui"),
            },
            default="idle",
            frame=[[21, 2, 21], [21, 2, 21]],
            scale=(.3, .3),
        )
        self.addLayer(self.bg_layer)

        self.addAction("statechanged", lambda: self.bg_layer.switchImage(self.getState()))

        ar = 12 / 7  # Aspect ratio of icons

        # TODO: maybe do not hardcode this anymore

        def b(x, y, sx, sy) -> Tuple[int, int]:
            if sy / 2 > sx:
                # X-Axis is constraining factor
                s = sx
                return (sx - s) / 2, (sy - s) / 2
            else:
                # Y-Axis is constraining factor
                s = sy / 2
                return (sx - s) / 2 / ar, (sy - s) / 2

        def o(x, y, sx, sy):
            if sy / 2 > sx:
                # X-Axis is constraining factor
                s = sx
                return 0, s / 2
            else:
                # Y-Axis is constraining factor
                s = sy / 2
                return 0, s / 2

        self.icon_layer = peng3d.gui.ImageWidgetLayer(
            "icon_layer", self, 2,
            img=(f"cg:img.game_icons.{self.game}{self.variant}", "icn"),
            border=b,
            offset=o,
        )
        self.addLayer(self.icon_layer)

        self.label1_layer = peng3d.gui.LabelWidgetLayer(
            "label1_layer", self, 3,
            label=self.peng.tl(f"cg:gui.menu.smain.play.{self.game}{self.variant}.label.0"),
            font_size=22,
            offset=[0, -20]
        )
        self.addLayer(self.label1_layer)

        self.label2_layer = peng3d.gui.LabelWidgetLayer(
            "label2_layer", self, 3,
            label=self.peng.tl(f"cg:gui.menu.smain.play.{self.game}{self.variant}.label.1"),
            font_size=16,
            offset=[0, -20 - 22 - 8],
        )
        self.addLayer(self.label2_layer)

        def f():
            self.peng.cg.client.send_message("cg:lobby.create",
                                             {
                                                 "game": GAME_TO_NAME[self.game],
                                                 "variant": self.variant,
                                             })
            self.peng.cg.info("Sent lobby creation request")
            # TODO: add loading screen here

        self.addAction("click", f)


class _FakeUser:
    username = ""
    profile_img = "transparent"
    ready = False
    uuid = None


class PlayerButton(peng3d.gui.LayeredWidget):
    submenu: LobbySubMenu

    def __init__(self, name, submenu, window, peng, pos, size,
                 player):
        super().__init__(name, submenu, window, peng, pos, size)

        self.register_event_handlers()

        self._player = player

        # Background
        self.bg_layer = peng3d.gui.DynImageWidgetLayer(
            "bg_layer", self,
            z_index=1,
            imgs={
                "idle": ("cg:img.bg.transparent", "gui"),
                "hover": ("cg:img.bg.gray_brown", "gui"),
                "press": ("cg:img.bg.dark_gray_brown", "gui")
            }
        )
        self.bg_layer.switchImage("idle")
        self.addLayer(self.bg_layer)

        def f():
            if self._player is not None and not self.submenu.c_invite.visible:
                self.bg_layer.switchImage("hover")

        self.addAction("hover_start", f)

        def f():
            self.bg_layer.switchImage("idle")

        self.addAction("hover_end", f)

        def f():
            self.bg_layer.switchImage("press")

        self.addAction("press", f)

        def f():
            self.bg_layer.switchImage("hover")

        self.addAction("click", f)

        # Admin Icon
        self.admin_icon = peng3d.gui.DynImageWidgetLayer(
            "admin_icon", self,
            z_index=3,
            border=(lambda bx, by, bw, bh: (bw / 2 - bh / 8, bh * 3 / 8)),
            offset=(lambda bx, by, bw, bh: (-bw / 2 + bh / 8 + 20, 0)),
            imgs={
                "transparent": ("cg:img.bg.transparent", "gui"),
                "admin": ("cg:img.btn.admin", "gui")
            },
        )
        self.admin_icon.switchImage("transparent")
        self.addLayer(self.admin_icon)

        # User icon
        profile_img = self.player.profile_img
        if profile_img not in self.peng.cg.client.gui.discover_profile_images():
            profile_img = "default"
        self.icon_layer = peng3d.gui.DynImageWidgetLayer(
            "img", self,
            z_index=3,
            border=(lambda bx, by, bw, bh: (bw / 2 - bh / 3, bh / 6)),
            offset=(lambda bx, by, bw, bh: (-bw/2 + bh * 7/12 + 40, 0)),
            imgs={
                "transparent": ("cg:img.bg.transparent", "gui"),
                profile_img: (f"cg:profile.{profile_img}", "profile")
            },
        )
        self.icon_layer.switchImage("transparent")
        self.addLayer(self.icon_layer)

        # Username
        self.username_label_layer = peng3d.gui.LabelWidgetLayer(
            "username_label_layer", self,
            z_index=3,
            label=self.player.username,
            font_size=30,
            offset=(lambda bx, by, bw, bh: (-bw/2 + bh * 11/12 + 60, 0))
        )
        self.username_label_layer._label.anchor_x = "left"
        self.addLayer(self.username_label_layer)

        # Ready icon
        self.readybtn = peng3d.gui.DynImageWidgetLayer(
            "readybtn", self,
            z_index=3,
            border=(lambda bx, by, bw, bh: (bw / 2 - bh / 8, bh * 3 / 8)),
            offset=(
                lambda bx, by, bw, bh: (-bw/2 + bh * 25/24 + 80 + self.username_label_layer._label.content_width, 0)
            ),
            imgs={
                "transparent": ("cg:img.bg.transparent", "gui"),
                "default": ("cg:img.btn.ok", "gui")
            },
        )
        self.readybtn.switchImage("transparent")
        self.addLayer(self.readybtn)

        # Kick Button
        self.kickbtn = peng3d.gui.DynImageWidgetLayer(
            "kickbtn", self,
            z_index=3,
            border=(lambda bx, by, bw, bh: (bw / 2 - bh / 6, bh * 1 / 3)),
            offset=(lambda bx, by, bw, bh: (bw / 2 - bh / 6 - 20, 0)),
            imgs={
                "transparent": ("cg:img.bg.transparent", "gui"),
                "default": ("cg:img.btn.kick", "gui")
            },
        )
        self.kickbtn.pressed = False
        self.kickbtn.switchImage("transparent")
        self.addLayer(self.kickbtn)

        # Make Admin Button
        self.make_admin_btn = peng3d.gui.DynImageWidgetLayer(
            "make_admin_btn", self,
            z_index=3,
            border=(lambda bx, by, bw, bh: (bw / 2 - bh / 6, bh * 1 / 3)),
            offset=(lambda bx, by, bw, bh: (bw / 2 - bh / 2 - 40, 0)),
            imgs={
                "transparent": ("cg:img.bg.transparent", "gui"),
                "default": ("cg:img.btn.admin", "gui")
            },
        )
        self.make_admin_btn.pressed = False
        self.make_admin_btn.switchImage("transparent")
        self.addLayer(self.make_admin_btn)

        self.mouse_offset = []
        self.is_dragged = False

    @property
    def clickable(self):
        return super().clickable and self._player is not None and not self.submenu.c_invite.visible

    @property
    def player(self):
        if self._player is None:
            return _FakeUser()
        else:
            return self._player

    @player.setter
    def player(self, value: Union[cgclient.user.User, _FakeUser]):
        self._player = value

        # Username
        self.username_label_layer.label = self.player.username

        # User icon
        if value is not None:
            self.icon_layer.addImage(self.player.profile_img, (f"cg:profile.{self.player.profile_img}", "profile"))

            # Kick button
            if self.peng.cg.client.lobby.user_roles.get(self.peng.cg.client.user_id, 0) >= ROLE_ADMIN:
                self.kickbtn.switchImage("default")

                # Make Admin button
                if self.peng.cg.client.lobby.user_roles.get(self.player.uuid, 0) < ROLE_ADMIN:
                    self.make_admin_btn.switchImage("default")

            # Admin Icon
            if self.peng.cg.client.lobby.user_roles.get(self.player.uuid, 0) >= ROLE_ADMIN:
                self.admin_icon.switchImage("admin")

        else:
            self.kickbtn.switchImage("transparent")
            self.admin_icon.switchImage("transparent")
            self.make_admin_btn.switchImage("transparent")

        self.icon_layer.switchImage(self.player.profile_img)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        super().on_mouse_drag(x, y, dx, dy, button, modifiers)
        if self.is_dragged:
            new_y = y - self.mouse_offset[1]
            lower_border = self.window.height * 2 / 9
            upper_boder = self.window.height * 5 / 6 - self.size[1]
            if lower_border < new_y < upper_boder:
                self.pos = [self.pos[0], new_y]

            # Check if the adjacent button should be swapped
            index = 0
            for index, btn in self.submenu.player_buttons.items():
                if btn == self:
                    break

            if index != 3:  # For the lower button
                next_button = self.submenu.player_buttons[index + 1]
                if next_button.clickable:
                    if abs(next_button.pos[1] - self.pos[1]) < self.size[1] / 2:  # Closer to next pos than to own
                        self.submenu.player_buttons[index] = next_button
                        self.submenu.player_buttons[index + 1] = self
                        next_button.pos = (lambda sw, sh, bw, bh: (
                            3, sh * (2 / 9 + ((3 - index) * 11 / 72))))  # TODO Fix potential memory leak
                        next_button.redraw()

            if index != 0:  # For the button above
                next_button = self.submenu.player_buttons[index - 1]
                if next_button.clickable:
                    if abs(next_button.pos[1] - self.pos[1]) < self.size[1] / 2:  # Closer to next pos than to own
                        self.submenu.player_buttons[index] = next_button
                        self.submenu.player_buttons[index - 1] = self
                        next_button.pos = (lambda sw, sh, bw, bh: (
                            3, sh * (2 / 9 + ((3 - index) * 11 / 72))))  # TODO Fix potential memory leak
                        next_button.redraw()

    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        if self.clickable and self.is_hovering:
            if button == LEFT:
                if self.kickbtn.getPos()[0] <= x <= self.kickbtn.getPos()[0] + self.kickbtn.getSize()[0] and \
                        self.kickbtn.getPos()[1] <= y <= self.kickbtn.getPos()[1] + self.kickbtn.getSize()[1]:
                    self.kickbtn.pressed = True
                elif self.make_admin_btn.getPos()[0] <= x <= self.make_admin_btn.getPos()[0] + \
                        self.make_admin_btn.getSize()[0] and \
                        self.make_admin_btn.getPos()[1] <= y <= self.make_admin_btn.getPos()[1] + \
                        self.make_admin_btn.getSize()[1]:
                    self.make_admin_btn.pressed = True
                else:
                    self.mouse_offset = [x - self.pos[0], y - self.pos[1]]
                    self.is_dragged = True

    def on_mouse_release(self, x, y, button, modifiers):
        super().on_mouse_release(x, y, button, modifiers)
        if button == LEFT:
            if self.kickbtn.getPos()[0] <= x <= self.kickbtn.getPos()[0] + self.kickbtn.getSize()[0] and \
                    self.kickbtn.getPos()[1] <= y <= self.kickbtn.getPos()[1] + self.kickbtn.getSize()[1] and \
                    self.kickbtn.pressed:
                self.submenu.c_kick.init_kick(self.player)
                self.submenu.c_kick.visible = True
                self.kickbtn.pressed = False
                return
            self.kickbtn.pressed = False

            if self.make_admin_btn.getPos()[0] <= x <= self.make_admin_btn.getPos()[0] + \
                    self.make_admin_btn.getSize()[0] and \
                    self.make_admin_btn.getPos()[1] <= y <= self.make_admin_btn.getPos()[1] + \
                    self.make_admin_btn.getSize()[1] and \
                    self.make_admin_btn.pressed:
                user_roles = self.peng.cg.client.lobby.user_roles
                user_roles[self.player.uuid] = ROLE_ADMIN
                self.peng.cg.client.send_message("cg:lobby.change", {
                    "user_roles": {k.hex: v for k, v in user_roles.items()}
                })
                self.make_admin_btn.pressed = False
                return
            self.make_admin_btn.pressed = False

            if self.is_dragged:
                if button == LEFT:
                    self.mouse_offset.clear()
                    self.is_dragged = False

                    for i, btn in self.submenu.player_buttons.items():
                        if btn == self:
                            self.pos = (lambda sw, sh, bw, bh: (
                                3, sh * (2 / 9 + ((3 - i) * 11 / 72))))  # TODO Fix potential memory leak
                            self.redraw()
                            break

                    player_order = []
                    for j in range(4):
                        if self.submenu.player_buttons[j]._player is not None:
                            player_order.append(self.submenu.player_buttons[j].player.uuid)
                    self.peng.cg.client.send_message("cg:lobby.change", {
                        "user_order": [p.hex for p in player_order]
                    })

    def register_event_handlers(self):
        self.peng.cg.add_event_listener("cg:user.update", self.handler_userupdate)
        self.peng.cg.add_event_listener("cg:lobby.admin.change", self.handle_admin_change)
        self.peng.cg.add_event_listener("cg:lobby.player.ready", self.handle_ready)

    def handler_userupdate(self, event: str, data: dict):
        if data["uuid"] == self.peng.cg.client.user_id:
            self.username_label_layer.label = self.player.username

            profile_img = self.player.profile_img
            if profile_img not in self.peng.cg.client.gui.discover_profile_images():
                profile_img = "default"
            self.icon_layer.addImage(profile_img, (f"cg:profile.{profile_img}", "profile"))
            self.icon_layer.switchImage(profile_img)

    def handle_admin_change(self, event: str, data: dict):
        role = data.get(self.player.uuid, None)
        if role is None:
            return

        print("hi")

        # Kick button
        if self.peng.cg.client.lobby.user_roles.get(self.peng.cg.client.user_id, 0) >= ROLE_ADMIN:
            print("Im Admin!")
            self.kickbtn.switchImage("default")

            # Make Admin button
            if self.peng.cg.client.lobby.user_roles.get(self.player.uuid, 0) < ROLE_ADMIN:
                self.make_admin_btn.switchImage("default")
            else:
                self.make_admin_btn.switchImage("transparent")
        else:
            self.kickbtn.switchImage("transparent")
            self.make_admin_btn.switchImage("transparent")

        # Admin Icon
        if self.peng.cg.client.lobby.user_roles.get(self.player.uuid, 0) >= ROLE_ADMIN:
            self.admin_icon.switchImage("admin")
        else:
            self.admin_icon.switchImage("transparent")

    def handle_ready(self, event: str, data: dict):
        if data["player"] == self.player.uuid:
            if data["ready"]:
                self.readybtn.switchImage("default")
            else:
                self.readybtn.switchImage("transparent")


class InviteDialog(peng3d.gui.Container):
    def __init__(self, name, submenu, window, peng, pos, size):
        super().__init__(name, submenu, window, peng,
                         pos, size)

        self.visible = False

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [2, 3], [30, 20])

        self.bg_widget = peng3d.gui.Widget("invite_bg", self, self.window, self.peng,
                                           pos=(0, 0),
                                           size=(lambda sw, sh: (sw, sh)))
        self.bg_widget.setBackground(peng3d.gui.button.FramedImageBackground(
            self.bg_widget,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )
        self.bg_widget.bg.vlist_layer = 10
        self.bg_widget.clickable = False
        self.addWidget(self.bg_widget)

        # Heading
        self.invite_heading = peng3d.gui.Label(
            "invite_heading", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 2], [2, 1]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.invite_heading"),
            font_size=25,
            label_layer=11,
        )
        self.invite_heading.clickable = False
        self.addWidget(self.invite_heading)

        # Input field for username
        self.input_field = cgclient.gui.CGTextInput(
            "invite_input", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 1], [2, 1]),
            font_size=25
        )
        self.input_field.bg.parent.vlist_layer = 11
        self.input_field.bg.vlist_cursor_layer = 12
        self.addWidget(self.input_field)

        # Ok Button
        self.okbtn = cgclient.gui.CGButton(
            "invite_okbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.invite_okbtn.label"),
            label_layer=12,
        )
        self.okbtn.bg.vlist_layer = 11
        self.addWidget(self.okbtn)

        def f():
            self.peng.cg.client.send_message("cg:lobby.invite", {
                "username": self.input_field.text
            })
            self.visible = False
            self.input_field.text = ""

        self.okbtn.addAction("click", f)

        # Cancel Button
        self.cancelbtn = cgclient.gui.CGButton(
            "invite_cancelbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.invite_cancelbtn.label"),
            label_layer=12,
        )
        self.cancelbtn.bg.vlist_layer = 11
        self.addWidget(self.cancelbtn)

        def f():
            self.visible = False
            self.input_field.text = ""

        self.cancelbtn.addAction("click", f)


class KickDialog(peng3d.gui.Container):
    def __init__(self, name, submenu, window, peng, pos, size):
        super().__init__(name, submenu, window, peng,
                         pos, size)

        self.visible = False
        self.kick_player = None

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [2, 3], [30, 20])

        self.bg_widget = peng3d.gui.Widget("kick_bg", self, self.window, self.peng,
                                           pos=(0, 0),
                                           size=(lambda sw, sh: (sw, sh)))
        self.bg_widget.setBackground(peng3d.gui.button.FramedImageBackground(
            self.bg_widget,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )
        self.bg_widget.bg.vlist_layer = 10
        self.bg_widget.clickable = False
        self.addWidget(self.bg_widget)

        # Heading
        self.kick_heading = peng3d.gui.Label(
            "kick_heading", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 2], [2, 1]),
            label="",
            font_size=25,
            label_layer=11,
        )
        self.kick_heading.clickable = False
        self.addWidget(self.kick_heading)

        # Input field for username
        self.input_field = cgclient.gui.CGTextInput(
            "kick_input", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 1], [2, 1]),
            font_size=25
        )
        self.input_field.bg.parent.vlist_layer = 11
        self.input_field.bg.vlist_cursor_layer = 12
        self.addWidget(self.input_field)

        # Ok Button
        self.okbtn = cgclient.gui.CGButton(
            "kick_okbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.kick_okbtn.label"),
            label_layer=12,
        )
        self.okbtn.bg.vlist_layer = 11
        self.addWidget(self.okbtn)

        def f():
            if self.kick_player is None:
                return
            self.peng.cg.client.send_message("cg:lobby.kick", {
                "uuid": self.kick_player.uuid.hex,
                "reason": self.input_field.text
            })
            self.visible = False
            self.input_field.text = ""
            self.kick_player = None

        self.okbtn.addAction("click", f)

        # Cancel Button
        self.cancelbtn = cgclient.gui.CGButton(
            "kick_cancelbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.kick_cancelbtn.label"),
            label_layer=12,
        )
        self.cancelbtn.bg.vlist_layer = 11
        self.addWidget(self.cancelbtn)

        def f():
            self.visible = False
            self.input_field.text = ""
            self.kick_player = None

        self.cancelbtn.addAction("click", f)

    def init_kick(self, player):
        self.kick_player = player
        self.kick_heading.label = self.peng.tl("cg:gui.menu.smain.lobby.kick_heading", {"username": player.username})


class TemplateSaveDialog(peng3d.gui.Container):
    def __init__(self, name, submenu, window, peng, pos, size):
        super().__init__(name, submenu, window, peng,
                         pos, size)

        self.visible = False

        self.s_template = self.menu.menu.s_template

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [2, 3], [30, 20])

        self.bg_widget = peng3d.gui.Widget("bg", self, self.window, self.peng,
                                           pos=(0, 0),
                                           size=(lambda sw, sh: (sw, sh)))
        self.bg_widget.setBackground(peng3d.gui.button.FramedImageBackground(
            self.bg_widget,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )
        self.bg_widget.bg.vlist_layer = 10
        self.bg_widget.clickable = False
        self.addWidget(self.bg_widget)

        # Heading
        self.save_heading = peng3d.gui.Label(
            "save_heading", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 2], [2, 1]),
            label=self.peng.tl("cg:gui.menu.smain.gamerule.save_template_heading"),
            font_size=25,
            label_layer=11,
        )
        self.save_heading.clickable = False
        self.addWidget(self.save_heading)

        # Input field for username
        self.input_field = cgclient.gui.CGTextInput(
            "save_input", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 1], [2, 1]),
            font_size=25
        )
        self.input_field.bg.parent.vlist_layer = 11
        self.input_field.bg.vlist_cursor_layer = 12
        self.addWidget(self.input_field)

        # Ok Button
        self.okbtn = cgclient.gui.CGButton(
            "save_okbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.gamerule.save_okbtn.label"),
            label_layer=12,
        )
        self.okbtn.bg.vlist_layer = 11
        self.addWidget(self.okbtn)

        def f():
            if self.input_field.text != "":
                if len(self.s_template.save_opts) >= 18:
                    self.cg.warn("Maximum amount of templates reached, cannot create new template")
                    return

                gamerule_copy = {
                    key: value.copy() if type(value) == list else value for key, value in
                    self.peng.cg.client.lobby.gamerules.items()
                }

                _saves = self.s_template.saves
                _saves[self.input_field.text] = gamerule_copy
                self.s_template.saves = _saves

                _save_opts = self.s_template.save_opts
                _save_opts.append(self.input_field.text)
                self.s_template.save_opts = _save_opts

                self.visible = False
                self.input_field.text = ""

        self.okbtn.addAction("click", f)

        # Cancel Button
        self.cancelbtn = cgclient.gui.CGButton(
            "save_cancelbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.gamerule.save_cancelbtn.label"),
            label_layer=12,
        )
        self.cancelbtn.bg.vlist_layer = 11
        self.addWidget(self.cancelbtn)

        def f():
            self.visible = False
            self.input_field.text = ""

        self.cancelbtn.addAction("click", f)


class GameRuleContainer(peng3d.gui.Container):
    def __init__(self, name, submenu, window, peng, pos, size,
                 page_num, gamerules):
        super().__init__(name, submenu, window, peng,
                         pos, size)

        self.visible = False

        self.grid = self.submenu.grid

        self.page = page_num
        self.gamerules = gamerules
        self.gamerule_btns = {}

        c = 0
        for gamerule in self.gamerules:
            grdat = self.peng.cg.client.lobby.gamerule_validators[gamerule].copy()
            if grdat["type"] == "bool":
                cls = BoolRuleButton
            elif grdat["type"] == "number":
                cls = NumberRuleButton
            elif grdat["type"] == "select":
                cls = SelectRuleButton
            elif grdat["type"] == "active":
                cls = ActivetRuleButton
            elif grdat["type"] == "str":
                cls = StrRuleButton
            else:
                self.peng.cg.fatal(f"Invalid type: {grdat['type']} for gamerule {gamerule}")
                self.peng.cg.crash("Failed generating gamerule menu for a rule had an invalid type")
                return

            del grdat["type"]
            self.gamerule_btns[c] = cls(gamerule, self, window, peng,
                                        self.grid.get_cell([0, 3 - 2 * c], [12, 2], border=0), None,
                                        gamerule, **grdat)
            self.addWidget(self.gamerule_btns[c])
            self.submenu.rule_buttons[gamerule] = self.gamerule_btns[c]
            c += 1


class RuleButton(peng3d.gui.Container):
    def __init__(self, name, submenu, window, peng,
                 pos, size, gamerule, default, requirements):
        super().__init__(name, submenu, window, peng, pos, size)

        self.gamerule = gamerule
        self.default_val = default
        self.requirements = requirements

        self.setBackground(peng3d.gui.FramedImageBackground(
            self,
            bg_idle=("cg:img.bg.bg_dark_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3)
        ))
        self.bg.vlist_layer = -2

        self.grid = peng3d.gui.GridLayout(self.peng, self, [2, 15], [60, 10])

        # 2nd Background
        self.disabled_background = peng3d.gui.Widget(
            "bg_disabled", self, self.window, self.peng,
            self.grid.get_cell([0, 0], [2, 15], border=0)
        )
        self.disabled_background.setBackground(peng3d.gui.FramedImageBackground(
            self.disabled_background,
            bg_idle=("cg:img.bg.bg_gray", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3)
        ))
        self.disabled_background.bg.vlist_layer = -1
        self.disabled_background.clickable = False
        self.addWidget(self.disabled_background)
        self.disabled_background.visible = False

        # Game rule label
        self.gamerule_label = peng3d.gui.Label(
            "gamerule_label", self, self.window, self.peng,
            self.grid.get_cell([0, 13], [2, 2]),
            label=self.peng.tl(f"cg:gamerule.{self.gamerule}.name"),
            font_size=30,
            multiline=True
        )
        self.gamerule_label.clickable = False
        self.addWidget(self.gamerule_label)

        # Game rule description
        self.description_label = peng3d.gui.Label(
            "description_label", self, self.window, self.peng,
            self.grid.get_cell([0, 11], [2, 1]),
            label=self.peng.tl(f"cg:gamerule.{self.gamerule}.description"),
            font_size=20,
            multiline=True
        )
        self.description_label.clickable = False
        self.addWidget(self.description_label)

    def set_rule(self, data):
        pass

    @property
    def enabled(self):
        return not self.disabled_background.visible


class BoolRuleButton(RuleButton):
    def __init__(self, name, submenu, window, peng,
                 pos, size,
                 gamerule, default, requirements):
        super().__init__(name, submenu, window, peng, pos, size,
                         gamerule, default, requirements)

        self.opt_grid = peng3d.gui.GridLayout(
            self.peng, self.grid.get_cell([0, 0], [2, 9]), [2, 1], [100, 0]
        )

        # Yes Button
        self.yesbtn = peng3d.gui.ToggleButton(
            "yesbtn", self, self.window, self.peng,
            pos=self.opt_grid.get_cell(
                [0, 0], [1, 1], border=0, anchor_y="center"
            ),
            size=(lambda sw, sh: (sh * 0.06, sh * 0.06)),
            label=""
        )
        self.yesbtn.setBackground(peng3d.gui.ImageBackground(
            self.yesbtn,
            bg_idle=("cg:img.btn.sce", "gui"),
            bg_pressed=("cg:img.btn.scf", "gui"),
        ))
        self.addWidget(self.yesbtn)

        def f():
            self.nobtn.pressed = False
            self.nobtn.doAction("press_up")
            self.nobtn.redraw()

            self.peng.cg.client.send_message("cg:lobby.change", {
                "gamerules": {self.gamerule: True}
            })

        self.yesbtn.addAction("press_down", f)

        def f():
            self.nobtn.pressed = True
            self.nobtn.redraw()

        self.yesbtn.addAction("press_up", f)

        # Yes Label
        self.yeslbl = peng3d.gui.Label(
            "yeslbl", self, self.window, self.peng,
            pos=self.opt_grid.get_cell(
                [0, 0], [1, 1], anchor_y="center"
            ),
            size=(lambda sw, sh: (sw / 2 - 120, 0)),
            label=self.peng.tl("cg:gamerule.opt.true"),
            multiline=True,
            font_size=16,
            anchor_y="baseline",
        )
        self.yeslbl.clickable = False
        self.addWidget(self.yeslbl)

        # No Button
        self.nobtn = peng3d.gui.ToggleButton(
            "nobtn", self, self.window, self.peng,
            pos=self.opt_grid.get_cell(
                [1, 0], [1, 1], border=0, anchor_y="center"
            ),
            size=(lambda sw, sh: (sh * 0.06, sh * 0.06)),
            label=""
        )
        self.nobtn.setBackground(peng3d.gui.ImageBackground(
            self.nobtn,
            bg_idle=("cg:img.btn.sce", "gui"),
            bg_pressed=("cg:img.btn.scf", "gui"),
        ))
        self.addWidget(self.nobtn)

        def f():
            self.yesbtn.pressed = False
            self.yesbtn.doAction("press_up")
            self.yesbtn.redraw()

            self.peng.cg.client.send_message("cg:lobby.change", {
                "gamerules": {self.gamerule: False}
            })

        self.nobtn.addAction("press_down", f)

        def f():
            self.yesbtn.pressed = True
            self.yesbtn.redraw()

        self.nobtn.addAction("press_up", f)

        # No Label
        self.nolbl = peng3d.gui.Label(
            "nolbl", self, self.window, self.peng,
            pos=self.opt_grid.get_cell(
                [1, 0], [1, 1], anchor_y="center"
            ),
            size=(lambda sw, sh: (sw / 2 - 120, 0)),
            label=self.peng.tl("cg:gamerule.opt.false"),
            multiline=True,
            font_size=16,
            anchor_y="baseline",
        )
        self.nolbl.clickable = False
        self.addWidget(self.nolbl)

    def set_rule(self, data):
        self.yesbtn.pressed = data
        self.yesbtn.redraw()

        self.nobtn.pressed = not data
        self.nobtn.redraw()


class NumberRuleButton(RuleButton):
    def __init__(self, name, submenu, window, peng,
                 pos, size,
                 gamerule, default, min, max, step, requirements):
        super().__init__(name, submenu, window, peng, pos, size,
                         gamerule, default, requirements)

        # TODO Implement this Button


class SelectRuleButton(RuleButton):
    def __init__(self, name, submenu, window, peng,
                 pos, size,
                 gamerule, default, options, requirements):
        super().__init__(name, submenu, window, peng, pos, size,
                         gamerule, default, requirements)

        self.length = len(options)
        self.options = options

        self.buttons = {}
        self.labels = {}

        if self.length in [2, 4]:
            self.opt_grid = peng3d.gui.GridLayout(
                self.peng, self.grid.get_cell([0, 0], [2, 9]), [2, self.length / 2], [100, 0]
            )
        else:
            self.opt_grid = peng3d.gui.GridLayout(
                self.peng, self.grid.get_cell([0, 0], [2, 9]), [3, math.ceil(self.length / 3)], [100, 0]
            )

        def f(button):
            for i in self.buttons.values():
                if i != button:
                    i.pressed = False
                    i.redraw()

            self.peng.cg.client.send_message("cg:lobby.change", {
                "gamerules": {self.gamerule: button.name}
            })

        def f2(button):
            button.pressed = True
            button.redraw()

        for i, option in enumerate(self.options):
            btn = peng3d.gui.ToggleButton(
                option, self, self.window, self.peng,
                pos=self.opt_grid.get_cell(
                    [i % (2 if self.length in [2, 4] else 3),
                     self.opt_grid.res[1] - 1 - (i // (2 if self.length in [2, 4] else 3))],
                    [1, 1], border=0, anchor_y="center"
                ),
                size=(lambda sw, sh: (sh * 0.06, sh * 0.06)),
                label=""
            )
            btn.setBackground(peng3d.gui.ImageBackground(
                btn,
                bg_idle=("cg:img.btn.sce", "gui"),
                bg_pressed=("cg:img.btn.scf", "gui"),
            ))
            self.addWidget(btn)

            btn.addAction("press_down", f, btn)
            btn.addAction("press_up", f2, btn)

            self.buttons[option] = btn

            lbl = peng3d.gui.Label(
                option + "lbl", self, self.window, self.peng,
                pos=self.opt_grid.get_cell(
                    [i % (2 if self.length in [2, 4] else 3),
                     self.opt_grid.res[1] - 1 - (i // (2 if self.length in [2, 4] else 3))],
                    [1, 1], anchor_y="center"
                ),
                size=(lambda sw, sh: (sw / (2 if self.length in [2, 4] else 3) - 120, 0)),
                label=self.peng.tl(f"cg:gamerule.{self.gamerule}.opt.{option}"),
                multiline=True,
                font_size=16,
                anchor_y="baseline",
            )
            lbl.clickable = False
            self.addWidget(lbl)

            self.labels[option] = lbl

    def set_rule(self, data):
        for btn in self.buttons.values():
            btn.pressed = False
            btn.redraw()
        self.buttons[data].pressed = True
        self.buttons[data].redraw()


class ActivetRuleButton(RuleButton):
    def __init__(self, name, submenu, window, peng,
                 pos, size,
                 gamerule, default, options, requirements):
        super().__init__(name, submenu, window, peng, pos, size,
                         gamerule, default, requirements)

        self.length = len(options)
        self.options = options

        self.buttons = {}
        self.labels = {}

        if self.length in [2, 4]:
            self.opt_grid = peng3d.gui.GridLayout(
                self.peng, self.grid.get_cell([0, 0], [2, 9]), [2, self.length / 2], [100, 0]
            )
        else:
            self.opt_grid = peng3d.gui.GridLayout(
                self.peng, self.grid.get_cell([0, 0], [2, 9]), [3, math.ceil(self.length / 3)], [100, 0]
            )

        for i, option in enumerate(self.options):
            btn = peng3d.gui.ToggleButton(
                option, self, self.window, self.peng,
                pos=self.opt_grid.get_cell(
                    [i % (2 if self.length in [2, 4] else 3),
                     self.opt_grid.res[1] - 1 - (i // (2 if self.length in [2, 4] else 3))],
                    [1, 1], border=0, anchor_y="center"
                ),
                size=(lambda sw, sh: (sh * 0.06, sh * 0.06)),
                label=""
            )
            btn.setBackground(peng3d.gui.ImageBackground(
                btn,
                bg_idle=("cg:img.btn.mce", "gui"),
                bg_pressed=("cg:img.btn.mcf", "gui"),
            ))
            self.addWidget(btn)

            def f():
                actives = []
                for i in self.buttons.values():
                    if i.pressed:
                        actives.append(i.name)

                self.peng.cg.client.send_message("cg:lobby.change", {
                    "gamerules": {self.gamerule: actives}
                })

            btn.addAction("press_down", f)
            btn.addAction("press_up", f)

            self.buttons[option] = btn

            lbl = peng3d.gui.Label(
                option + "lbl", self, self.window, self.peng,
                pos=self.opt_grid.get_cell(
                    [i % (2 if self.length in [2, 4] else 3),
                     self.opt_grid.res[1] - 1 - (i // (2 if self.length in [2, 4] else 3))],
                    [1, 1], anchor_y="center"
                ),
                size=(lambda sw, sh: (sw / (2 if self.length in [2, 4] else 3) - 120, 0)),
                label=self.peng.tl(f"cg:gamerule.{self.gamerule}.opt.{option}"),
                multiline=True,
                font_size=16,
                anchor_y="baseline",
            )
            lbl.clickable = False
            self.addWidget(lbl)

            self.labels[option] = lbl

    def set_rule(self, data):
        for btn in self.buttons.values():
            btn.pressed = btn.name in data
            btn.redraw()


class StrRuleButton(RuleButton):
    def __init__(self, name, submenu, window, peng,
                 pos, size,
                 gamerule, default, minlen, maxlen, requirements):
        super().__init__(name, submenu, window, peng, pos, size,
                         gamerule, default, requirements)

        # TODO Implement this Button
