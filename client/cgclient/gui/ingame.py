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

FLIGHT_MODE = False


class IngameMenu(peng3d.gui.Menu):
    def __init__(self, name, window, peng, gui):
        super().__init__(name, window, peng)

        self.gui = gui
        self.cg = gui.cg

        self.register_event_handlers()

        self.bg_layer: BackgroundLayer = BackgroundLayer("background", self, self.window, self.peng)
        self.addLayer(self.bg_layer)

        self.game_layer: GameLayer = GameLayer(self, self.window, self.peng)
        self.addLayer(self.game_layer)

        self.hud_layer: HUDLayer = HUDLayer("hud", self, self.window, self.peng)
        self.addLayer(self.hud_layer)

        self.popup_layer: PopupLayer = PopupLayer("popup", self, self.window, self.peng)
        self.addLayer(self.popup_layer)

        self.gui_layer: GUILayer = GUILayer("game_gui", self, self.window, self.peng)
        self.addLayer(self.gui_layer)

        self.status_layer: StatusLayer = StatusLayer("status_msg", self, self.window, self.peng)
        self.addLayer(self.status_layer)

        self.d_status_message = self.status_layer.d_status_message

    def register_event_handlers(self):
        self.cg.add_event_listener("cg:status.message.open", self.handler_status_message_open)
        self.cg.add_event_listener("cg:status.message.close", self.handler_status_message_close)

    def handler_status_message_open(self, event: str, data: dict):
        self.status_layer.changeSubMenu("status_msg")
        self.d_status_message.label_main = self.peng.tl(data["message"], data["data"])

    def handler_status_message_close(self, event: str, data: dict):
        self.status_layer.changeSubMenu("empty")


