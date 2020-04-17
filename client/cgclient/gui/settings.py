#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  settings.py
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


class SettingsMenu(peng3d.gui.GUIMenu):
    def __init__(self, name, window, peng, gui):
        super().__init__(name, window, peng,
                         font="Times New Roman",
                         font_size=25,
                         font_color=[255, 255, 255, 100]
                         )

        self.gui = gui
        self.cg = gui.cg

        self.prev_menu = None

        self.setBackground(peng3d.gui.button.FramedImageBackground(
            peng3d.gui.FakeWidget(self),
            bg_idle=self.peng.resourceMgr.getTex("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
            tex_size=self.peng.resourceMgr.getTexSize("cg:img.bg.bg_brown", "gui")
        )
        )
        self.bg.vlist_layer = -3

        self.s_settings = SettingsSubMenu("settings", self, self.window, self.peng)
        self.addSubMenu(self.s_settings)

        self.changeSubMenu("settings")


class SettingsSubMenu(peng3d.gui.SubMenu):
    menu: SettingsMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [3, 10], [10, 10])

        self.label = peng3d.gui.Label(
            "label", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 6], [1, 1]),
            label="Settings here",
            anchor_x="center",
            anchor_y="center",
            )
        self.addWidget(self.label)

        self.exitbtn = cgclient.gui.CGButton(
            "exitbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 4], [1, 1]),
            label=self.peng.tl("cg:gui.menu.settings.exitbtn.label"),
            )
        self.addWidget(self.exitbtn)

        def f():
            self.window.changeMenu(self.menu.prev_menu)
        self.exitbtn.addAction("click", f)
