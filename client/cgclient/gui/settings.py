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
        super().__init__(name, menu, window, peng, font_size=30)

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [8, 10], [20, 20])

        self.label = peng3d.gui.Label(
            "label", self, self.window, self.peng,
            # TODO: fix alignment of this
            pos=self.grid.get_cell([0, 9], [8, 1], anchor_y="bottom"),
            label=self.peng.tl("cg:gui.menu.settings.label"),
            anchor_x="center",
            anchor_y="center",
            font_size=40,
            )
        self.addWidget(self.label)

        self.exitbtn = cgclient.gui.CGButton(
            "exitbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 9], [2, 1]),
            label=self.peng.tl("cg:gui.menu.settings.exitbtn.label"),
            )
        self.addWidget(self.exitbtn)

        def f():
            self.peng.cg.client.save_settings()
            self.window.changeMenu(self.menu.prev_menu)
        self.exitbtn.addAction("click", f)

        # Language Selector
        # TODO Add language discovery to windows
        self.langlabel = peng3d.gui.Label(
            "langlabel", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 7], [2, 1], anchor_x="left"),
            # size=[0,0],
            label=self.peng.tl("cg:gui.menu.settings.lang.label"),
            anchor_x="center",
        )
        self.addWidget(self.langlabel)

        self.langgrid = peng3d.gui.layout.GridLayout(
            self.peng,
            self.grid.get_cell([3, 7], [4, 1], border=0),
            [5, 1], [20, 20]
        )
        self.langlist = []

        self.langprevbtn = cgclient.gui.CGButton(
            "langprevbtn", self, self.window, self.peng,
            pos=self.langgrid.get_cell([0, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.settings.lang.prevbtn"),
            font_size=35,
        )
        self.addWidget(self.langprevbtn)

        def f():
            curlang = self.peng.i18n.lang
            if curlang not in self.langlist:
                self.peng.cg.error(f"Current language {curlang} not in available languages!")
                return
            curidx = self.langlist.index(curlang)
            idx = (curidx-1) % len(self.langlist)
            newlang = self.langlist[idx]

            self.peng.cg.info(f"Switching language to {newlang}")
            self.peng.i18n.setLang(newlang)

            self.peng.cg.client.settings["language"] = newlang
        self.langprevbtn.addAction("click", f)

        self.langnextbtn = cgclient.gui.CGButton(
            "langnextbtn", self, self.window, self.peng,
            pos=self.langgrid.get_cell([4, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.settings.lang.nextbtn"),
            font_size=35,
        )
        self.addWidget(self.langnextbtn)

        def f():
            curlang = self.peng.i18n.lang
            if curlang not in self.langlist:
                self.peng.cg.error(f"Current language {curlang} not in available languages!")
                return
            curidx = self.langlist.index(curlang)
            idx = (curidx + 1) % len(self.langlist)
            newlang = self.langlist[idx]

            self.peng.cg.info(f"Switching language to {newlang}")
            self.peng.i18n.setLang(newlang)

            self.peng.cg.client.settings["language"] = newlang
        self.langnextbtn.addAction("click", f)

        self.langcurlabel = peng3d.gui.Label(
            "langcurlabel", self, self.window, self.peng,
            pos=self.langgrid.get_cell([1, 0], [3, 1]),
            label=self.peng.tl("cg:meta.name.native"),
            font_size=35,
        )
        self.addWidget(self.langcurlabel)

        # Autosort for cards
        self.sortbtn = peng3d.gui.ToggleButton(
            "sortlabel", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 6], [6, 1]),
            label=self.peng.tl("cg:gui.menu.settings.sort.label"),
        )
        self.sortbtn.setBackground(cgclient.gui.CGButtonBG(self.sortbtn))
        self.addWidget(self.sortbtn)

        def f():
            self.menu.cg.client.settings["dk.sort_cards"] = not self.menu.cg.client.settings.get("dk.sort_cards", False)
        self.sortbtn.addAction("click", f)

        # TODO: maybe add UI for cursor type
        # TODO: add UI + logic for FPS limit / vsync

    def on_enter(self, old):
        self.langlist = self.peng.i18n.discoverLangs()

        self.peng.cg.info(f"Found {len(self.langlist)} languages")
        self.peng.cg.debug(f"Available languages: {self.langlist}")

        self.sortbtn.pressed = self.menu.cg.client.settings.get("dk.sort_cards", False)