class BackgroundLayer(peng3d.gui.GUILayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setBackground(peng3d.gui.FramedImageBackground(
            peng3d.gui.FakeWidget(self),
            bg_idle=(self.peng.cg.get_config_option("cg:graphics.background"), "bg"),
            frame=[[0, 1, 0], [0, 1, 0]],
            scale=(0, 0),
            repeat_center=True
        ))

        # Empty submenu
        self.sm = peng3d.gui.SubMenu("sm", self, self.window, self.peng)
        self.addSubMenu(self.sm)
        self.changeSubMenu("sm")

    def on_resize(self, w, h):
        super().on_resize(w, h)
        if self.peng.cg.client.game is None:
            return
        # This must be done here for GameLayer has no on_resize method
        for i in ["hand1", "hand3", "tricks0", "tricks1", "tricks2", "tricks3"]:
            for c in self.peng.cg.client.game.slots[i]:
                if c.anim_state != cgclient.gui.card.ANIM_STATE_ACTIVE:
                    c.start_anim(i, i)


class GameLayer(peng3d.layer.Layer):
    peng: peng3d.Peng

    batch: pyglet.graphics.Batch
    batch_pick: pyglet.graphics.Batch

    NUM_SYNCS = 2
    MIN_COLORID = 1 / 30.

    DRAG_BASE_MULT = -0.565  # Multiplied by window height
    DRAG_MIN = 5  # Minimum drag distance before card becomes dragged / pulled-out

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

        # Initialize the PBO for colorID
        pbo_ids = (GLuint * self.NUM_SYNCS)()
        glGenBuffers(self.NUM_SYNCS, pbo_ids)
        self.pbos = list(pbo_ids)
        self.cur_pbo = 0
        self.pbo_wait = False

        for n in range(self.NUM_SYNCS):
            glBindBuffer(GL_PIXEL_PACK_BUFFER, self.pbos[n])
            glBufferData(GL_PIXEL_PACK_BUFFER, 4, 0, GL_STREAM_READ)

        glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

        self.pbo_syncs = [None for i in range(self.NUM_SYNCS)]
        self.last_colorid = 0

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
        self.peng.keybinds.add("f3", "cg:debug", self.on_debug, False)
        self.peng.registerEventHandler("on_mouse_motion", self.on_mouse_motion)
        self.peng.registerEventHandler("on_mouse_drag", self.on_mouse_drag)
        self.peng.registerEventHandler("on_mouse_press", self.on_mouse_press)
        self.peng.registerEventHandler("on_mouse_release", self.on_mouse_release)

        # TODO: possibly increase the animation frequency for high refreshrate monitors
        pyglet.clock.schedule_interval(self.update, 1 / 60.)

    def norm_card_slot(self, slot: str):
        # Normalize handN and tricksN slots to physical slots
        # Needed because the different hands can map to different players
        if slot.startswith("hand"):
            return f"player_{self.hand_to_player[int(slot[4])]}"
        elif slot.startswith("tricks"):
            return f"ptrick_{self.hand_to_player[int(slot[6])]}"
        else:
            # No modification necessary
            return slot

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
        for card in self.game.cards.values():
            card.draw()

        # Customized variant of PengWindow.set3d()
        width, height = self.window.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.window.cfg["graphics.fieldofview"], width / float(height),
                       self.window.cfg["graphics.nearclip"],
                       self.window.cfg["graphics.farclip"])  # default 60
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rot
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.pos
        glTranslatef(-x, -y, -z)

        if self.mouse_moved and time.time() - self.last_colorid > self.MIN_COLORID:
            self.last_colorid = time.time()

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
            # buf = (GLubyte*4)()
            # buf_ptr = ctypes.cast(buf, ctypes.POINTER(GLubyte))

            glReadPixels(*self.mouse_pos, 1, 1, GL_BGRA, GL_UNSIGNED_BYTE, 0)

            glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

            if self.pbo_syncs[self.cur_pbo] is not None:
                glDeleteSync(self.pbo_syncs[self.cur_pbo])
            self.pbo_syncs[self.cur_pbo] = glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE, 0)

            self.cur_pbo = (self.cur_pbo + 1) % self.NUM_SYNCS
            self.pbo_wait = True

            # Reset state
            glDisable(GL_SCISSOR_TEST)
            # self.window.clear()

            # et = time.time()

            # tdiff = et-t
            # self.menu.cg.info(f"T_total: {tdiff*1000:.4f}ms Tr: {(t2-t)*1000:.4f}ms Tg: {(et-t2)*1000:.4f}ms")

            self.mouse_moved = False

        t = time.time()
        # Draw the main batch
        # Contains the table and cards
        self.batch.draw()

        et = time.time()
        # self.menu.cg.info(f"T_r: {(et-t)*1000:.4f}ms")

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
            dy += self.jump * 0.2
            x, y, z = self.pos
            self.pos = dx + x, dy + y, dz + z

        if self.pbo_wait:
            # a PBO with colorID data may be ready
            result = (GLint * 1)()
            # r_pointer = ctypes.cast(result, ctypes.POINTER(GLint))
            length = (GLsizei * 1)()
            # l_pointer = ctypes.cast(length, ctypes.POINTER(GLsizei))
            for n in range(self.NUM_SYNCS):
                if self.pbo_syncs[n] is None:
                    # PBO sync is not active, skip check
                    continue
                # t = time.time()
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
                        # Remove hovered flag from old card
                        cid = self.get_card_at_mouse()
                        if cid is not None:
                            co = self.game.cards[cid]
                            co.hovered = False
                            co.start_anim(co.slot, co.slot, 0.2)

                        # Update mouse_color
                        self.mouse_color = o

                        if self.is_card_clickable() and self.clicked_card is None:
                            # Add hovered flag to new card
                            cid = self.get_card_at_mouse()
                            if cid is not None:
                                co = self.game.cards[cid]
                                if co.slot == self.game.own_hand:
                                    co.hovered = True
                                    co.start_anim(co.slot, co.slot, 0.2)

                    self.mouse_color = o

                    # et = time.time()
                    # self.menu.cg.info(f"T: {(et-t)*1000:.4f}ms for color {o}")

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

    def is_card_clickable(self):
        return (self.menu is self.window.menu
                and self.menu.popup_layer.activeSubMenu == "empty"
                and self.menu.gui_layer.activeSubMenu == "ingame"
                )

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
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            x %= 360
            self.rot = x, y

        if self.clicked_card is not None:
            # We are dragging a card, potentially update its position
            start_drag = False
            if not self.clicked_card.dragged and ((x-self.clicked_card.drag_start_pos[0])**2+(y-self.clicked_card.drag_start_pos[1])**2) >= self.DRAG_MIN**2:
                start_drag = True
                self.clicked_card.dragged = True
                self.clicked_card.start_anim(self.game.own_hand, self.game.own_hand)

            dx = x-self.window.width/2
            dy = y-self.window.height*self.DRAG_BASE_MULT
            angle = -math.degrees(math.atan2(dx, dy))

            n_cards = len(self.game.slots[self.game.own_hand])
            card_angle = cgclient.gui.card.CARD_ANGLE
            total_angle = n_cards*card_angle  # Total angle occupied by cards
            base_angle = 0

            # Original equation:
            # angle = base_angle + (index-count/2. + 0.5)*angle_per_card
            # angle = base_angle + ridx*angle_per_card
            # (angle-base_angle)/angle_per_card=ridx
            # We are basically trying to figure out index
            # ridx = index-count/2+0.5
            # index=ridx-count/2+0.5
            # This theoretical approach doesn't quite work, since the rendered perspective uses
            # a different coordinate system than the mouse coordinates
            # Results in base_angle=0 and flipped sign of angle
            r_idx = (angle-base_angle)/card_angle  # Raw index, term in parentheses
            nidx = int(r_idx+n_cards/2+0.5)  # Actual index

            # Normalize index
            idx = min(max(nidx, 0), n_cards-1)

            own_hand = self.game.slots[self.game.own_hand]
            cur_idx = own_hand.index(self.clicked_card)

            # self.menu.cg.info(f"{angle=:.03} {r_idx=:.03} {n_cards=} {nidx=} {idx=} {cur_idx=}")

            if idx != cur_idx:
                # Index changed, swap card position
                own_hand[cur_idx] = own_hand[idx]
                own_hand[idx] = self.clicked_card

                # Re-animate all cards in hand
                for c in self.game.slots[self.game.own_hand]:
                    if not start_drag or c != self.clicked_card:
                        c.start_anim(self.game.own_hand, self.game.own_hand, 0.1)

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.is_card_clickable():
            return
        c = self.get_card_at_mouse()
        if c is None:
            return

        co = self.game.cards[c]

        if co.slot != self.game.own_hand:
            return

        co.clicked = True
        co.start_anim(co.slot, co.slot)
        co.drag_start_pos = x, y
        self.clicked_card = co
        self.menu.cg.info(f"Pressed Card {co.value} ({co.cardid})")

        co.redraw()

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.is_card_clickable():
            return

        if self.clicked_card is None:
            return

        co = self.clicked_card
        self.menu.cg.info(f"Released Card {co.value} ({co.cardid})")
        if not co.dragged:
            # Card has been selected
            self.game.select_card(co.cardid)

        co.clicked = False
        co.dragged = False

        co.start_anim(co.slot, co.slot)
        self.clicked_card = None

    def on_redraw(self):
        pass

    def on_menu_enter(self,old):
        super().on_menu_enter(old)

        for suit in card.SUITES.values():
            for val in card.COUNTS.values():
                self.peng.resourceMgr.getTex(f"cg:card.{suit}_{val}", "card")

    def on_debug(self, symbol, modifiers, release):
        if release:
            return

        c = self.get_card_at_mouse()
        if c not in self.game.cards:
            self.menu.cg.warn(f"CARD {c} not in cards!")
            return
        co = self.game.cards[c]
        self.menu.cg.info(f"DEBUG: {co.value=} {co.slot=} {co.rot=} {co.texf[1]}/{co.texb[1]}")

    def clean_up(self):
        # Delete all cards and reset to beginning
        for c in self.game.cards.values():
            c.delete()
        self.game.cards = {}

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


