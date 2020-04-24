#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  card.py
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
from typing import List

import peng3d
from vectormath import Vector3

import cg

import pyglet
from pyglet.gl import *
import numpy as np

SUITES = {
    "c": "clubs",
    "s": "spades",
    "h": "hearts",
    "d": "diamonds",
}

COUNTS = {
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "10",
    "j": "jack",
    "q": "queen",
    "k": "king",
    "a": "ace",
}

# Standard cards - 6cm x 9cm
CARD_SIZE_W = 0.6
CARD_SIZE_H = 0.9


def rotation_matrix(axis, theta):
    # From https://stackoverflow.com/a/6802723
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


class Card(object):
    def __init__(self,
                 c: cg.CardGame,
                 layer,
                 slot: str,
                 cardid: uuid.UUID, value: str,
                 ):

        self.cg = c

        self.layer = layer

        self.slot: str = slot
        self.cardid: uuid.UUID = cardid
        self.value: value = value

        self.pos: List[float] = [0, 0, 0]
        self.rot: List[float] = [0, 180, 0]  # In degrees, (short axis, long axis, z axis)

        # 4 vertices front, 4 vertices back
        self.vlist = self.layer.batch.add(8, GL_QUADS,
                                          pyglet.graphics.TextureGroup(
                                              peng3d.gui.button._FakeTexture(*self.layer.peng.resourceMgr.getTex(self.layer.get_backname(), "card")),
                                              parent=pyglet.graphics.OrderedGroup(1)
                                          ),
                                          "v3f",
                                          "t3f",
                                          )

        self.should_redraw: bool = True

    def on_transfer(self, new_slot: str):
        pass

    def redraw(self):
        self.should_redraw = True

    def draw(self):
        if self.should_redraw:
            self.on_redraw()

    def on_redraw(self):
        idx = self.layer.slots[self.slot].index(self)
        self.pos = self.layer.get_card_slot_pos(self.slot, idx, len(self.layer.slots[self.slot]))

        #self.rot[2] = idx
        #self.rot[1] = idx*2

        # First, set the texture coordinates
        texf = self.layer.peng.resourceMgr.getTex(self.get_texname(), "card")
        texb = self.layer.peng.resourceMgr.getTex(self.layer.get_backname(), "card")
        tf = texf[2]
        tb = texb[2]
        self.vlist.tex_coords = tf+tb

        if texf[1] != texb[1]:
            self.cg.warn(f"Front and back texture IDs for card {self.cardid} with value {self.value} do not match!")

        # Then, generate and set the vertices
        vf = self.get_vertices(0)
        vb = self.get_vertices(0.00002)  # 0.2mm

        self.vlist.vertices = vf+vb

    def get_texname(self):
        if self.value == "":
            name = "unknown_front"
        elif self.value == "j0":
            name = "jolly_joker"
        else:
            suite = SUITES[self.value[0]]
            count = COUNTS[self.value[1:]]
            name = f"{suite}_{count}"

        return f"cg:card.{name}"

    def get_vertices(self, offset: float) -> List[float]:
        # Card position is anchored in the center of the card
        # Rotation is applied first, then the card is moved to its final position
        center = Vector3(*self.pos)

        # First, generate vectors for x and y of card
        vcw = Vector3(CARD_SIZE_W/2, 0, 0)  # Vector pointing along the width (short side) of the card
        vch = Vector3(0, 0, CARD_SIZE_H/2)  # Vector pointing along the height (long side) of the card
        vcp = Vector3(0, offset, 0)  # Vector pointing "out" of the card, perpendicular

        #a_s = math.radians(self.rot[0])  # Angle along short axis in radians,
        if self.rot[0] != 0:
            self.cg.error(f"Card {self.cardid} with value {self.value} has non-zero short axis rotation of {self.rot[0]}")
        a_l = math.radians(self.rot[1])  # Angle along long axis in radians
        a_z = math.radians(self.rot[2])  # Angle along z axis in radians

        # Rotations are not "generic" and specifically optimized (for readability...) for
        # cards and how they are moved
        # The z axis is fixed to simplify the math. It is mainly used for card orientation
        # on screen
        # The long axis is used to flip cards
        # TODO: The short axis is currently not implemented

        # Generate and apply the z axis rotation matrix
        mz = rotation_matrix([0, 0, 1], a_z)
        vcw = Vector3(np.dot(mz, vcw))
        vch = Vector3(np.dot(mz, vch))
        vcp = Vector3(np.dot(mz, vcp))

        # Generate and apply the long (height) axis rotation matrix
        # Note that we rotate around the rotated vch vector
        ml = rotation_matrix(list(vch), a_l)
        vcw = Vector3(np.dot(ml, vcw))
        vch = Vector3(np.dot(ml, vch))
        vcp = Vector3(np.dot(ml, vcp))

        # Generate the four corners of the card
        c1 = -vcw-vch  # Bottom left
        c2 = +vcw-vch  # Bottom right
        c3 = +vcw+vch  # Top right
        c4 = -vcw+vch  # Top left

        # Add a multiple of the direction vector and offset
        vcp += center

        c1 += vcp
        c2 += vcp
        c3 += vcp
        c4 += vcp

        # Add together for usage in vertex list
        return list(c1) + list(c2) + list(c3) + list(c4)

    def delete(self):
        self.vlist.delete()


