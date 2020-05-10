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
from typing import Tuple, Union

import peng3d

import cgclient.gui
from pyglet.window.mouse import LEFT

GAMES = [
    "sk",       # Skat
    "dk",       # Doppelkopf
    "rm",       # Romme
    "cn",       # Canasta
]

GAME_VARIANTS = [
    "c",        # Custom
    "m",        # Modified
    "s",        # Standard
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
        self.d_create_acc.wbtn_confirm.size = lambda sw, sh: (sw/5, 64)
        self.d_create_acc.wbtn_cancel.pos = lambda sw, sh, bw, bh: (sw/2+5, sh/2 - bh*2)
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
            print("hi")
            self.cg.client.send_message("cg:lobby.invite.accept", {
                "accepted": True,
                "lobby_id": self.cg.client.lobby_invitation[1].hex,
                "inviter": self.cg.client.lobby_invitation[0].hex,
            })
        self.d_lobby_inv.addAction("confirm", f)

        def f():
            print("bye")
            self.cg.client.send_message("cg:lobby.invite.accept", {
                "accepted": False,
                "lobby_id": self.cg.client.lobby_invitation[1].hex,
                "inviter": self.cg.client.lobby_invitation[0].hex,
            })
        self.d_lobby_inv.addAction("cancel", f)

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

        w = self.subgrid_1.get_cell([1, 1], [2, 3], "center", "center").pos[0] / self.window.width
        h = self.subgrid_1.get_cell([1, 1], [2, 3], "center", "center").pos[1] / self.window.height
        sx = self.subgrid_1.get_cell([1, 1], [2, 3]).size[0] / self.window.width
        def s(sw, sh):
            return sw*sx, sw*sx
        # Profile Image
        self.profile_img = peng3d.gui.ImageButton(
            "profileimg", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw*w - bw/2, sh*h - bh/2)),
            #size=(lambda sw, sh: (sw*sx, sw*sx)),
            size=s,
            bg_idle=("cg:img.profilbild", "gui"),
            label="",
        )
        self.addWidget(self.profile_img)

        # Profile Label
        self.profile_label = peng3d.gui.Label(
            "profilelbl", self, self.window, self.peng,
            pos=self.subgrid_1.get_cell([1, 0], [2, 1]),
            label="<unknown>",  # This should be the username
            anchor_x="center",
            anchor_y="center",
        )
        self.addWidget(self.profile_label)

        def f1(button):
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
            frame=[[1, 2, 1], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        ))

        self.partybtn.addAction("press_down", f1, self.partybtn)
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

        self.lbbtn.addAction("press_down", f1, self.lbbtn)
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

        self.profilebtn.addAction("press_down", f1, self.profilebtn)
        self.addWidget(self.profilebtn)

        # Settings Button
        # This button switches to the settings submenu
        self.settingsbtn = cgclient.gui.CGButton(
            "settingsbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.smain.main.settingsbtn.label"),
        )
        self.addWidget(self.settingsbtn)

        def f():
            self.window.changeMenu("settings")
            self.window.menu.prev_menu = "servermain"
        self.settingsbtn.addAction("click", f)
        self.settingsbtn.addAction("click", f1, self.settingsbtn)

        self.togglebuttons = [self.playbtn, self.partybtn, self.lbbtn, self.profilebtn]

        # Play Container
        self.c_play = PlayContainer("play", self, self.window, self.peng,
                                    pos=(lambda sw, sh, bw, bh: (sw/3, 0)),
                                    size=(lambda sw, sh: (sw*2/3, sh))
                                    )
        self.addWidget(self.c_play)

        # Party Container

        # Leaderboard Container

        # Profile Container

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

    def handler_login(self, event: str, data: dict):
        self.profile_label.label = self.menu.cg.client.users_uuid[self.menu.cg.client.user_id].username


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
        self.addWidget(self.w_lower_bar)

        # Game Label
        self.game_label = peng3d.gui.Label("lobby_game_label", self, self.window, self.peng,
                                           pos=(lambda sw, sh, bw, bh: (sw/2, sh*19/24)),
                                           size=(lambda sw, sh: (0, sh/6)),
                                           label=self.peng.tl("None"),  # This will be changed later
                                           font_size=40,
                                           )
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
        self.leavebtn.addAction("click", f)

        # Game Button
        self.gamebtn = cgclient.gui.CGButton(
            "gamebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [3, 2]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.gamebtn.label")
        )
        self.addWidget(self.gamebtn)

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
        self.readybtn = cgclient.gui.CGButton(
            "readybtn", self, self.window, self.peng,
            pos=self.grid.get_cell([3, 0], [3, 4]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.readybtn.label"),
        )
        self.addWidget(self.readybtn)

        def f():
            self.menu.cg.client.send_message("cg:lobby.ready", {"ready": True})
        self.readybtn.addAction("click", f)

        # Player list
        self.w_player_0 = PlayerButton(
            "player0btn", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (3, sh * (2 / 9 + 3 * 11 / 72))),
            size=(lambda sw, sh: (sw-6, sh * 11 / 72)),
            player=None
        )
        self.addWidget(self.w_player_0)

        self.w_player_1 = PlayerButton(
            "player1btn", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (3, sh * (2 / 9 + 2 * 11 / 72))),
            size=(lambda sw, sh: (sw-6, sh * 11 / 72)),
            player=None
        )
        self.addWidget(self.w_player_1)

        self.w_player_2 = PlayerButton(
            "player2btn", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (3, sh * (2 / 9 + 1 * 11 / 72))),
            size=(lambda sw, sh: (sw-6, sh * 11 / 72)),
            player=None
        )
        self.addWidget(self.w_player_2)

        self.w_player_3 = PlayerButton(
            "player3btn", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (3, sh * (2 / 9))),
            size=(lambda sw, sh: (sw-6, sh * 11 / 72)),
            player=None
        )
        self.addWidget(self.w_player_3)

        self.player_buttons = {
            0: self.w_player_0,
            1: self.w_player_1,
            2: self.w_player_2,
            3: self.w_player_3
        }

        self.c_invite = InviteDialog(
            "c_invite", self, self.window, self.peng,
            pos=self.grid.get_cell([3, 6], [3, 6]),
            size=None
        )
        self.addWidget(self.c_invite)

    def register_event_handlers(self):
        self.menu.cg.add_event_listener("cg:lobby.game.change", self.handle_game_change)

    def handle_game_change(self, event: str, data: dict):
        self.game_label.label = self.peng.tl(f"cg:game.{data['game']}")


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

        ar = 12/7  # Aspect ratio of icons
        # TODO: maybe do not hardcode this anymore

        def b(x, y, sx, sy) -> Tuple[int, int]:
            if sy/2 > sx:
                # X-Axis is constraining factor
                s = sx
                return (sx-s)/2, (sy-s)/2
            else:
                # Y-Axis is constraining factor
                s = sy/2
                return (sx-s)/2/ar, (sy-s)/2

        def o(x, y, sx, sy):
            if sy/2 > sx:
                # X-Axis is constraining factor
                s = sx
                return 0, s/2
            else:
                # Y-Axis is constraining factor
                s = sy/2
                return 0, s/2

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
            font="Times New Roman",
            font_size=22,
            font_color=[255, 255, 255, 100],
            offset=[0, -20]
        )
        self.addLayer(self.label1_layer)

        self.label2_layer = peng3d.gui.LabelWidgetLayer(
            "label2_layer", self, 3,
            label=self.peng.tl(f"cg:gui.menu.smain.play.{self.game}{self.variant}.label.1"),
            font="Times New Roman",
            font_size=16,
            font_color=[255, 255, 255, 100],
            offset=[0, -20-22-8],
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
    ready = False


class PlayerButton(peng3d.gui.LayeredWidget):
    def __init__(self, name, submenu, window, peng, pos, size,
                 player):
        super().__init__(name, submenu, window, peng, pos, size)

        self._player = player

        # Background
        self.bg_layer = peng3d.gui.DynImageWidgetLayer(
            "bg_layer", self,
            z_index=1,
            imgs={
                "idle": ("cg:img.bg.transparent", "gui"),
                "hover": ("cg:img.bg.gray_brown", "gui")
            }
        )
        self.bg_layer.switchImage("idle")
        self.addLayer(self.bg_layer)

        def f():
            if self._player is not None:
                self.bg_layer.switchImage("hover")
        self.addAction("hover_start", f)

        def f():
            self.bg_layer.switchImage("idle")
        self.addAction("hover_end", f)

        # TODO Add user icon

        # Username
        self.username_label_layer = peng3d.gui.LabelWidgetLayer(
            "username_label_layer", self,
            z_index=2,
            label=self.player.username,
            font="Times New Roman",
            font_size=30,
            font_color=[255, 255, 255, 100],
            offset=(lambda bx, by, bw, bh: (-bw/2 + 20, 0))
        )
        self.username_label_layer._label.anchor_x = "left"
        self.addLayer(self.username_label_layer)

        self.mouse_offset = []
        self.is_dragged = False

    @property
    def clickable(self):
        return super().clickable and self.player.username != ""

    @property
    def player(self):
        if self._player is None:
            return _FakeUser()
        else:
            return self._player

    @player.setter
    def player(self, value: Union[cgclient.user.User, _FakeUser]):
        self._player = value
        self.username_label_layer.label = self.player.username

    @property
    def ready(self):
        return self.player.ready

    @ready.setter
    def ready(self, value):
        pass
        # TODO Update ready indicator

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
                        next_button.pos = (lambda sw, sh, bw, bh: (3, sh * (2 / 9 + ((3 - index) * 11 / 72))))
                        next_button.redraw()

            if index != 0:  # For the button above
                next_button = self.submenu.player_buttons[index - 1]
                if next_button.clickable:
                    if abs(next_button.pos[1] - self.pos[1]) < self.size[1] / 2:  # Closer to next pos than to own
                        self.submenu.player_buttons[index] = next_button
                        self.submenu.player_buttons[index - 1] = self
                        next_button.pos = (lambda sw, sh, bw, bh: (3, sh * (2 / 9 + ((3 - index) * 11 / 72))))
                        next_button.redraw()

    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        if self.clickable and self.is_hovering:
            if button == LEFT:
                self.mouse_offset = [x - self.pos[0], y - self.pos[1]]
                self.is_dragged = True

    def on_mouse_release(self,x,y,button,modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        if self.is_dragged:
            if button == LEFT:
                self.mouse_offset.clear()
                self.is_dragged = False

                for i, btn in self.submenu.player_buttons.items():
                    if btn == self:
                        self.pos = (lambda sw, sh, bw, bh: (3, sh * (2 / 9 + ((3 - i) * 11 / 72))))
                        self.redraw()
                        break


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
        self.addWidget(self.bg_widget)

        # Heading
        self.invite_heading = peng3d.gui.Label(
            "invite_heading", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 2], [2, 1]),
            label=self.peng.tl("cg:gui.menu.smain.lobby.invite_heading"),
            font="Times New Roman",
            font_size=25,
            label_layer=11,
        )
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