class _BlendableDynImageGroup(pyglet.graphics.Group):
    def __init__(self,layer,parent=None):
        super().__init__(parent)
        self.layer = layer
    def set_state(self):
        tex_info = self.layer.imgs[self.layer.cur_img]
        glEnable(tex_info[0])
        glBindTexture(tex_info[0],tex_info[1])

        glEnable(GL_BLEND)
        glBlendFunc(GL_CONSTANT_ALPHA, GL_ONE_MINUS_CONSTANT_ALPHA)
        glBlendColor(1.0, 1.0, 1.0, self.layer.widget.perc_visible)
    def unset_state(self):
        tex_info = self.layer.imgs[self.layer.cur_img]
        glDisable(tex_info[0])

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


class BlendableFramedImageWidgetLayer(peng3d.gui.layered.FramedImageWidgetLayer):
    def initialize(self):
        self.cur_img = self.cur_img if self.cur_img is not None else (
            self.default_img if self.default_img is not None else list(self.imgs.keys())[0])

        if (self.frame_x[0] + self.frame_x[2]) * self.scale[0] > self.widget.size[0] or \
                (self.frame_y[0] + self.frame_y[2]) * self.scale[1] > self.widget.size[1]:
            raise ValueError(f"Scale {self.scale} is too large for this widget")

        self.bg_group = _BlendableDynImageGroup(self, self.group)
        self.vlist_corners = self.widget.submenu.batch2d.add(16, GL_QUADS, self.bg_group, "v2f", "t3f")
        self.vlist_edges = self.widget.submenu.batch2d.add(16, GL_QUADS, self.bg_group, "v2f", "t3f")
        self.vlist_center = self.widget.submenu.batch2d.add(4, GL_QUADS, self.bg_group, "v2f", "t3f")
        self.regVList(self.vlist_corners)
        self.regVList(self.vlist_edges)
        self.regVList(self.vlist_center)


class AnnounceWidget(peng3d.gui.LayeredWidget):
    ANIM_BASE = 10
    ANIM_EXP_SHIFT = -3.5

    def __init__(self, name, submenu, window, peng,
                 pos=None, size=None,
                 ):
        super().__init__(name, submenu, window, peng,
                         pos=pos, size=size,
                         )

        self.l_bg = BlendableFramedImageWidgetLayer(
            "bg", self, 1,
            border=(0,0),
            offset=(0,0),
            imgs={
                "idle": ("cg:img.btn.fld_idle", "gui"),
            },
            frame=[[1, 2, 1], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
            )
        self.addLayer(self.l_bg)
        self.l_bg.switchImage("idle")

        self.l_label = peng3d.gui.LabelWidgetLayer("label", self, 2,
                                                   border=(0,0),
                                                   offset=(0,0),
                                                   label=self.peng.tl("cg:announce.default"),
                                                   font_color=[255, 255, 255, 100]
                                                   )
        self.addLayer(self.l_label)

        # Invisible by default
        self.visible = False

        self.start_time: float = 0
        self.perc_visible = 1.0

        self.announce_queue = []

    def draw(self):
        super().draw()

        if not self.visible:
            return

        dt = time.time()-self.start_time

        self.perc_visible = min(-pow(self.ANIM_BASE, dt+self.ANIM_EXP_SHIFT)+1, 1.0)
        self.redraw()

        if self.perc_visible <= 0:
            self.visible = False
            self.perc_visible = 1.0

            if len(self.announce_queue) > 0:
                t, dat = self.announce_queue.pop(0)
                self.set_announce(t, dat)

    def set_announce(self, t: str, dat: Dict):
        if self.visible:
            # Announce already running, postpone it
            self.announce_queue.append([t, dat])
            return

        self.l_label.label = self.peng.tl(t, dat)

        self.start_time = time.time()
        self.visible = True

        self.redraw()

    def on_redraw(self):
        super().on_redraw()

        # Update alpha of font
        self.l_label._label.color[3] = int(self.perc_visible*100)


class MainHUDSubMenu(peng3d.gui.SubMenu):
    labels: Dict[str, peng3d.gui.Label]
    announces: Dict[str, AnnounceWidget]

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        # Player Icons
        def f(sw, sh, bw, bh):
            y_diff = x_diff = 0
            if "gui_layer" in self.menu.menu.__dict__:
                v = self.menu.menu.gui_layer.s_ingame.pigsbtn.visible
                y_diff = v * (self.menu.menu.gui_layer.s_ingame.pigsbtn.size[1] + 5)
                x_diff = v * 0.03
            return (sw + (0.489 + x_diff) * sh) / 2, 5 + y_diff

        # Profile Image
        self.self_img = PlayerIcon(
            "selfimg", self, self.window, self.peng,
            pos=f,
            size=(lambda sw, sh: (sh/8,)*2)
        )
        self.self_img.lbl._label.anchor_x = "left"
        self.self_img.lbl.offset = (lambda sx, sy, sw, sh: (sw/2 + 5, 0))
        self.addWidget(self.self_img)

        self.left_img = PlayerIcon(
            "leftimg", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (5, sh * 1/5 - (bh / 2))),
            size=(lambda sw, sh: (sh/8,)*2)
        )
        self.left_img.lbl._label.anchor_x = "left"
        self.left_img.lbl.offset = (lambda sx, sy, sw, sh: (sw / 2 + 5, 0))
        self.addWidget(self.left_img)

        self.top_img = PlayerIcon(
            "topimg", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: ((sw - 0.489 * sh) / 2 - bw, sh - bh - 5)),
            size=(lambda sw, sh: (sh/8,)*2)
        )
        self.top_img.lbl._label.anchor_x = "right"
        self.top_img.lbl.offset = (lambda sx, sy, sw, sh: (-sw / 2 - 5, 0))
        self.addWidget(self.top_img)

        self.right_img = PlayerIcon(
            "rightimg", self, self.window, self.peng,
            pos=(lambda sw, sh, bw, bh: (sw - bw - 5, sh * 4/5 - (bh / 2))),
            size=(lambda sw, sh: (sh/8,)*2)
        )
        self.right_img.lbl._label.anchor_x = "right"
        self.right_img.lbl.offset = (lambda sx, sy, sw, sh: (-sw / 2 - 5, 0))
        self.addWidget(self.right_img)

        # Announces
        self.announces = {}

        self.pself_announce = AnnounceWidget("pself_announce", self, self.window, self.peng,
                                             pos=(lambda sw, sh, bw, bh: (sw/2-bw/2, sh/32)),
                                             size=(lambda sw, sh: (sw/6, sh/16)),
                                             )
        self.addWidget(self.pself_announce)
        self.announces["self"] = self.pself_announce

        self.pleft_announce = AnnounceWidget("pleft_announce", self, self.window, self.peng,
                                             pos=(lambda sw, sh, bw, bh: (sw/32, sh/2-bh/2)),
                                             size=(lambda sw, sh: (sw/6, sh/16)),
                                             )
        self.addWidget(self.pleft_announce)
        self.announces["left"] = self.pleft_announce

        self.pright_announce = AnnounceWidget("pright_announce", self, self.window, self.peng,
                                              pos=(lambda sw, sh, bw, bh: (sw-bw-sw / 32, sh / 2 - bh / 2)),
                                              size=(lambda sw, sh: (sw / 6, sh / 16)),
                                              )
        self.addWidget(self.pright_announce)
        self.announces["right"] = self.pright_announce

        self.ptop_announce = AnnounceWidget("ptop_announce", self, self.window, self.peng,
                                            pos=(lambda sw, sh, bw, bh: (sw / 2 - bw / 2, sh-bh-sh / 32)),
                                            size=(lambda sw, sh: (sw / 6, sh / 16)),
                                            )
        self.addWidget(self.ptop_announce)
        self.announces["top"] = self.ptop_announce


