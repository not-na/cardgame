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

        self.s_loadconn = LoadConnectSubMenu("loadconn", self, self.window, self.peng)
        self.addSubMenu(self.s_loadconn)

        self.s_login = LoginSubMenu("login", self, self.window, self.peng)
        self.addSubMenu(self.s_login)

        self.changeSubMenu("loadconn")


class LoadConnectSubMenu(peng3d.gui.SubMenu):
    menu: ServerMainMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.setBackground([242, 241, 240])

        self.label = peng3d.gui.Label("load_label", self, self.window, self.peng,
                                      pos=(lambda sw, sh, bw, bh: (sw / 2, sh / 2)),
                                      size=[0, 0],  # (lambda sw, sh: (sw, sh)),
                                      label=self.peng.tl("cg:gui.menu.smain.loadconn.loading"),
                                      # font_size=20,
                                      anchor_x="center",
                                      anchor_y="center",
                                      )
        self.addWidget(self.label)


class LoginSubMenu(peng3d.gui.SubMenu):
    menu: ServerMainMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.setBackground([242, 241, 240])

        # TODO: implement this submenu
