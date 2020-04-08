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
        super().__init__(name, window, peng)

        self.gui = gui
        self.cg = gui.cg

        self.s_titlescreen = TitleScreenSubMenu("titlescreen", self, self.window, self.peng)
        self.addSubMenu(self.s_titlescreen)

        self.s_serverselect = ServerSelectSubMenu("serverselect", self, self.window, self.peng)
        self.addSubMenu(self.s_serverselect)

        self.changeSubMenu("titlescreen")


class TitleScreenSubMenu(peng3d.gui.SubMenu):
    menu: ServerSelectMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.setBackground([242, 241, 240])

        # Play Button
        # This button switches to the serverselect submenu
        self.playbtn = peng3d.gui.Button(
            "playbtn", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw/2-bw/2, sh/2+5)),
            size=(lambda sw, sh: (sw*0.3, sh*0.2)),
            label=self.peng.tl("cg:gui.menu.serverselect.title.playbtn.label"),
            borderstyle="oldshadow",
        )
        self.addWidget(self.playbtn)

        def f():
            self.menu.changeSubMenu("serverselect")
            self.menu.s_serverselect.reload_server_list()
        self.playbtn.addAction("click", f)

        # Settings Button
        # This button switches to the settings submenu
        self.settingsbtn = peng3d.gui.Button(
            "settingsbtn", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw/2-bw/2, sh/2-bh-5)),
            size=(lambda sw, sh: (sw*0.3, sh*0.1)),
            label=self.peng.tl("cg:gui.menu.serverselect.title.settingsbtn.label"),
            borderstyle="oldshadow",
        )
        self.addWidget(self.settingsbtn)

        def f():
            self.peng.cg.error("Settings not yet implemented!")
        self.settingsbtn.addAction("click", f)


class ServerSelectSubMenu(peng3d.gui.SubMenu):
    menu: ServerSelectMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.register_event_handlers()

        self.setBackground([242, 241, 240])

        # Address Field
        default_addr = self.peng.cg.client.default_server
        self.addr = peng3d.gui.TextInput(
            "addr", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw/2-bw/2, sh/2+bh/2+5)),
            size=(lambda sw, sh: (sw/2, 32)),
            text=default_addr,
            borderstyle="oldshadow",
            font_size=16,
        )
        self.addWidget(self.addr)

        # OK Button
        self.okbtn = peng3d.gui.Button(
            "okbtn", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw/2-bw/2, sh/2-bh/2-5)),
            size=(lambda sw, sh: (sw/2, 32)),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.okbtn.label"),
            borderstyle="oldshadow",
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

