#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  loadingscreen.py
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


class LoadingScreenMenu(peng3d.gui.GUIMenu):
    def __init__(self, name, window, peng, gui):
        super().__init__(name, window, peng)

        self.gui = gui
        self.cg = gui.cg

        self.s_loadingscreen = LoadingScreenSubMenu("loadingscreen", self, self.window, self.peng)
        self.addSubMenu(self.s_loadingscreen)

        self.changeSubMenu("loadingscreen")


class LoadingScreenSubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.setBackground(peng3d.gui.button.FramedImageBackground(
            peng3d.gui.FakeWidget(self),
            bg_idle=("cg:img.bg.bg_dark_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )

        self.w_label = peng3d.gui.Label(
            "label", self, self.window, self.peng,
            # Its not perfectly centered, but the loading screen shouldn't be visible for long anyway
            pos=(lambda sw, sh, bw, bh: (sw / 2, sh / 2)),
            size=[0, 0],
            label=self.peng.tl("cg:gui.menu.load.progress.init"),
            anchor_x="center",
            anchor_y="center",
            font="Times New Roman",
            font_color=[255, 255, 255, 100],
            font_size=40,
        )
        self.addWidget(self.w_label)

        self.has_drawn = False

    def draw(self):
        super().draw()

        # Initialize menus if we have been drawn at least once
        # Ensures that the loading screen is visible
        if self.has_drawn:
            self.peng.cg.client.gui.register_menus()
        else:
            self.has_drawn = True
