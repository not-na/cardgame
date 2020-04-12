#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  stretchbtn
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

import time

from pyglet.gl import *


class StretchBackground(peng3d.gui.widgets.Background):
    vlist_layer = 0

    def __init__(self, widget,bg_idle=[GL_TEXTURE_2D,GL_TEXTURE1,[0]*12],bg_hover=None,bg_disabled=None,bg_pressed=None, frame=[2,10,2]):
        tc = bg_idle[2]
        tsx, tsy = tc[3] - tc[0], tc[10] - tc[1]  # Texture Size

        self.frame = list(map(lambda x: x * (tsx/sum(frame)), frame))

        bg = bg_idle
        self.bg_texinfo = bg
        if bg_hover is None:
            self.bg_hover = bg
        else:
            self.bg_hover = bg_hover
        if bg_disabled is None:
            self.bg_disabled = bg
        else:
            self.bg_disabled = bg_disabled
        if bg_pressed is None:
            self.bg_pressed = bg
        else:
            self.bg_pressed = bg_pressed

        super().__init__(widget)

    def init_bg(self):
        self.bg_group = pyglet.graphics.TextureGroup(peng3d.gui.button._FakeTexture(*self.bg_texinfo),
                                                     parent=pyglet.graphics.OrderedGroup(self.vlist_layer))
        self.vlist_bg = self.submenu.batch2d.add(12,GL_QUADS,self.bg_group,
            "v2f", "t3f"
            )
        self.reg_vlist(self.vlist_bg)

    def redraw_bg(self):
        # Convenience Variables
        sx, sy = self.widget.size
        x, y = self.widget.pos

        tc = self.bg_texinfo[2]
        tsx, tsy = tc[3] - tc[0], tc[10] - tc[1]  # Texture Size

        fl, fr = self.frame[0] / tsy * sy, self.frame[2] / tsy * sy
        fc = sx - (fl + fr)

        # Button Background

        # Vertices
        v0 = x,           y
        v1 = x + fl,      y
        v2 = x + fl,      y + sy
        v3 = x,           y + sy
        v4 = x + fl + fc, y
        v5 = x + fl + fc, y + sy
        v6 = x + sx,      y
        v7 = x + sx,      y + sy

        self.vlist_bg.vertices = v0+v1+v2+v3 + v1+v4+v5+v2 + v4+v6+v7+v5

        bg_disabled_coords = self.transform_texture(self.bg_disabled)
        bg_pressed_coords = self.transform_texture(self.bg_pressed)
        bg_hovered_coords = self.transform_texture(self.bg_hover)
        bg_idle_coords = self.transform_texture(self.bg_texinfo)

        if not self.widget.enabled:
            self.vlist_bg.tex_coords = bg_disabled_coords
        elif self.widget.pressed:
            self.vlist_bg.tex_coords = bg_pressed_coords
        elif self.widget.is_hovering:
            self.vlist_bg.tex_coords = bg_hovered_coords
        else:
            self.vlist_bg.tex_coords = bg_idle_coords

    def transform_texture(self, texture):
        tc = texture[2]

        # TexCoords
        t0 = tc[0], tc[1], tc[2]
        t1 = tc[0] + self.frame[0], tc[1], tc[2]
        t2 = tc[9] + self.frame[0], tc[10], tc[11]
        t3 = tc[9], tc[10], tc[11]
        t4 = tc[3] - self.frame[2], tc[4], tc[5]
        t5 = tc[6] - self.frame[2], tc[7], tc[8]
        t6 = tc[3], tc[4], tc[5]
        t7 = tc[6], tc[7], tc[8]

        tex_coords = t0 + t1 + t2 + t3 + t1 + t4 + t5 + t2 + t4 + t6 + t7 + t5
        return tex_coords


