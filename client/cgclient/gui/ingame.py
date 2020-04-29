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
import ctypes
import math
import time
import uuid
from typing import List, Mapping, Optional, Tuple, Dict

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
    batch_pick: pyglet.graphics.Batch

    CARD_KEYS = "0123456789abcdef"
    NUM_SYNCS = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pos = [0, 3, 0]
        self.rot = [0, -90]

        self.game: Optional[cgclient.game.CGame] = None

        self.hand_to_player: Dict[int, str] = {}

        self.player_list: List[uuid.UUID] = []

        self.clicked_card: Optional[card.Card] = None

        self.color_db: Dict[int, Optional[uuid.UUID]] = {
            0: None,
        }
        self.mouse_moved = True
        self.mouse_pos = 0, 0
        self.mouse_color = 255, 0, 255

        self.batch = pyglet.graphics.Batch()
        self.batch_pick = pyglet.graphics.Batch()

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

        # Initialize the PBO for colorID
        pbo_ids = (GLuint*self.NUM_SYNCS)()
        glGenBuffers(self.NUM_SYNCS, pbo_ids)
        self.pbos = list(pbo_ids)
        self.cur_pbo = 0
        self.pbo_wait = False

        for n in range(self.NUM_SYNCS):
            glBindBuffer(GL_PIXEL_PACK_BUFFER, self.pbos[n])
            glBufferData(GL_PIXEL_PACK_BUFFER, 4, 0, GL_STREAM_READ)

        glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

        self.pbo_syncs = [None for i in range(self.NUM_SYNCS)]

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
            self.peng.registerEventHandler("on_mouse_press", self.on_mouse_press)
            self.peng.registerEventHandler("on_mouse_release", self.on_mouse_release)

        self.peng.registerEventHandler("on_key_release", self.on_key_release)

        # TODO: possibly increase the animation frequency for high refreshrate monitors
        pyglet.clock.schedule_interval(self.update, 1/60.)

    def get_card_slot_pos_rot(self, slot: str, index: int, count: int = 1):
        # First, map virtual slots to physical slots
        if slot.startswith("hand"):
            slot = f"player_{self.hand_to_player[int(slot[4])]}"
        elif slot.startswith("tricks"):
            slot = f"ptrick_{self.hand_to_player[int(slot[6])]}"

        # TODO: fix the card positions
        # Currently, _self is the middle stack of the group of three
        # A bit misleading, but it is only temporary

        if slot == "stack":
            return [(index-count/2)*0.1, 0.01*index+0.2, 0.1], 0
        elif slot == "table":
            return [.5, 0.1+0.001*index, 0.1*index], 0
        elif slot == "poverty":
            return [-.5, index*0.05, 0], 0
        elif slot == "player_self":
            return [-2+0.1*index, 0.1+0.001*index, 0], 0
        elif slot == "player_left":
            return [-2+0.1*index, 0.1+0.001*index, -2], 0
        elif slot == "player_right":
            return [-2+0.1*index, 0.1+0.001*index, 2], 0
        elif slot == "player_top":
            return [2.5-0.1*index, 0.1+0.001*index, 0], 0
        elif slot == "ptrick_self":
            return [-2.5-0.1*index, 0.5+0.001*index, 0], 0
        elif slot == "ptrick_left":
            return [-2.5-0.1*index, 0.5+0.001*index, -1], 0
        elif slot == "ptrick_right":
            return [-2.5-0.1*index, 0.5+0.001*index, 1], 0
        elif slot == "ptrick_top":
            return [2.5+0.1*index, 0.5+0.001*index, 0], 0
        else:
            self.menu.cg.crash(f"Unknown card slot {slot}")

    def get_backname(self):
        return "cg:card.back_1"

    def gen_color_id(self, co: card.Card) -> Tuple:
        for n in range(0, 255):
            if n not in self.color_db:
                break
        else:
            self.menu.cg.crash(f"Could not generate a new ColorID for card {co.value} ({co.cardid})")
            return 255, 0, 0

        self.color_db[n] = co.cardid

        return 0, n, 0

    def draw(self):
        # Customized variant of PengWindow.set3d()
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

        if self.mouse_moved:
            t = time.time()
            # Draw the ColorID pass
            # Used to determine which card we are hovering over
            # Based roughly on https://stackoverflow.com/a/4059685
            # PBO based on
            glEnable(GL_SCISSOR_TEST)
            glScissor(*self.mouse_pos, 1, 1)  # Restrict to 1x1 px around the mouse cursor

            # Draw the colorID batch
            self.batch_pick.draw()

            t2 = time.time()

            glBindBuffer(GL_PIXEL_PACK_BUFFER, self.pbos[self.cur_pbo])
            # Read the pixel at the mouse
            #buf = (GLubyte*4)()
            #buf_ptr = ctypes.cast(buf, ctypes.POINTER(GLubyte))

            glReadPixels(*self.mouse_pos, 1, 1, GL_BGRA, GL_UNSIGNED_BYTE, 0)

            glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

            if self.pbo_syncs[self.cur_pbo] is not None:
                glDeleteSync(self.pbo_syncs[self.cur_pbo])
            self.pbo_syncs[self.cur_pbo] = glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE, 0)

            self.cur_pbo = (self.cur_pbo+1) % self.NUM_SYNCS
            self.pbo_wait = True

            # Reset state
            glDisable(GL_SCISSOR_TEST)
            #self.window.clear()

            #et = time.time()

            #tdiff = et-t
            #self.menu.cg.info(f"T_total: {tdiff*1000:.4f}ms Tr: {(t2-t)*1000:.4f}ms Tg: {(et-t2)*1000:.4f}ms")

            self.mouse_moved = False

        t = time.time()
        # Draw the main batch
        # Contains the table and cards
        self.batch.draw()

        et = time.time()
        #self.menu.cg.info(f"T_r: {(et-t)*1000:.4f}ms")

    def get_card_at_mouse(self) -> Optional[uuid.UUID]:
        if self.mouse_color == (255, 0, 255):
            return None

        if self.mouse_color[1] in self.color_db:
            return self.color_db[self.mouse_color[1]]
        else:
            return None

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

        if self.pbo_wait:
            # a PBO with colorID data may be ready
            result = (GLint*1)()
            #r_pointer = ctypes.cast(result, ctypes.POINTER(GLint))
            length = (GLsizei*1)()
            #l_pointer = ctypes.cast(length, ctypes.POINTER(GLsizei))
            for n in range(self.NUM_SYNCS):
                if self.pbo_syncs[n] is None:
                    # PBO sync is not active, skip check
                    continue
                #t = time.time()
                # Check sync status
                glGetSynciv(self.pbo_syncs[n], GL_SYNC_STATUS, 1, length, result)
                if result[0] == GL_SIGNALED:
                    # Sync has been signaled, data is ready
                    buf = (GLubyte * 4)()
                    buf_ptr = ctypes.cast(buf, ctypes.POINTER(GLubyte))
                    glBindBuffer(GL_PIXEL_PACK_BUFFER, self.pbos[n])
                    glGetBufferSubData(GL_PIXEL_PACK_BUFFER, 0, 4, buf_ptr)

                    glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

                    # Re-arrange buffer data
                    b, g, r, a = buf
                    o = r, g, b

                    glDeleteSync(self.pbo_syncs[n])
                    self.pbo_syncs[n] = None

                    if o != self.mouse_color:
                        self.menu.cg.info(f"Mouse color changed from {self.mouse_color} to {o}")
                        pass
                        # TODO: implement hover
                    self.mouse_color = o

                    #et = time.time()
                    #self.menu.cg.info(f"T: {(et-t)*1000:.4f}ms for color {o}")

            if not any(map(lambda s: s is not None, self.pbo_syncs)):
                self.pbo_wait = False

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
        self.mouse_moved = True
        self.mouse_pos = x, y
        if FLIGHT_MODE and self.window.menu is self.menu and self.flight_enabled:
            m = 0.15
            x, y = self.rot
            x, y = x + dx*m, y + dy*m
            y = max(-90, min(90, y))
            x %= 360
            self.rot = x, y

        # TODO: add card dragging support here

    def on_mouse_press(self, x, y, button, modifiers):
        if self.window.menu is not self.menu:
            return
        c = self.get_card_at_mouse()
        if c is None:
            return

        co = self.game.cards[c]
        co.clicked = True
        self.clicked_card = co
        self.menu.cg.info(f"Pressed Card {co.value} ({co.cardid})")

        co.redraw()

    def on_mouse_release(self, x, y, button, modifiers):
        if self.menu is not self.window.menu:
            return
        c = self.get_card_at_mouse()
        if c is None:
            return

        co = self.game.cards[c]

        if co != self.clicked_card:
            return  # Not the clicked card, do nothing

        self.menu.cg.info(f"Released Card {co.value} ({co.cardid})")

        if not co.dragged:
            # Card has been selected
            self.game.select_card(c)
        else:
            # TODO: implement card dragging
            pass

        co.clicked = False
        co.dragged = False

        co.redraw()
        self.clicked_card = None

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

        self.color_db = {
            0: None,
        }

    def reinit(self):
        self.game = self.menu.cg.client.game


