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
import math
import uuid
from typing import List, Mapping

import peng3d
from . import card
from pyglet.gl import *

import cgclient.gui
import pyglet


class IngameMenu(peng3d.gui.Menu):
    def __init__(self, name, window, peng, gui):
        super().__init__(name, window, peng)

        self.gui = gui
        self.cg = gui.cg

        self.bg_layer: BackgroundLayer = BackgroundLayer(self, self.window, self.peng)
        self.addLayer(self.bg_layer)

        self.game_layer: GameLayer = GameLayer(self, self.window, self.peng)
        self.addLayer(self.game_layer)

        self.hud_layer: HUDLayer = HUDLayer("hud", self, self.window, self.peng)
        self.addLayer(self.hud_layer)

        self.gui_layer: GUILayer = GUILayer("game_gui", self, self.window, self.peng)
        self.addLayer(self.gui_layer)


class BackgroundLayer(peng3d.layer.Layer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GameLayer(peng3d.layer.Layer):
    SLOT_NAMES: List[str] = [
        "stack",
        "poverty",
        "table",
        "hand0",
        "hand1",
        "hand2",
        "hand3",
        "tricks0",
        "tricks1",
        "tricks2",
        "tricks3",
    ]
    peng: peng3d.Peng

    batch: pyglet.graphics.Batch

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.slots: Mapping[str, card.Card] = {name: [] for name in self.SLOT_NAMES}
        self.cards: Mapping[uuid.UUID, card.Card] = {}

        self.player_order: List[uuid.UUID] = []
        self.hand_to_player: Mapping[int, str] = {}

        self.pos = [0, 2, 0]
        self.rot = [0, -90]

        self.batch = pyglet.graphics.Batch()

        texinfo = self.peng.resourceMgr.getTex("cg:img.bg.test_table", "bg")
        self.vlist_table = self.batch.add(4, GL_QUADS, pyglet.graphics.TextureGroup(
            peng3d.gui.button._FakeTexture(*texinfo),
            parent=pyglet.graphics.OrderedGroup(0)),
                                          ("v3f",
                                           [
                                               -2, 0, 2, 2, 0, -2, 2, 0, 2, -2, 0, 2,
                                           ]),
                                          ("t3f", texinfo[2]),
                                          )

        # TODO: possibly increase the animation frequency for high refreshrate monitors
        pyglet.clock.schedule_interval(self.update, 1/60.)

    def get_card_slot_pos(self, slot: str, index: int, count: int = 1):
        # First, map virtual slots to physical slots
        if slot.startswith("hand"):
            slot = f"player_{self.hand_to_player[int(slot[4])]}"
        elif slot.startswith("tricks"):
            slot = f"ptrick_{self.hand_to_player[int(slot[6])]}"

        if slot == "stack":
            return [0, 0, 0]
        elif slot == "table":
            return [.5, index*0.05, 0]
        elif slot == "poverty":
            return [-.5, index*0.05, 0]
        elif slot == "player_self":
            pass
        elif slot == "player_left":
            pass
        elif slot == "player_right":
            pass
        elif slot == "player_top":
            pass
        elif slot == "ptrick_self":
            pass
        elif slot == "ptrick_left":
            pass
        elif slot == "ptrick_right":
            pass
        elif slot == "ptrick_top":
            pass

    def get_backname(self):
        return "cg:card.back_1"

    def draw(self):
        width, height = self.window.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.window.cfg["graphics.fieldofview"], width / float(height), self.window.cfg["graphics.nearclip"],
                       self.window.cfg["graphics.farclip"])  # default 60
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rot
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.pos
        glTranslatef(-x, -y, -z)

        # Draw the main batch
        # Contains the table and cards
        self.batch.draw()

    def update(self, dt=None):
        pass

    def on_redraw(self):
        for card in self.cards.values():
            card.draw()

    def reinit(self):
        # Delete all cards and reset to beginning

        for c in self.cards.values():
            c.delete()
        self.cards = {}
        self.slots = {name: [] for name in self.SLOT_NAMES}


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
