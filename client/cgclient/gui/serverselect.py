#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  serverselect.py
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


class ServerSelectMenu(peng3d.gui.GUIMenu):
    def __init__(self, name, window, peng, gui):
        super().__init__(name, window, peng,
                         font="Times New Roman",
                         font_size=30,
                         font_color=[255, 255, 255, 100]
                         )

        self.gui = gui
        self.cg = gui.cg

        self.setBackground(peng3d.gui.button.FramedImageBackground(
            self,
            bg_idle=self.peng.resourceMgr.getTex("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(1, 1),
            tex_size=self.peng.resourceMgr.getTexSize("cg:img.bg.bg_brown", "gui")
            )
        )
        self.bg.vlist_layer = -3

        self.s_titlescreen = TitleScreenSubMenu("titlescreen", self, self.window, self.peng)
        self.addSubMenu(self.s_titlescreen)

        self.s_serverselect = ServerSelectSubMenu("serverselect", self, self.window, self.peng)
        self.addSubMenu(self.s_serverselect)

        self.changeSubMenu("titlescreen")


class TitleScreenSubMenu(peng3d.gui.SubMenu):
    menu: ServerSelectMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        # Background
        self.setBackground(peng3d.gui.FramedImageBackground(
            self,
            bg_idle=self.peng.resourceMgr.getTex("cg:img.bg.bg", "bg"),
            frame=[[0, 1, 0], [0, 1, 0]],
            scale=(.3, .3),
            repeat_edge=True, repeat_center=True,
            tex_size=self.peng.resourceMgr.getTexSize("cg:img.bg.bg", "bg")
            )
        )
        self.bg.vlist_layer = -2

        # Left sidebar (background)
        self.sidebar = peng3d.gui.Widget(
            "sidebar", self, self.window, self.peng,
            pos=(0, 0),
            size=(lambda sw, sh: (sw/3, sh)),
        )
        self.sidebar.setBackground(peng3d.gui.FramedImageBackground(
            self.sidebar,
            bg_idle=self.peng.resourceMgr.getTex("cg:img.bg.sidebar", "gui"),
            frame=[[1, 1, 10], [0, 1, 0]],
            scale=(1, 0),
            tex_size=self.peng.resourceMgr.getTexSize("cg:img.bg.sidebar", "gui")
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
            bg_idle=self.peng.resourceMgr.getTex("cg:img.bg.bg_trans", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(1, 1),
            tex_size=self.peng.resourceMgr.getTexSize("cg:img.bg.bg_trans", "gui")
            )
        )
        self.addWidget(self.screen_edge)

        # Play Button
        # This button switches to the serverselect submenu
        self.playbtn = peng3d.gui.FramedImageButton(
            "playbtn", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw/6-bw/2, sh/2 + 15)),
            size=(lambda sw, sh: (sw*0.3, sh*0.1)),
            label=self.peng.tl("cg:gui.menu.serverselect.title.playbtn.label"),
            bg_idle=self.peng.resourceMgr.getTex("cg:img.btn.btn_idle", "gui"),
            bg_hover=self.peng.resourceMgr.getTex("cg:img.btn.btn_hov", "gui"),
            bg_pressed=self.peng.resourceMgr.getTex("cg:img.btn.btn_press", "gui"),
            frame=[[1, 2, 1], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
            tex_size=self.peng.resourceMgr.getTexSize("cg:img.btn.btn_idle", "gui")
        )
        self.addWidget(self.playbtn)

        def f():
            self.menu.changeSubMenu("serverselect")
            self.menu.s_serverselect.reload_server_list()
        self.playbtn.addAction("click", f)

        # Settings Button
        # This button switches to the settings submenu
        self.settingsbtn = peng3d.gui.FramedImageButton(
            "settingsbtn", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw/6 - bw/2, sh/2 - bh - 5)),
            size=(lambda sw, sh: (sw * 0.3, sh * 0.1)),
            label=self.peng.tl("cg:gui.menu.serverselect.title.settingsbtn.label"),
            bg_idle=self.peng.resourceMgr.getTex("cg:img.btn.btn_idle", "gui"),
            bg_hover=self.peng.resourceMgr.getTex("cg:img.btn.btn_hov", "gui"),
            bg_pressed=self.peng.resourceMgr.getTex("cg:img.btn.btn_press", "gui"),
            frame=[[1, 2, 1], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
            tex_size=self.peng.resourceMgr.getTexSize("cg:img.btn.btn_idle", "gui")
        )
        self.addWidget(self.settingsbtn)

        def f():
            self.peng.cg.error("1; 2; Du bist dran!")
        self.settingsbtn.addAction("click", f)


class ServerSelectSubMenu(peng3d.gui.SubMenu):
    menu: ServerSelectMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.register_event_handlers()

        self.setBackground(None)

        # Address Field
        default_addr = self.peng.cg.client.default_server
        self.addr = peng3d.gui.TextInput(
            "addr", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw/2-bw/2, sh/2+bh/2)),
            size=(lambda sw, sh: (sw/2, 32)),
            text=default_addr,
            borderstyle="oldshadow",
            font_size=20,
        )
        self.addr.setBackground(cgclient.gui.custombuttons.RepeatTextBackground(
            self.addr,
            bg_idle=self.peng.resourceMgr.getTex("cg:img.btn.fld_idle", "gui"),
            bg_hover=self.peng.resourceMgr.getTex("cg:img.btn.fld_hov", "gui"),
            bg_pressed=self.peng.resourceMgr.getTex("cg:img.btn.fld_press", "gui"),
            frame=[150, 700, 150],
            border=[6, 0]
            )
        )
        self.addWidget(self.addr)

        # OK Button
        self.okbtn = peng3d.gui.FramedImageButton(
            "okbtn", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw/2-bw/2, sh/2-bh-5)),
            size=(lambda sw, sh: (sw * 0.5, sh * 0.1)),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.okbtn.label"),
            bg_idle=self.peng.resourceMgr.getTex("cg:img.btn.btn_idle", "gui"),
            bg_hover=self.peng.resourceMgr.getTex("cg:img.btn.btn_hov", "gui"),
            bg_pressed=self.peng.resourceMgr.getTex("cg:img.btn.btn_press", "gui"),
            frame=[[1, 2, 1], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
            tex_size=self.peng.resourceMgr.getTexSize("cg:img.btn.btn_idle", "gui")
        )
        self.addWidget(self.okbtn)

        def f():
            self.peng.cg.client.connect_to(self.addr.text)
            self.window.changeMenu("servermain")
            self.window.menus["servermain"].changeSubMenu("load")
            self.window.menus["servermain"].d_load.label_main = self.peng.tl("cg:gui.menu.smain.load.connect")
        self.okbtn.addAction("click", f)

    def reload_server_list(self):
        pass

    # Event Handlers
    def register_event_handlers(self):
        pass
