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

import peng3d

import cgclient.gui


class ServerMainMenu(peng3d.gui.GUIMenu):
    def __init__(self, name, window, peng, gui):
        super().__init__(name, window, peng)

        self.gui = gui
        self.cg = gui.cg

        self.d_load = peng3d.gui.TextSubMenu(
            "load", self, self.window, self.peng,
            label_main=self.peng.tl("cg:gui.menu.smain.load.load"),
            timeout=-1,
        )
        self.addSubMenu(self.d_load)

        self.d_load.setBackground([242, 241, 240])

        self.s_login = LoginSubMenu("login", self, self.window, self.peng)
        self.addSubMenu(self.s_login)

        self.d_create_acc = peng3d.gui.menus.ConfirmSubMenu(
            "create_acc", self, self.window, self.peng,
            label_confirm=self.peng.tl("cg:gui.menu.smain.create_acc.confirm"),
            label_cancel=self.peng.tl("cg:gui.menu.smain.create_acc.cancel"),
            label_main=self.peng.tl("cg:gui.menu.smain.create_acc.label_main"),
        )
        self.addSubMenu(self.d_create_acc)

        self.d_create_acc.setBackground([242, 241, 240])

        def f():
            self.cg.client.send_message("cg:auth", {
                "username": self.s_login.user.text.strip(),
                "pwd": self.s_login.pwd.text,
                "create": True,
            })
        self.d_create_acc.addAction("confirm", f)

        self.d_login_err = peng3d.gui.menus.DialogSubMenu(
            "login_err", self, self.window, self.peng,
            label_main=self.peng.tl("cg:gui.menu.smain.loginerr.unknown"),
            label_ok=self.peng.tl("cg:gui.menu.smain.loginerr.ok"),
        )
        self.addSubMenu(self.d_login_err)

        self.d_login_err.setBackground([242, 241, 240])

        self.s_main = MainSubMenu("main", self, self.window, self.peng)
        self.addSubMenu(self.s_main)

        self.changeSubMenu("load")


class LoginSubMenu(peng3d.gui.SubMenu):
    menu: ServerMainMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.setBackground([242, 241, 240])

        # Username Field
        default_user = self.menu.cg.client.username
        self.user = peng3d.gui.TextInput(
            "user", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw/2-bw/2, sh/2+bh/2+5)),
            size=(lambda sw, sh: (sw/2, 32)),
            text=default_user,
            borderstyle="oldshadow",
            font_size=16,
        )
        self.addWidget(self.user)

        # Password Field
        # TODO: use an actual password field
        default_pwd = self.menu.cg.client.pwd
        self.pwd = peng3d.gui.TextInput(
            "pwd", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw/2-bw/2, sh/2+bh*1.5+5)),
            size=(lambda sw, sh: (sw/2, 32)),
            text=default_pwd,
            borderstyle="oldshadow",
            font_size=16,
        )
        self.addWidget(self.pwd)

        # OK Button
        self.okbtn = peng3d.gui.Button(
            "okbtn", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw/2-bw/2, sh/2-bh/2-5)),
            size=(lambda sw, sh: (sw/2, 32)),
            label=self.peng.tl("cg:gui.menu.smain.login.okbtn.label"),
            borderstyle="oldshadow",
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

        self.setBackground([242, 241, 240])

        self.label = peng3d.gui.Label("load_label", self, self.window, self.peng,
                                      pos=(lambda sw, sh, bw, bh: (sw / 2, sh / 2)),
                                      size=[0, 0],  # (lambda sw, sh: (sw, sh)),
                                      label="Hello World!",
                                      # font_size=20,
                                      anchor_x="center",
                                      anchor_y="center",
                                      )
        self.addWidget(self.label)
