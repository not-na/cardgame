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
import time

import peng3d

import cgclient.gui


class ServerMainMenu(peng3d.gui.GUIMenu):
    def __init__(self, name, window, peng, gui):
        super().__init__(name, window, peng,
                         font="Times New Roman",
                         font_size=25,
                         font_color=[255, 255, 255, 100],
                         )
        self.gui = gui
        self.cg = gui.cg

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
        self.d_create_acc.wbtn_confirm.pos = lambda sw, sh, bw, bh: (sw/2-bw-5, sh/2-bh*2)
        self.d_create_acc.wbtn_confirm.size = lambda sw, sh: (sw/5, 32)
        self.d_create_acc.wbtn_cancel.pos = lambda sw, sh, bw, bh: (sw/2+5, sh/2 - bh*2)
        self.d_create_acc.wbtn_cancel.size = lambda sw, sh: (sw / 5, 32)
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

        # Login Menu
        self.s_login = LoginSubMenu("login", self, self.window, self.peng)
        self.addSubMenu(self.s_login)

        # Main Menu
        self.s_main = MainSubMenu("main", self, self.window, self.peng)
        self.addSubMenu(self.s_main)

        # Lobby Menu
        self.s_lobby = LobbySubMenu("lobby", self, self.window, self.peng)
        self.addSubMenu(self.s_lobby)

        # Gamerule Menu
        self.s_gamerule = GameruleSubMenu("gamerules", self, self.window, self.peng)
        self.addSubMenu(self.s_gamerule)

        self.changeSubMenu("load")


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
        self.addWidget(self.screen_edge)

        self.subgrid_1 = peng3d.gui.layout.GridLayout(self.peng, self.grid.get_cell([0, 5], [1, 3]),
                                                      [4, 4], [60, 20])
        # Profile Image
        self.profile_img = peng3d.gui.ImageButton(
            "profileimg", self, self.window, self.peng,
            pos=self.subgrid_1.get_cell([1, 1], [2, 3]),
            bg_idle=("cg:img.profilbild", "gui"),
            label=""
        )
        self.addWidget(self.profile_img)

        # Profile Label
        self.profile_label = peng3d.gui.Label(
            "profilelbl", self, self.window, self.peng,
            pos=self.subgrid_1.get_cell([1, 0], [2, 1]),
            size=[0, 0],
            label="",  # This should be the username
            anchor_x="center",
            anchor_y="center"
        )
        self.addWidget(self.profile_label)

        def g(button):
            # Reset the previously pressed button
            for btn in self.togglebuttons:
                if btn != button and btn.pressed:
                    btn.pressed = False
                    btn.doAction("press_up")
                    btn.redraw()

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
            frame=[[1, 2, 1], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        ))

        self.playbtn.addAction("press_down", g, self.playbtn)
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
            frame=[[1, 2, 1], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        ))

        self.partybtn.addAction("press_down", g, self.partybtn)
        self.addWidget(self.partybtn)

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
            frame=[[1, 2, 1], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        ))

        self.lbbtn.addAction("press_down", g, self.lbbtn)
        self.addWidget(self.lbbtn)

        # Profile Button
        # This button switches to the profile container
        self.profilebtn = peng3d.gui.ToggleButton(
            "profilebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 1], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.main.profilebtn.label")
        )
        self.profilebtn.setBackground(peng3d.gui.FramedImageBackground(
            self.profilebtn,
            bg_idle=("cg:img.btn.btn_idle", "gui"),
            bg_hover=("cg:img.btn.btn_hov", "gui"),
            bg_pressed=("cg:img.btn.btn_press", "gui"),
            frame=[[1, 2, 1], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        ))

        self.profilebtn.addAction("press_down", g, self.profilebtn)
        self.addWidget(self.profilebtn)

        # Settings Button
        # This button switches to the settings submenu
        self.settingsbtn = cgclient.gui.CGButton(
            "settingsbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.main.settingsbtn.label"),
        )
        self.addWidget(self.settingsbtn)

        self.settingsbtn.addAction("click", g, self.settingsbtn)

        self.togglebuttons = [self.playbtn, self.partybtn, self.lbbtn, self.profilebtn]

        # Play Container
        self.c_play = PlayContainer("play", self, self.window, self.peng,
                                    pos=(lambda sw, sh, bw, bh: (sw/3, 0)),
                                    size=(lambda sw, sh: (sw*2/3, sh))
                                    )

        # Party Container

        # Leaderboard Container

        # Profile Container

    def register_event_handlers(self):
        self.menu.cg.add_event_listener("cg:network.client.login", self.handler_login)

    def handler_login(self, event: str, data: dict):
        self.profile_label.label = self.menu.cg.client.users_uuid[self.menu.cg.client.user_id].username


class LobbySubMenu(peng3d.gui.SubMenu):
    menu: ServerMainMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.label = peng3d.gui.Label("lobby_label", self, self.window, self.peng,
                                      pos=(lambda sw, sh, bw, bh: (sw / 2, sh / 2)),
                                      size=[0, 0],  # (lambda sw, sh: (sw, sh)),
                                      label="Hello Lobby!",
                                      font_size=40,
                                      anchor_x="center",
                                      anchor_y="center",
                                      )
        self.addWidget(self.label)

        # Gamerule Button
        self.gamerulebtn = cgclient.gui.CGButton(
            "gamerulebtn", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw / 2 - bw / 2, sh / 2 - bh / 2 - 5)),
            size=(lambda sw, sh: (sw / 2, 32)),
            label=self.peng.tl("cg:gui.menu.smain.lobby.gamerulebtn.label"),
        )
        self.addWidget(self.gamerulebtn)

        def f():
            self.menu.changeSubMenu("gamerules")
        self.gamerulebtn.addAction("click", f)


class GameruleSubMenu(peng3d.gui.SubMenu):
    menu: ServerMainMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.label = peng3d.gui.Label("label", self, self.window, self.peng,
                                      pos=(lambda sw, sh, bw, bh: (sw / 2, sh/2-bh*2)),
                                      size=[0, 0],  # (lambda sw, sh: (sw, sh)),
                                      label="Gamerules here",
                                      font_size=40,
                                      anchor_x="center",
                                      anchor_y="center",
                                      )
        self.addWidget(self.label)

        # Back Button
        self.backbtn = cgclient.gui.CGButton(
            "backbtn", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw / 2 - bw / 2, sh / 2 - bh / 2 - 5)),
            size=(lambda sw, sh: (sw / 2, 32)),
            label=self.peng.tl("cg:gui.menu.smain.gamerule.backbtn.label"),
        )
        self.addWidget(self.backbtn)

        def f():
            self.menu.changeSubMenu("lobby")
        self.backbtn.addAction("click", f)


class PlayContainer(peng3d.gui.Container):
    menu: ServerMainMenu

    def __init__(self, name, submenu, window, peng, pos, size):
        super().__init__(name, submenu, window, peng,
                         pos, size,
                         font_size=20)

        self.setBackground([67, 51, 12])