class StretchButton(peng3d.gui.button.Button):
    def __init__(self, name, submenu, window, peng, pos=None, size=[100, 24], bg=None, label="Button", min_size=None,
                 bg_idle=None, bg_hover=None, bg_pressed=None, bg_disabled=None, frame=[2,10,2],
                 font="Arial", font_size=16, font_color=[0, 0, 0, 255], border=[0, 0]):
        if bg is None:
            bg = StretchBackground(self, bg_idle, bg_hover, bg_disabled, bg_pressed, frame)
        super().__init__(name, submenu, window, peng, pos, size, bg, label=label, font=font, font_size=font_size,
                         font_color=font_color, border=border)


class RepeatBackground(peng3d.gui.widgets.Background):
    vlist_layer = 0

    def __init__(self, widget,bg_idle=[GL_TEXTURE_2D,GL_TEXTURE1,[0]*12],bg_hover=None,bg_disabled=None,bg_pressed=None, frame=[2,10,2]):
        tc = bg_idle[2]
        tsx, tsy = tc[3] - tc[0], tc[10] - tc[1]  # Texture Size

        self.frame = list(map(lambda x: x * (tsx/sum(frame)), frame))

        bg = bg_idle
        self.bg_texinfo = bg
        if bg_hover is None:
            self.bg_hover = bg
        else:
            self.bg_hover = bg_hover
        if bg_disabled is None:
            self.bg_disabled = bg
        else:
            self.bg_disabled = bg_disabled
        if bg_pressed is None:
            self.bg_pressed = bg
        else:
            self.bg_pressed = bg_pressed

        super().__init__(widget)

    def init_bg(self):
        self.bg_group = pyglet.graphics.TextureGroup(peng3d.gui.button._FakeTexture(*self.bg_texinfo),
                                                     parent=pyglet.graphics.OrderedGroup(self.vlist_layer))
        self.vlist_bg = self.submenu.batch2d.add(12,GL_QUADS,self.bg_group,
            "v2f", "t3f")
        self.reg_vlist(self.vlist_bg)

    def redraw_bg(self):
        # Convenience Variables
        sx, sy = self.widget.size
        x, y = self.widget.pos

        tc = self.bg_texinfo[2]
        tsx, tsy = tc[3] - tc[0], tc[10] - tc[1]  # Texture Size

        fl, ofc, fr = self.frame[0] / tsy * sy, self.frame[1] / tsy * sy, self.frame[2] / tsy * sy
        fc = sx - (fl + fr)

        am = int(fc/ofc)  # Amount of complete middle parts

        self.vlist_bg.resize((am+3)*4)

        # Button Background

        # Vertices
        # 3--2----9-5--7
        # |  |    | |  |
        # 0--1----8-4--6

        v0 = x,      y
        v1 = x + fl, y
        v2 = x + fl, y + sy
        v3 = x,      y + sy

        middle_vs = []
        for i in range(am):
            middle_vs += x + fl + i * ofc,     y,\
                         x + fl + (i+1) * ofc, y,\
                         x + fl + (i+1) * ofc, y + sy,\
                         x + fl + i * ofc,     y + sy

        middle_vs += x + fl + am * ofc, y,\
                     x + sx - fr,       y,\
                     x + sx - fr,       y + sy,\
                     x + fl + am * ofc, y + sy

        v4 = x + sx - fr, y
        v5 = x + sx - fr, y + sy
        v6 = x + sx,      y
        v7 = x + sx,      y + sy

        self.vlist_bg.vertices = v0+v1+v2+v3 + tuple(middle_vs) + v4+v6+v7+v5

        bg_disabled_coords = self.transform_texture(self.bg_disabled)
        bg_pressed_coords = self.transform_texture(self.bg_pressed)
        bg_hovered_coords = self.transform_texture(self.bg_hover)
        bg_idle_coords = self.transform_texture(self.bg_texinfo)

        if not self.widget.enabled:
            self.vlist_bg.tex_coords = bg_disabled_coords
        elif self.widget.pressed or (isinstance(self, RepeatTextBackground) and self.pressed):
            self.vlist_bg.tex_coords = bg_pressed_coords
        elif self.widget.is_hovering:
            self.vlist_bg.tex_coords = bg_hovered_coords
        else:
            self.vlist_bg.tex_coords = bg_idle_coords

    def transform_texture(self, texture):
        # Convenience Variables
        sx, sy = self.widget.size
        x, y = self.widget.pos

        tc = texture[2]
        tsx, tsy = tc[3] - tc[0], tc[10] - tc[1]  # Texture Size

        fl, ofc, fr = self.frame[0] / tsy * sy, self.frame[1] / tsy * sy, self.frame[2] / tsy * sy
        fc = sx - (fl + fr)

        am = int(fc / ofc)  # Amount of complete middle parts

        # TexCoords
        t0 = tc[0], tc[1], tc[2]
        t1 = tc[0] + self.frame[0], tc[1], tc[2]
        t2 = tc[9] + self.frame[0], tc[10], tc[11]
        t3 = tc[9], tc[10], tc[11]

        t4 = tc[3] - self.frame[2], tc[4], tc[5]
        t5 = tc[6] - self.frame[2], tc[7], tc[8]
        t6 = tc[3], tc[4], tc[5]
        t7 = tc[6], tc[7], tc[8]

        middle_ts = am * (t1 + t4 + t5 + t2)

        rx = sx - fl - fr - am * ofc
        orx = rx / sy * tsy

        t8 = tc[3] - self.frame[2] - orx, tc[4], tc[5]
        t9 = tc[6] - self.frame[2] - orx, tc[7], tc[8]

        tex_coords = t0+t1+t2+t3 + middle_ts + t8+t4+t5+t9 + t4+t6+t7+t5
        return tex_coords


