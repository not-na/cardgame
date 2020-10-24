#!/usr/bin/env python
# -- coding: utf-8 --
#
#  updategame.py
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
#  along with cardgame.  If not, see http://www.gnu.org/licenses/.

import webbrowser

import peng3d
import cgclient.gui

WEBSITE_URL = "https://pycardgame.readthedocs.io/en/latest/updating.html"

class UpdateGameMenu(peng3d.gui.GUIMenu):
    def __init__(self, name, window, peng, gui):
        super().__init__(name, window, peng,
                         font="Times New Roman",
                         font_size=25,
                         font_color=[255, 255, 255, 100],
                         )

        self.register_event_handlers()

        self.gui = gui
        self.old_menu = ""

        self.setBackground(peng3d.gui.button.FramedImageBackground(
            peng3d.gui.FakeWidget(self),
            bg_idle=self.peng.resourceMgr.getTex("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(0.3, 0.3),
            tex_size=self.peng.resourceMgr.getTexSize("cg:img.bg.bg_brown", "gui"),
        )
        )

        self.s_update = UpdateGameSubMenu("update", self, self.window, self.peng)
        self.addSubMenu(self.s_update)

        self.changeSubMenu("update")

    def register_event_handlers(self):
        self.peng.cg.add_event_listener("cg:update.available", self.handler_update_available)

    def handler_update_available(self, event, data):
        dat = {
            "oldver": data["cur"],
            "newver": data["latest"],
        }

        self.s_update.body_label_1.label = self.peng.tl("cg:gui.menu.update.body.1", dat)
        self.s_update.body_label_2.label = self.peng.tl("cg:gui.menu.update.body.2", dat)
        self.s_update.body_label_3.label = self.peng.tl("cg:gui.menu.update.body.3", dat)

        self.window.changeMenu("updategame")

    def on_enter(self, old):
        super().on_enter(old)
        self.old_menu = old


class UpdateGameSubMenu(peng3d.gui.SubMenu):
    menu: UpdateGameMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.grid = peng3d.gui.GridLayout(self.peng, self, [5, 6], [60, 60])

        # Headline
        self.head_label = peng3d.gui.Label("headlabel", self, self.window, self.peng,
                                           pos=self.grid.get_cell([2, 4], [1, 1]),
                                           label=self.peng.tl("cg:gui.menu.update.header"),
                                           font_size=50,
                                           )
        self.addWidget(self.head_label)

        # Body Label
        self.middle_grid = peng3d.gui.GridLayout(self.peng, self.grid.get_cell([2, 2], [1, 2], border=0), [1, 6], [0, 0])

        self.body_label_1 = peng3d.gui.Label("bdylbl1", self, self.window, self.peng,
                                             pos=self.middle_grid.get_cell([0, 4], [1, 1]),
                                             label=self.peng.tl("cg:gui.menu.update.body.1"),
                                             )
        self.addWidget(self.body_label_1)

        self.body_label_2 = peng3d.gui.Label("bdylbl2", self, self.window, self.peng,
                                             pos=self.middle_grid.get_cell([0, 3], [1, 1]),
                                             label=self.peng.tl("cg:gui.menu.update.body.2"),
                                             )
        self.addWidget(self.body_label_2)

        self.body_label_3 = peng3d.gui.Label("bdylbl3", self, self.window, self.peng,
                                             pos=self.middle_grid.get_cell([0, 2], [1, 1]),
                                             label=self.peng.tl("cg:gui.menu.update.body.3"),
                                             )
        self.addWidget(self.body_label_3)

        # Update Button
        self.update_btn = cgclient.gui.CGButton(
            "updatebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 1], [1, 1]),
            label=self.peng.tl("cg:gui.menu.update.updatebtn.label"),
        )
        self.addWidget(self.update_btn)

        def f():
            webbrowser.open(url=WEBSITE_URL, autoraise=True)
        self.update_btn.addAction("click", f)

        # Cancel Button
        self.cancel_btn = cgclient.gui.CGButton(
            "cancelbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([3, 1], [1, 1]),
            label=self.peng.tl("cg:gui.menu.update.cancelbtn.label"),
        )
        self.addWidget(self.cancel_btn)

        def f():
            self.window.changeMenu(self.menu.old_menu)
        self.cancel_btn.addAction("click", f)