class PlayerIcon(peng3d.gui.LayeredWidget):
    def __init__(self, name, submenu, window, peng, pos, size):
        super().__init__(name, submenu, window, peng, pos, size)

        self._label = ""
        self._profile = "default"

        self.halo = peng3d.gui.DynImageWidgetLayer(
            "halo", self, 0,
            imgs={
                "default": ("cg:img.btn.halo", "gui"),
                "transparent": ("cg:img.bg.transparent", "gui")
            }
        )
        self.halo.switchImage("transparent")
        self.addLayer(self.halo)

        self.img = peng3d.gui.DynImageWidgetLayer(
            "img", self, 1,
            border=[5, 5],
            imgs={
                "default": ("cg:profile.default", "profile"),
            }
        )
        self.img.switchImage("default")
        self.addLayer(self.img)

        self.hover = peng3d.gui.DynImageWidgetLayer(
            "hover", self, 2,
            border=[5, 5],
            imgs={
                "default": ("cg:img.btn.profile_hover", "gui"),
                "transparent": ("cg:img.bg.transparent", "gui")
            }
        )
        self.hover.switchImage("transparent")
        self.addLayer(self.hover)

        self.lbl = peng3d.gui.LabelWidgetLayer(
            "lbl", self, 3,
            label="",
            font_size=35,
            font_color=[255, 255, 255, 150],
        )
        self.addLayer(self.lbl)

        def f():
            self.hover.switchImage("default")
            self.lbl.label = self._label
        self.addAction("hover_start", f)

        def f():
            self.hover.switchImage("transparent")
            self.lbl.label = ""
        self.addAction("hover_end", f)


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

        self.s_solo = SoloPopupSubMenu("solo", self, self.window, self.peng)
        self.addSubMenu(self.s_solo)

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

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [8, 12], [60, 60])

        self.bg_widget = peng3d.gui.FramedImageButton(
            "bg_widget", self, self.window, self.peng,
            pos=self.grid.get_cell([2, 4], [4, 4], border=0),
            label="",
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        self.addWidget(self.bg_widget, -1)

        self.question = peng3d.gui.Label(
            "question", self, self.window, self.peng,
            pos=self.grid.get_cell([2, 6], [4, 2]),
            label=self.peng.tl("cg:question.unknown.text"),
            font_color=[255, 255, 255, 100],
            multiline=False,
            anchor_y="baseline"
        )
        self.addWidget(self.question)

        self.choice1btn = cgclient.gui.CGButton(
            "choice1btn", self, self.window, self.peng,
            pos=self.grid.get_cell([2, 4], [2, 2]),
            label=self.peng.tl("cg:question.unknown.choice1"),
        )
        self.addWidget(self.choice1btn)

        self.choice1btn.addAction("click", self.on_click_choice1)

        self.choice2btn = cgclient.gui.CGButton(
            "choice2btn", self, self.window, self.peng,
            pos=self.grid.get_cell([4, 4], [2, 2]),
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
            "solo": "solo_yes",
            "black_sow_solo": "black_sow_solo",
        }

        self.choice2 = {
            "reservation": "reservation_no",
            "throw": "throw_no",
            "pigs": "pigs_no",
            "superpigs": "superpigs_no",
            "poverty": "poverty_no",
            "poverty_accept": "poverty_decline",
            "wedding": "wedding_no",
            "solo": "solo_no",
            # Black Sow Solo does not allow choice2
        }

    def on_click_choice1(self):
        self.menu.cg.info(f"User clicked on choice 1 of question {self.questiontype}")

        if self.questiontype.endswith("solo"):
            self.menu.changeSubMenu("solo")
            return

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

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [8, 12], [60, 60])

        self.bg_widget = peng3d.gui.FramedImageButton(
            "bg_widget", self, self.window, self.peng,
            pos=self.grid.get_cell([2, 4], [4, 4], border=0),
            label="",
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        self.addWidget(self.bg_widget, -1)

        self.question = peng3d.gui.Label(
            "question", self, self.window, self.peng,
            pos=self.grid.get_cell([2, 6], [4, 2]),
            label=self.peng.tl("cg:question.poverty_return_trumps.text"),
            font_color=[255, 255, 255, 100],
            multiline=True,
            anchor_y="baseline"
        )
        self.addWidget(self.question)

        self.choice1btn = cgclient.gui.CGButton(
            "choice1btn", self, self.window, self.peng,
            pos=self.grid.get_cell([2, 4], [2, 1]),
            label=self.peng.tl("cg:question.poverty_return_trumps.choice1"),
        )
        self.addWidget(self.choice1btn)

        self.choice1btn.addAction("click", self.on_click, 0)

        self.choice2btn = cgclient.gui.CGButton(
            "choice2btn", self, self.window, self.peng,
            pos=self.grid.get_cell([4, 4], [2, 1]),
            label=self.peng.tl("cg:question.poverty_return_trumps.choice2"),
        )
        self.addWidget(self.choice2btn)

        self.choice2btn.addAction("click", self.on_click, 1)

        self.choice3btn = cgclient.gui.CGButton(
            "choice3btn", self, self.window, self.peng,
            pos=self.grid.get_cell([2, 6], [2, 1]),
            label=self.peng.tl("cg:question.poverty_return_trumps.choice3"),
        )
        self.addWidget(self.choice3btn)

        self.choice3btn.addAction("click", self.on_click, 2)

        self.choice4btn = cgclient.gui.CGButton(
            "choice4btn", self, self.window, self.peng,
            pos=self.grid.get_cell([4, 6], [2, 1]),
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


class SoloPopupSubMenu(peng3d.gui.SubMenu):
    SOLOS = [
        "queen",
        "jack",
        "clubs",
        "spades",
        "hearts",
        "diamonds",
        "fleshless",
        "aces",
        "10s",
        "king",
        "9s",
        "picture",
        "noble_brothel",
        "monastery",
        "brothel",
        "pure_clubs",
        "pure_spades",
        "pure_hearts",
        "pure_diamonds",
        "null",
        "boneless",
    ]

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.register_event_handlers()

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [22, 10], [20, 20])

        self.bg_widget = peng3d.gui.FramedImageButton(
            "bg_widget", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 2], [20, 6], border=0),
            label="",
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        self.addWidget(self.bg_widget, -1)

        self.question = peng3d.gui.Label("question", self, self.window, self.peng,
                                         pos=self.grid.get_cell([0, 7], [22, 1]),
                                         label=self.peng.tl("cg:question.solo.heading"),
                                         font_color=[255, 255, 255, 100],
                                         multiline=False,
                                         )
        self.addWidget(self.question)

        self.solobtns = {}

        for i, solo in enumerate(self.SOLOS):
            sbtn = cgclient.gui.CGButton(f"solo_{solo}btn", self, self.window, self.peng,
                                         pos=self.grid.get_cell([1 + (i % 5) * 4, 6 - (i // 5)], [4, 1]),
                                         label=self.peng.tl(f"cg:question.solo.{solo}"),
                                         font_size=20
                                         )
            self.addWidget(sbtn)
            self.solobtns[f"solo_{solo}"] = sbtn

            sbtn.addAction("click", self.on_click_solo, solo)

    def on_click_solo(self, answer):
        self.menu.cg.client.send_message("cg:game.dk.announce", {
            "type": self.menu.s_question.choice1[self.menu.s_question.questiontype],
            "data": {"type": f"solo_{answer}"}
        })

        self.menu.changeSubMenu("empty")

    def register_event_handlers(self):
        self.peng.cg.add_event_listener("cg:lobby.gamerules.change", self.handle_gamerule_change)

    def handle_gamerule_change(self, event: str, data: dict):
        data = data["gamerules"]
        if "dk.solos" in data:
            for solo, btn in self.solobtns.items():
                btn.enabled = (solo in self.peng.cg.client.lobby.gamerules["dk.solos"])


class GUILayer(peng3d.gui.GUILayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = "Times New Roman"
        self.font_size = 25
        self.font_color = [255, 255, 255, 100]

        self.setBackground([255, 0, 255, 0])

        self.s_ingame = IngameGUISubMenu("ingame", self, self.window, self.peng)
        self.addSubMenu(self.s_ingame)

        self.s_load = LoadingScreenGUISubMenu("loadingscreen", self, self.window, self.peng)
        self.addSubMenu(self.s_load)

        self.s_pause = PauseGUISubMenu("pause", self, self.window, self.peng)
        self.addSubMenu(self.s_pause)

        self.s_scoreboard = ScoreboardGUISubMenu("scoreboard", self, self.window, self.peng)
        self.addSubMenu(self.s_scoreboard)

        self.changeSubMenu("loadingscreen")


class LoadingScreenGUISubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.setBackground([242, 241, 240])


class IngameGUISubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.register_event_handlers()

        self.grid = peng3d.gui.GridLayout(self.peng, self, [12, 10], [30, 10])

        self.readybtn = cgclient.gui.CGButton(
            "readybtn", self, self.window, self.peng,
            pos=self.grid.get_cell([4, 4], [4, 2]),
            label=self.peng.tl("cg:gui.menu.ingame.ingamegui.readybtn.label")
        )
        self.readybtn.visible = False
        self.addWidget(self.readybtn)

        def f():
            if self.menu.menu.status_layer.activeSubMenu != "status_msg":
                self.peng.cg.client.send_message("cg:game.dk.announce", {
                    "type": "ready"
                })

        self.readybtn.addAction("click", f)

        self.throwbtn = cgclient.gui.CGButton(
            "throwbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([4, 3], [4, 1]),
            label=self.peng.tl("cg:gui.menu.ingame.ingamegui.throwbtn.label")
        )
        self.throwbtn.should_visible = False
        self.throwbtn.visible = False
        self.addWidget(self.throwbtn)

        def f():
            if self.menu.menu.status_layer.activeSubMenu != "status_msg":
                self.peng.cg.client.send_message("cg:game.dk.announce", {
                    "type": "throw"
                })

        self.throwbtn.addAction("click", f)

        self.rebtn = cgclient.gui.CGButton(
            "rebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([2, 0], [2, 1]),
            label=""
        )
        self.rebtn.visible = False
        self.rebtn.purpose = "None"
        self.addWidget(self.rebtn)

        def f():
            if self.menu.menu.status_layer.activeSubMenu != "status_msg":
                self.peng.cg.client.send_message("cg:game.dk.announce", {
                    "type": self.rebtn.purpose
                })

        self.rebtn.addAction("click", f)

        self.pigsbtn = cgclient.gui.CGButton(
            "pigsbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([8, 0], [2, 1]),
            label=""
        )
        self.pigsbtn.should_visible = False
        self.pigsbtn.visible = False
        self.pigsbtn.purpose = "None"
        self.addWidget(self.pigsbtn)

        def f():
            if self.menu.menu.status_layer.activeSubMenu != "status_msg":
                self.peng.cg.client.send_message("cg:game.dk.announce", {
                    "type": self.pigsbtn.purpose
                })

        self.pigsbtn.addAction("click", f)

    def register_event_handlers(self):
        self.peng.cg.add_event_listener("cg:lobby.gamerules.change", self.handle_gamerule_change)

    def handle_gamerule_change(self, event: str, data: dict):
        data = data["gamerules"]
        if "dk.throw" in data:
            if data["dk.throw"] == "throw":
                self.throwbtn.should_visible = True
            else:
                self.throwbtn.should_visible = False

        if "dk.pigs" in data:
            if data["dk.pigs"] in ["one_first", "one_on_play", "one_on_fox", "two_on_play"]:
                self.pigsbtn.should_visible = True
                self.pigsbtn.purpose = "pigs"
                self.pigsbtn.label = self.peng.tl("cg:gui.menu.ingame.ingamegui.pigsbtn.pigs")
            else:
                self.pigsbtn.should_visible = False


class PauseGUISubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)


class ScoreboardGUISubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.player_list = []

        self.grid = peng3d.gui.GridLayout(self.peng, self, [20, 8], [30, 30])

        self.setBackground(peng3d.gui.button.FramedImageBackground(
            peng3d.gui.FakeWidget(self),
            bg_idle=("cg:img.bg.bg_dark_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )

        # Upper Bar
        self.w_upper_bar = peng3d.gui.Widget(
            "upper_bar", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 7], [20, 1], border=0),
        )
        self.w_upper_bar.setBackground(peng3d.gui.FramedImageBackground(
            self.w_upper_bar,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3)
        ))
        self.w_upper_bar.clickable = False
        self.addWidget(self.w_upper_bar)

        # Lower Bar
        self.w_lower_bar = peng3d.gui.Widget(
            "lower_bar", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [20, 1], border=0),
        )
        self.w_lower_bar.setBackground(peng3d.gui.FramedImageBackground(
            self.w_lower_bar,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3)
        ))
        self.w_lower_bar.clickable = False
        self.addWidget(self.w_lower_bar)

        self.vertical_lines = []
        for i in range(4):
            line = peng3d.gui.ImageButton(
                f"line{i}", self, self.window, self.peng,
                pos=self.grid.get_cell([4 * (i + 1), 1], [1, 6], border=0),
                size=(lambda sw, sh: (3, sh * 3 / 4)),
                bg_idle=("cg:img.bg.horizontal", "gui"),
                label="",
            )
            line.clickable = False
            self.addWidget(line)
            self.vertical_lines.append(line)

        self.w_upper_line = peng3d.gui.ImageButton(
            "upper_line", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 6], [20, 1], border=0),
            size=(lambda sw, sh: (sw, 3)),
            bg_idle=("cg:img.bg.vertical", "gui"),
            label="",
        )
        self.w_upper_line.clickable = False
        self.addWidget(self.w_upper_line)

        self.w_lower_line = peng3d.gui.ImageButton(
            "lower_line", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 2], [20, 1], border=0),
            size=(lambda sw, sh: (sw, 3)),
            bg_idle=("cg:img.bg.vertical", "gui"),
            label="",
        )
        self.w_lower_line.clickable = False
        self.addWidget(self.w_lower_line)

        def f1(button):
            # Reset the previously pressed button
            for btn in self.togglebuttons:
                if btn != button and btn.pressed:
                    btn.pressed = False
                    btn.doAction("press_up")
                    btn.redraw()

        # Continue Button
        self.continuebtn = peng3d.gui.ToggleButton(
            "continuebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [5, 1]),
            label=self.peng.tl("cg:gui.menu.ingame.scoreboard.continuebtn.label")
        )
        self.continuebtn.setBackground(cgclient.gui.CGButtonBG(self.continuebtn))
        self.addWidget(self.continuebtn)

        def f():
            self.peng.cg.client.send_message("cg:game.dk.announce", {
                "type": "continue_yes",
                "announcer": self.peng.cg.client.user_id.hex
            })

        self.continuebtn.addAction("press_down", f)
        self.continuebtn.addAction("press_down", f1, self.continuebtn)

        def f():
            self.peng.cg.client.send_message("cg:game.dk.announce", {
                "type": "continue_no",
                "announcer": self.peng.cg.client.user_id.hex
            })

        self.continuebtn.addAction("press_up", f)

        # Continue Later Button
        self.adjournbtn = peng3d.gui.ToggleButton(
            "adjournbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([5, 0], [5, 1]),
            label=self.peng.tl("cg:gui.menu.ingame.scoreboard.adjournbtn.label")
        )
        self.adjournbtn.setBackground(cgclient.gui.CGButtonBG(self.adjournbtn))
        self.addWidget(self.adjournbtn)

        def f():
            self.peng.cg.client.send_message("cg:game.dk.announce", {
                "type": "adjourn_yes",
                "announcer": self.peng.cg.client.user_id.hex
            })

        self.adjournbtn.addAction("press_down", f)
        self.adjournbtn.addAction("press_down", f1, self.adjournbtn)

        def f():
            self.peng.cg.client.send_message("cg:game.dk.announce", {
                "type": "adjourn_no",
                "announcer": self.peng.cg.client.user_id.hex
            })

        self.adjournbtn.addAction("press_up", f)

        # Quit Button
        self.quitbtn = peng3d.gui.ToggleButton(
            "quitbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([10, 0], [5, 1]),
            label=self.peng.tl("cg:gui.menu.ingame.scoreboard.quitbtn.label")
        )
        self.quitbtn.setBackground(cgclient.gui.CGButtonBG(self.quitbtn))
        self.addWidget(self.quitbtn)
        self.quitbtn.enabled = False

        def f():
            self.peng.cg.client.send_message("cg:game.dk.announce", {
                "type": "quit_yes",
                "announcer": self.peng.cg.client.user_id.hex
            })

        self.quitbtn.addAction("press_down", f)
        self.quitbtn.addAction("press_down", f1, self.quitbtn)

        def f():
            self.peng.cg.client.send_message("cg:game.dk.announce", {
                "type": "quit_no",
                "announcer": self.peng.cg.client.user_id.hex
            })

        self.quitbtn.addAction("press_up", f)

        # Cancel Button
        self.cancelbtn = peng3d.gui.ToggleButton(
            "cancelbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([15, 0], [5, 1]),
            label=self.peng.tl("cg:gui.menu.ingame.scoreboard.cancelbtn.label")
        )
        self.cancelbtn.setBackground(cgclient.gui.CGButtonBG(self.cancelbtn))
        self.addWidget(self.cancelbtn)

        def f():
            self.peng.cg.client.send_message("cg:game.dk.announce", {
                "type": "cancel_yes",
                "announcer": self.peng.cg.client.user_id.hex
            })

        self.cancelbtn.addAction("press_down", f)
        self.cancelbtn.addAction("press_down", f1, self.cancelbtn)

        def f():
            self.peng.cg.client.send_message("cg:game.dk.announce", {
                "type": "cancel_no",
                "announcer": self.peng.cg.client.user_id.hex
            })

        self.cancelbtn.addAction("press_up", f)

        self.togglebuttons = [self.continuebtn, self.adjournbtn, self.quitbtn, self.cancelbtn]

        self.heading = peng3d.gui.Label(
            "heading", self, self.window, self.peng,
            pos=self.grid.get_cell([9, 7], [2, 1]),
            label="Round -1",
        )
        self.heading.clickable = False
        self.addWidget(self.heading)

        # Player Labels
        self.player_labels = []
        for i in range(4):
            label = peng3d.gui.Label(
                f"p_label{i}", self, self.window, self.peng,
                pos=self.grid.get_cell([i * 4, 6], [4, 1]),
                label="player label",
            )
            label.clickable = False
            self.addWidget(label)
            self.player_labels.append(label)

        # Scores
        self.score_labels = []
        for i in range(4):
            label = peng3d.gui.Label(
                f"s_label{i}", self, self.window, self.peng,
                pos=self.grid.get_cell([i * 4, 1], [4, 1]),
                label="score_label",
            )
            label.clickable = False
            self.addWidget(label)
            self.score_labels.append(label)

        self.container = peng3d.gui.ScrollableContainer(
            "container", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 2], [20, 4], border=0),
            size=(lambda sw, sh: (sw, 0)),
            content_height=0
        )
        self.container.pos = (lambda sw, sh, bw, bh: (
            self.grid.get_cell([0, 2], [20, 4], anchor_y="top", border=0).pos[0],
            self.grid.get_cell([0, 2], [20, 4], anchor_y="top", border=0).pos[1] - bh
        ))
        self.container._scrollbar.visible = False
        self.addWidget(self.container)

        # Player scores
        self.player_scores = [[], [], [], []]

        # Game Summary
        self.game_summaries = []

        # Seperation Bars
        self.separation_bars = [[], [], [], [], []]

    def init_game(self, player_list: List[uuid.UUID]):
        self.reset()

        self.player_list = player_list
        for i, uid in enumerate(self.player_list):
            self.player_labels[i].label = self.peng.cg.client.get_user(uid).username

    def add_round(self, round_num: int, winner: str,
                  game_type: str, eyes: List[int], extras: List[List[str]],
                  point_change: List[int], points: List[str]):
        # Heading
        self.heading.label = self.peng.tl("cg:gui.menu.ingame.scoreboard.heading", {"round": round_num})

        # Quit button / Cancel button
        if round_num % 4 == 0:
            self.quitbtn.enabled = True
            self.quitbtn._label.font_size = 25
            self.quitbtn.label = self.peng.tl("cg:gui.menu.ingame.scoreboard.quitbtn.label")
        else:
            self.quitbtn.enabled = False
            self.quitbtn._label.font_size = 16
            self.quitbtn.label = self.peng.tl(
                "cg:gui.menu.ingame.scoreboard.quitbtn.label3", {"rounds": 4 - (round_num % 4)})

        # Height of the new widgets
        font = pyglet.font.load("Times New Roman", 16)
        font_height = font.ascent - font.descent
        h = font_height * (len(extras) + 2) + 8

        # Adjust height of the container
        old_container_height = self.container.size[1]
        if old_container_height + h > self.window.height * 1 / 2 - 3:
            self.container.size = (lambda sw, sh: (sw, sh * 1 / 2 - 3))
            self.container.content_height = old_container_height + h - (self.window.height * 1 / 2 - 3)
        else:
            self.container.size = (lambda sw, sh: (sw, old_container_height + h))

        # Move old widgets upwards
        # Scores
        for i, l in enumerate(self.player_scores):
            for j in l:
                old_widget_pos = j.pos[1] - self.container.pos[1]
                j.pos = self._lambda_score_pos(i, old_widget_pos + h)

        # Summaries
        for j in self.game_summaries:
            old_widget_pos = j.pos[1] - self.container.pos[1]
            j.pos = self._lambda_bar_pos(4, old_widget_pos + h)

        # Bars
        for i, l in enumerate(self.separation_bars):
            for j in l:
                old_widget_pos = j.pos[1] - self.container.pos[1]
                if not j.visible:  # Workaround because of the pos being [-10000, -10000] when invisible
                    j.visible = True
                    old_widget_pos = j.pos[1] - self.container.pos[1]
                    j.visible = False
                j.pos = self._lambda_bar_pos(i, old_widget_pos + h)

        # Create new widgets
        for i in range(5):
            # Scores
            if i < 4:
                score = peng3d.gui.Label(
                    f"score{i}.{round_num}", self.container, self.window, self.peng,
                    pos=self._lambda_score_pos(i, 0),
                    size=(lambda sw, sh: (sw / 5, h)),
                    label=str(point_change[i])
                )
                score.clickable = False
                self.container.addWidget(score)
                self.player_scores[i].append(score)

            # Summary
            elif i == 4:
                summary_label = ""
                summary_label += str(self.peng.tl(f"cg:game.doppelkopf.game_type.{game_type}")) + "\n"
                summary_label += f"{eyes[0]} : {eyes[1]}\n"
                for extra in extras:
                    # TODO This kind of undermines the whole point of peng.tl...
                    summary_label += str(self.peng.tl(f"cg:game.doppelkopf.extra.{extra}")) + "\n"
                summary = peng3d.gui.Label(
                    f"summary{round_num}", self.container, self.window, self.peng,
                    pos=self._lambda_bar_pos(i, 0),
                    size=(lambda sw, sh: (sw / 5 - 60, h)),
                    label=summary_label,
                    multiline=True,
                    font_size=16,
                )
                summary.clickable = False
                self.container.addWidget(summary)
                self.game_summaries.append(summary)

            # Separation bar
            bar = peng3d.gui.ImageButton(
                f"separation_bar{i}.{round_num}", self.container, self.window, self.peng,
                pos=self._lambda_bar_pos(i, 0),
                size=(lambda sw, sh: (sw / 5 - 60, 3)),
                bg_idle=("cg:img.bg.gray_brown", "gui"),
                label=""
            )
            bar.clickable = False
            bar.visible = False
            self.container.addWidget(bar)
            self.separation_bars[i].append(bar)

            # Previous separation bar
            if round_num > 1:
                self.container.getWidget(f"separation_bar{i}.{round_num - 1}").visible = True

        # Update total scores
        for i, j in enumerate(self.score_labels):
            j.label = points[i]

    def reset(self):
        self.continuebtn.pressed = False
        self.continuebtn.label = self.peng.tl("cg:gui.menu.ingame.scoreboard.continuebtn.label")

        self.adjournbtn.pressed = False
        self.adjournbtn.label = self.peng.tl("cg:gui.menu.ingame.scoreboard.adjournbtn.label")

        self.quitbtn.pressed = False
        self.quitbtn.label = self.peng.tl("cg:gui.menu.ingame.scoreboard.quitbtn.label")

        self.cancelbtn.pressed = False
        self.cancelbtn.label = self.peng.tl("cg:gui.menu.ingame.scoreboard.cancelbtn.label")

        for i in self.separation_bars:
            for bar in i:
                bar.visible = False
        self.separation_bars = [[], [], [], [], []]

        for i in self.score_labels:
            i.visible = False
        self.score_labels = []

        self.container.size = (lambda sw, sh: (sw, 0))
        self.container._scrollbar.visible = False

        for i in self.player_scores:
            for s in i:
                s.visible = False
        self.player_scores = [[], [], [], []]

        for i in self.game_summaries:
            i.visible = False
        self.game_summaries = []

    def _lambda_score_pos(self, i, y):
        return lambda sw, sh, ww, wh: (sw / 5 * i, y - 3)

    def _lambda_bar_pos(self, i, y):
        return lambda sw, sh, ww, wh: (sw / 5 * i + 30, y)

    def register_event_handlers(self):
        self.peng.cg.add_event_listener("cg:user.update", self.handle_user_update)

    def handle_user_update(self, event: str, data: dict):
        if data["uuid"] in self.player_list:
            u = self.peng.cg.client.users_uuid.get(data["uuid"], None)
            if u is not None:
                self.player_labels[self.player_list.index(data["uuid"])].label = u.username