class RepeatButton(peng3d.gui.button.Button):
    def __init__(self, name, submenu, window, peng, pos=None, size=[100, 24], bg=None, label="Button", min_size=None,
                 bg_idle=None, bg_hover=None, bg_pressed=None, bg_disabled=None, frame=[2,10,2],
                 font="Arial", font_size=16, font_color=[0, 0, 0, 255], border=[0, 0]):
        if bg is None:
            bg = RepeatBackground(self, bg_idle, bg_hover, bg_disabled, bg_pressed, frame)
        super().__init__(name, submenu, window, peng, pos, size, bg, label=label, font=font, font_size=font_size,
                         font_color=font_color, border=border)


class TiledImageBackground(peng3d.gui.widgets.Background):
    vlist_layer = 0

    def __init__(self, widget, bg_idle=[GL_TEXTURE_2D,GL_TEXTURE1,[0]*12],bg_hover=None,bg_disabled=None,bg_pressed=None, scale=1):
        super().__init__(widget)

        bg = bg_idle
        self.bg_texinfo = bg
        if bg_hover is None:
            self.bg_hover = bg
        else:
            self.bg_hover = bg_hover
        if bg_disabled is None:
            self.bg_disabled = bg
        else:
            self.bg_disabled = bg_disabled
        if bg_pressed is None:
            self.bg_pressed = bg
        else:
            self.bg_pressed = bg_pressed

        self.scale = scale

    def init_bg(self):
        self.bg_group = pyglet.graphics.TextureGroup(peng3d.gui.button._FakeTexture(*self.bg_texinfo),
                                                     parent=pyglet.graphics.OrderedGroup(self.vlist_layer))
        self.vlist_bg = self.submenu.batch2d.add(4, GL_QUADS, self.bg_group,
                                                 "v2f", "t3f")
        self.reg_vlist(self.vlist_bg)

    def redraw_bg(self):
        sx, sy = self.window.width, self.window.height
        tc = self.bg_texinfo[2]
        tsx, tsy = (tc[3] - tc[0]) * 4096, (tc[10] - tc[1]) * 4096   # Texture Size

        tx, ty = tsx * self.scale, tsy * self.scale  # Tile Size

        amx, amy = int(sx / tx), int(sy / ty)  # Amount of completed tiles in x and y direction

        self.vlist_bg.resize(4 * ((amx+1) * (amy+1)))

        vertices = []

        # Completed tiles
        for j in range(amy):
            for i in range(amx):
                vertices += i * tx, j * ty
                vertices += (i+1) * tx, j * ty
                vertices += (i+1) * tx, (j+1) * ty
                vertices += i * tx, (j+1) * ty

        # Y-shortened tiles
        for i in range(amx):
            vertices += i * tx, amy * ty
            vertices += (i+1) * tx, amy * ty
            vertices += (i+1) * tx, sy
            vertices += i * tx, sy

        # X-shortened tiles
        for j in range(amy):
            vertices += amx * tx, j * ty
            vertices += sx, j * ty
            vertices += sx, (j+1) * ty
            vertices += amx * tx, (j+1) * ty

        # X-Y-shortened tile
        vertices += amx * tx, amy * ty
        vertices += sx, amy * ty
        vertices += sx, sy
        vertices += amx * tx, sy

        self.vlist_bg.vertices = vertices

        bg_disabled_coords = self.transform_texture(self.bg_disabled)
        bg_pressed_coords = self.transform_texture(self.bg_pressed)
        bg_hovered_coords = self.transform_texture(self.bg_hover)
        bg_idle_coords = self.transform_texture(self.bg_texinfo)

        if not self.widget.enabled:
            self.vlist_bg.tex_coords = bg_disabled_coords
        elif self.widget.pressed or (isinstance(self, RepeatTextBackground) and self.pressed):
            self.vlist_bg.tex_coords = bg_pressed_coords
        elif self.widget.is_hovering:
            self.vlist_bg.tex_coords = bg_hovered_coords
        else:
            self.vlist_bg.tex_coords = bg_idle_coords

    def transform_texture(self, texture):
        sx, sy = self.window.width, self.window.height
        tc = self.bg_texinfo[2]
        tsx, tsy = (tc[3] - tc[0]) * 4096, (tc[10] - tc[1]) * 4096  # Texture Size

        tx, ty = tsx * self.scale, tsy * self.scale  # Tile Size

        amx, amy = int(sx / tx), int(sy / ty)  # Amount of completed tiles in x and y direction

        rx, ry = sx % tx, sy % ty
        orx, ory = rx / self.scale / 4096, ry / self.scale / 4096

        # Completed textures
        textures = list(tc * (amx * amy))

        # Y-shortened textures
        mtc = list(tc)
        mtc[7], mtc[10] = ory, ory
        textures += mtc * amx

        # X-shortened textures
        mtc = list(tc)
        mtc[3], mtc[6] = orx, orx
        textures += mtc * amy

        # X-Y-shortened texture
        mtc[7], mtc[10] = ory, ory
        textures += mtc

        return textures