class HUDLayer(peng3d.gui.GUILayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = "Times New Roman"
        self.font_size = 25
        self.font_color = [100, 100, 100, 255]

        self.setBackground([255, 0, 255, 0])

        self.s_main = MainHUDSubMenu("main", self, self.window, self.peng)
        self.addSubMenu(self.s_main)

        self.changeSubMenu("main")


class MainHUDSubMenu(peng3d.gui.SubMenu):
    labels: Dict[str, peng3d.gui.Label]

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.labels = {}

        self.pself_label = peng3d.gui.Label("pself_label", self, self.window, self.peng,
                                            pos=(lambda sw, sh, bw, bh: (0, 20)),
                                            size=(lambda sw, sh: (sw, 0)),
                                            label="PSELF",
                                            anchor_x="center",
                                            anchor_y="baseline",
                                            multiline=False,
                                            font_size=35,
                                            )
        self.addWidget(self.pself_label)
        self.labels["self"] = self.pself_label

        self.pleft_label = peng3d.gui.Label("pleft_label", self, self.window, self.peng,
                                            pos=(lambda sw, sh, bw, bh: (0, sh/2)),
                                            size=(lambda sw, sh: (0, 0)),
                                            label="PLEFT",
                                            anchor_x="left",
                                            anchor_y="baseline",
                                            multiline=False,
                                            font_size=35,
                                            )
        self.addWidget(self.pleft_label)
        self.labels["left"] = self.pleft_label

        self.pright_label = peng3d.gui.Label("pright_label", self, self.window, self.peng,
                                             pos=(lambda sw, sh, bw, bh: (sw-self.pright_label._label.content_width-20, sh/2)),
                                             size=(lambda sw, sh: (0, 0)),
                                             label="PRIGHT",
                                             anchor_x="left",
                                             anchor_y="baseline",
                                             #align="right",
                                             multiline=False,
                                             font_size=35,
                                             )
        self.addWidget(self.pright_label)
        self.labels["right"] = self.pright_label

        self.ptop_label = peng3d.gui.Label("ptop_label", self, self.window, self.peng,
                                           pos=(lambda sw, sh, bw, bh: (0, sh-60)),
                                           size=(lambda sw, sh: (sw, 0)),
                                           label="PTOP",
                                           anchor_x="center",
                                           anchor_y="baseline",
                                           multiline=False,
                                           font_size=35,
                                           )
        self.addWidget(self.ptop_label)
        self.labels["top"] = self.ptop_label


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

        self.s_returnt = ReturnTrumpsSubMenu("returnt", self, self.window, self.peng)
        self.addSubMenu(self.s_returnt)

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


class ReturnTrumpsSubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.setBackground([242, 241, 240, 200])

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [6, 6], [20, 20])

        self.qcell = self.grid.get_cell([2, 4], [2, 1], anchor_x="center", anchor_y="center")
        self.question = peng3d.gui.Label("question", self, self.window, self.peng,
                                         pos=self.qcell,
                                         size=(lambda sw, sh: (self.qcell.size[0], 0)),
                                         label=self.peng.tl("cg:question.poverty_return_trumps.text"),
                                         font_color=[0, 0, 0, 255],
                                         multiline=True,
                                         )
        self.addWidget(self.question)

        self.choice1btn = cgclient.gui.CGButton("choice1btn", self, self.window, self.peng,
                                                pos=self.grid.get_cell([2, 2], [1, 1]),
                                                label=self.peng.tl("cg:question.poverty_return_trumps.choice1"),
                                                )
        self.addWidget(self.choice1btn)

        self.choice1btn.addAction("click", self.on_click, 0)

        self.choice2btn = cgclient.gui.CGButton("choice2btn", self, self.window, self.peng,
                                                pos=self.grid.get_cell([3, 2], [1, 1]),
                                                label=self.peng.tl("cg:question.poverty_return_trumps.choice2"),
                                                )
        self.addWidget(self.choice2btn)

        self.choice2btn.addAction("click", self.on_click, 1)

        self.choice3btn = cgclient.gui.CGButton("choice3btn", self, self.window, self.peng,
                                                pos=self.grid.get_cell([2, 1], [1, 1]),
                                                label=self.peng.tl("cg:question.poverty_return_trumps.choice3"),
                                                )
        self.addWidget(self.choice3btn)

        self.choice3btn.addAction("click", self.on_click, 2)

        self.choice4btn = cgclient.gui.CGButton("choice4btn", self, self.window, self.peng,
                                                pos=self.grid.get_cell([3, 1], [1, 1]),
                                                label=self.peng.tl("cg:question.poverty_return_trumps.choice4"),
                                                )
        self.addWidget(self.choice4btn)

        self.choice4btn.addAction("click", self.on_click, 3)

    def on_click(self, n):
        self.menu.cg.info(f"User clicked on choice {n} of question poverty_return_trumps")

        self.menu.cg.client.send_message("cg:game.dk.announce",
                                         {
                                             "type": "poverty_return",
                                             "data": {"amount": n},
                                         })

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