class StatusLayer(peng3d.gui.GUILayer):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        # Status Message Menu
        self.d_status_message = peng3d.gui.menus.DialogSubMenu(
            "status_msg", self, self.window, self.peng,
            font="Times New Roman",
            font_size=25,
            font_color=[255, 255, 255, 100],
        )
        self.d_status_message.setBackground(peng3d.gui.button.FramedImageBackground(
            peng3d.gui.FakeWidget(self.d_status_message),
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )
        self.d_status_message.label_ok = self.peng.tl("cg:gui.menu.status_msg.okbtn.label")
        self.d_status_message.wbtn_ok.setBackground(peng3d.gui.FramedImageBackground(
            self.d_status_message.wbtn_ok,
            bg_idle=("cg:img.btn.btn_idle", "gui"),
            bg_hover=("cg:img.btn.btn_hov", "gui"),
            bg_pressed=("cg:img.btn.btn_press", "gui"),
            frame=[[249, 502, 249], [0, 1, 0]],
            scale=(None, 0),
            repeat_edge=True, repeat_center=True,
        )
        )
        self.addSubMenu(self.d_status_message)

        def f():
            self.peng.cg.send_event("cg:status.message.close")

        self.d_status_message.wbtn_ok.addAction("click", f)

        # Empty menu
        self.s_empty = peng3d.gui.SubMenu("empty", self, self.window, self.peng)
        self.addSubMenu(self.s_empty)

        self.changeSubMenu("empty")