class RepeatTextBackground(RepeatBackground):
    def __init__(self, widget, bg_idle=[GL_TEXTURE_2D,GL_TEXTURE1,[0]*12],bg_hover=None,bg_disabled=None,bg_pressed=None,
                 frame=[2,10,2], border=[0, 0]):
        super().__init__(widget, bg_idle, bg_hover, bg_disabled, bg_pressed, frame)

        self.border = border
        self.stime = 0

    def init_bg(self):
        super().init_bg()
        self.vlist_cursor = self.submenu.batch2d.add(2, GL_LINES, pyglet.graphics.OrderedGroup(10),
            "v2f", "c4B",
        )
        self.reg_vlist(self.vlist_cursor)

    def redraw_bg(self):
        super().redraw_bg()

        sx, sy, x, y, bx, by = self.getPosSize()

        otext = self.widget._text.text
        self.widget._text.text = self.widget._text.text[:self.widget.cursor_pos]
        tw = self.widget._text.content_width + 2 if len(self.widget._text.text) != 0 else 0
        self.widget._text.text = otext

        v = x + tw + bx, y + by, x + tw + bx, y + sy - by
        self.vlist_cursor.vertices = v

        s = [0, 0, 0, 0]
        c = s * 2 if (self.stime - time.time()) % 1 > .5 or not self.widget.focussed else [255, 255, 255, 100] * 2
        self.vlist_cursor.colors = c

    def getPosSize(self):
        sx, sy = self.widget.size
        x, y = self.widget.pos
        bx, by = self.border
        return sx, sy, x, y, bx, by

    @property
    def pressed(self):
        return self.widget.focussed
