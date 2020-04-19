#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ingame.py
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


class IngameMenu(peng3d.gui.Menu):
    def __init__(self, name, window, peng, gui):
        super().__init__(name, window, peng)

        self.gui = gui
        self.cg = gui.cg

        self.bg_layer = BackgroundLayer(self, self.window, self.peng)
        self.addLayer(self.bg_layer)

        self.game_layer = GameLayer(self, self.window, self.peng)
        self.addLayer(self.game_layer)

        self.hud_layer = HUDLayer("hud", self, self.window, self.peng)
        self.addLayer(self.hud_layer)

        self.gui_layer = GUILayer("game_gui", self, self.window, self.peng)
        self.addLayer(self.gui_layer)


class BackgroundLayer(peng3d.layer.Layer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GameLayer(peng3d.layer.Layer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HUDLayer(peng3d.gui.GUILayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = "Times New Roman",
        self.font_size = 25,
        self.font_color = [255, 255, 255, 100]

        self.setBackground([255, 0, 255, 0])

        self.s_main = MainHUDSubMenu("main", self, self.window, self.peng)
        self.addSubMenu(self.s_main)


class MainHUDSubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)


class GUILayer(peng3d.gui.GUILayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = "Times New Roman",
        self.font_size = 25,
        self.font_color = [255, 255, 255, 100]

        self.setBackground([255, 0, 255, 0])

        self.s_ingame = IngameGUISubMenu("ingame", self, self.window, self.peng)
        self.addSubMenu(self.s_ingame)

        self.s_load = LoadingScreenGUISubMenu("loadingscreen", self, self.window, self.peng)
        self.addSubMenu(self.s_load)

        self.s_pause = PauseGUISubMenu("pause", self, self.window, self.peng)
        self.addSubMenu(self.s_pause)

        self.changeSubMenu("loadingscreen")


class LoadingScreenGUISubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.setBackground([242, 241, 240])


class IngameGUISubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)


class PauseGUISubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)
