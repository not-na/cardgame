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
from typing import List, Mapping, Optional

import peng3d
from . import card
from pyglet.gl import *

import cgclient.gui
import pyglet


FLIGHT_MODE = True


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

        self.popup_layer: PopupLayer = PopupLayer("popup", self, self.window, self.peng)
        self.addLayer(self.popup_layer)

        self.gui_layer: GUILayer = GUILayer("game_gui", self, self.window, self.peng)
        self.addLayer(self.gui_layer)


class BackgroundLayer(peng3d.layer.Layer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: add skybox here


class GameLayer(peng3d.layer.Layer):
    peng: peng3d.Peng

    batch: pyglet.graphics.Batch

    CARD_KEYS = "0123456789abcdef"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pos = [0, 3, 0]
        self.rot = [0, -90]

        self.game: Optional[cgclient.game.CGame] = None

        self.hand_to_player: Mapping[int, str] = {}

        self.batch = pyglet.graphics.Batch()

        texinfo = self.peng.resourceMgr.getTex("cg:img.bg.test_table", "bg")
        self.vlist_table = self.batch.add(4, GL_QUADS, pyglet.graphics.TextureGroup(
            peng3d.gui.button._FakeTexture(*texinfo),
            parent=pyglet.graphics.OrderedGroup(0)),
                                          ("v3f",
                                           [
                                               -2, 0, 2,
                                               2, 0, 2,
                                               2, 0, -2,
                                               -2, 0, -2,
                                           ]),
                                          ("t3f", texinfo[2]),
                                          )

        # Developer Flight Mode
        if FLIGHT_MODE:
            self.move = [0, 0]
            self.jump = 0
            self.flight_enabled = False

            self.peng.keybinds.add("w", "cg:move.forward", self.on_fwd_down, False)
            self.peng.keybinds.add("s", "cg:move.backward", self.on_bwd_down, False)
            self.peng.keybinds.add("a", "cg:move.left", self.on_left_down, False)
            self.peng.keybinds.add("d", "cg:move.right", self.on_right_down, False)
            self.peng.keybinds.add("lshift", "cg:crouch", self.on_crouch_down, False)
            self.peng.keybinds.add("space", "cg:jump", self.on_jump_down, False)
            self.peng.keybinds.add("escape", "cg:escape", self.on_escape, False)
            self.peng.registerEventHandler("on_mouse_motion", self.on_mouse_motion)
            self.peng.registerEventHandler("on_mouse_drag", self.on_mouse_drag)

        self.peng.registerEventHandler("on_key_release", self.on_key_release)

        # TODO: possibly increase the animation frequency for high refreshrate monitors
        pyglet.clock.schedule_interval(self.update, 1/60.)

    def get_card_slot_pos(self, slot: str, index: int, count: int = 1):
        # First, map virtual slots to physical slots
        if slot.startswith("hand"):
            slot = f"player_{self.hand_to_player[int(slot[4])]}"
        elif slot.startswith("tricks"):
            slot = f"ptrick_{self.hand_to_player[int(slot[6])]}"

        # TODO: fix the card positions
        # Currently, _self is the middle stack of the group of three
        # A bit misleading, but it is only temporary

        if slot == "stack":
            return [(index-count/2)*0.1, 0.01*index+0.2, 0.1]
        elif slot == "table":
            return [.5, index*0.05, 0]
        elif slot == "poverty":
            return [-.5, index*0.05, 0]
        elif slot == "player_self":
            return [-2+0.1*index, 0.1+0.001*index, 0]
        elif slot == "player_left":
            return [-2+0.1*index, 0.1+0.001*index, -2]
        elif slot == "player_right":
            return [-2+0.1*index, 0.1+0.001*index, 2]
        elif slot == "player_top":
            return [2+0.1*index, 0.1+0.001*index, 0]
        elif slot == "ptrick_self":
            return [-1+0.1*index, 0.1+0.001*index, 0]
        elif slot == "ptrick_left":
            return [-1+0.1*index, 0.1+0.001*index, -1]
        elif slot == "ptrick_right":
            return [-1+0.1*index, 0.1+0.001*index, 1]
        elif slot == "ptrick_top":
            return [1+0.1*index, 0.1+0.001*index, 0]

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
        if FLIGHT_MODE and self.window.menu is self.menu and self.flight_enabled:
            speed = 5
            d = dt * speed  # distance covered this tick.
            dx, dy, dz = self.get_motion_vector()
            # New position in space, before accounting for gravity.
            dx, dy, dz = dx * d, dy * d, dz * d
            dy += self.jump*0.2
            x, y, z = self.pos
            self.pos = dx + x, dy + y, dz + z

    def get_motion_vector(self):
        if any(self.move):
            x, y = self.rot
            strafe = math.degrees(math.atan2(*self.move))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            dy = 0.0
            dx = math.cos(x_angle)
            dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return dx, dy, dz

    def on_fwd_down(self, symbol, modifiers, release):
        self.move[0] -= 1 if not release else -1

    def on_bwd_down(self, symbol, modifiers, release):
        self.move[0] += 1 if not release else -1

    def on_left_down(self, symbol, modifiers, release):
        self.move[1] -= 1 if not release else -1

    def on_right_down(self, symbol, modifiers, release):
        self.move[1] += 1 if not release else -1

    def on_crouch_down(self, symbol, modifiers, release):
        self.jump -= 1 if not release else -1

    def on_jump_down(self, symbol, modifiers, release):
        self.jump += 1 if not release else -1

    def on_escape(self, symbol, modifiers, release):
        if release:
            return
        self.window.toggle_exclusivity()
        self.flight_enabled = self.window.exclusive

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_motion(self, x, y, dx, dy):
        if FLIGHT_MODE and self.window.menu is self.menu and self.flight_enabled:
            m = 0.15
            x, y = self.rot
            x, y = x + dx*m, y + dy*m
            y = max(-90, min(90, y))
            x %= 360
            self.rot = x, y

    def on_key_release(self, symbol, modifiers):
        if not self.menu == self.window.menu:
            # Only active when the parent menu is active
            return

        if symbol < 0x7A and chr(symbol) in self.CARD_KEYS:
            # "Play" the card
            idx = self.CARD_KEYS.index(chr(symbol))
            self.menu.cg.info(f"Playing card #{idx}")
            if idx < len(self.game.slots[self.game.own_hand]):
                self.game.select_card(self.game.slots[self.game.own_hand][idx].cardid)

    def on_redraw(self):
        for card in self.game.cards.values():
            card.draw()

    def clean_up(self):
        # Delete all cards and reset to beginning
        for c in self.game.cards.values():
            c.delete()

    def reinit(self):
        self.game = self.menu.cg.client.game


class HUDLayer(peng3d.gui.GUILayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = "Times New Roman"
        self.font_size = 25
        self.font_color = [255, 255, 255, 100]

        self.setBackground([255, 0, 255, 0])

        self.s_main = MainHUDSubMenu("main", self, self.window, self.peng)
        self.addSubMenu(self.s_main)

        self.changeSubMenu("main")


class MainHUDSubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)


class PopupLayer(peng3d.gui.GUILayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = "Times New Roman"
        self.font_size = 25
        self.font_color = [255, 255, 255, 100]

        self.cg = self.menu.cg

        self.setBackground([0, 255, 0, 0])

        self.s_empty = peng3d.gui.SubMenu("empty", self, self.window, self.peng)
        self.addSubMenu(self.s_empty)

        self.s_question = QuestionPopupSubMenu("question", self, self.window, self.peng)
        self.addSubMenu(self.s_question)

        self.changeSubMenu("empty")

    def ask_question_2choice(self, questiontype):
        self.s_question.questiontype = questiontype

        self.s_question.question.label = self.peng.tl(f"cg:question.{questiontype}.text")
        self.s_question.choice1btn.label = self.peng.tl(f"cg:question.{questiontype}.choice1")
        self.s_question.choice2btn.label = self.peng.tl(f"cg:question.{questiontype}.choice2")

        self.changeSubMenu("question")


class QuestionPopupSubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.setBackground([242, 241, 240, 200])

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [6, 6], [20, 20])

        self.qcell = self.grid.get_cell([2, 4], [2, 1], anchor_x="center", anchor_y="center")
        self.question = peng3d.gui.Label("question", self, self.window, self.peng,
                                         pos=self.qcell,
                                         size=(lambda sw, sh: (self.qcell.size[0], 0)),
                                         label=self.peng.tl("cg:question.unknown.text"),
                                         font_color=[0, 0, 0, 255],
                                         multiline=True,
                                         )
        self.addWidget(self.question)

        self.choice1btn = cgclient.gui.CGButton("choice1btn", self, self.window, self.peng,
                                                pos=self.grid.get_cell([2, 2], [1, 1]),
                                                label=self.peng.tl("cg:question.unknown.choice1"),
                                                )
        self.addWidget(self.choice1btn)

        self.choice1btn.addAction("click", self.on_click_choice1)

        self.choice2btn = cgclient.gui.CGButton("choice2btn", self, self.window, self.peng,
                                                pos=self.grid.get_cell([3, 2], [1, 1]),
                                                label=self.peng.tl("cg:question.unknown.choice2"),
                                                )
        self.addWidget(self.choice2btn)

        self.choice2btn.addAction("click", self.on_click_choice2)

        self.questiontype = "unknown"

        self.choice1 = {
            "reservation": "reservation_yes",
            "throw": "throw_yes",
            "pigs": "pigs_yes",
            "superpigs": "superpigs_yes",
            "poverty": "poverty_yes",
            "poverty_accept": "poverty_accept",
            "wedding": "wedding_yes",
        }

        self.choice2 = {
            "reservation": "reservation_no",
            "throw": "throw_no",
            "pigs": "pigs_no",
            "superpigs": "superpigs_no",
            "poverty": "poverty_no",
            "poverty_accept": "poverty_decline",
            "wedding": "wedding_no"
        }

    def on_click_choice1(self):
        self.menu.cg.info(f"User clicked on choice 1 of question {self.questiontype}")

        t = self.choice1[self.questiontype]
        self.menu.cg.client.send_message("cg:game.dk.announce", {"type": t})

        self.menu.changeSubMenu("empty")

    def on_click_choice2(self):
        self.menu.cg.info(f"User clicked on choice 2 of question {self.questiontype}")

        t = self.choice2[self.questiontype]
        self.menu.cg.client.send_message("cg:game.dk.announce", {"type": t})

        self.menu.changeSubMenu("empty")


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

        self.changeSubMenu("ingame")


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
