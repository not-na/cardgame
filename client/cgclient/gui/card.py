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
import time
import uuid
from typing import List, Tuple

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
HOVER_EXTENSION = 0.1
CLICK_EXTENSION = 0.2
SELECTED_EXTENSION = 0.3
DEFAULT_ANIM_DURATION = 1.0

ANIM_STATE_DONE = 0
ANIM_STATE_ACTIVE = 1


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


def lin_interpolate(src: float, target: float, p: float):
    # Just a simple linear interpolation
    return src+(target-src)*p


def multi_interpolate(src: List[float], target: List[float], p: float):
    if len(src) != len(target):
        raise ValueError("multi_interpolate() requires two list of equal length")

    out = []
    for i in range(len(src)):
        out.append(lin_interpolate(src[i], target[i], p))

    return out


class _FakeTexture(object):
    def __init__(self, card):
        self.card = card

    @property
    def target(self):
        return self.card.texf[0]

    @property
    def id(self):
        return self.card.texf[1]

    @property
    def tex_coords(self):
        return self.card.texf[2]


class Card(object):

    def __init__(self,
                 c: cg.CardGame,
                 layer,
                 slot: str,
                 cardid: uuid.UUID, value: str,
                 ):

        self.cg = c
        self.game = self.cg.client.game

        self.layer = layer

        self.slot: str = slot
        self.cardid: uuid.UUID = cardid
        self.value: value = value

        self.anim_fromslot: str = slot
        self.anim_stime: float = 0.0
        self.anim_state: int = ANIM_STATE_DONE
        self.anim_frompos = [0, 0, 0]
        self.anim_fromrot = [0, 0, 0]
        self.anim_duration: float = 1.0

        self.color_id = self.layer.gen_color_id(self)

        self.texf = self.layer.peng.resourceMgr.getTex(self.get_texname(), "card")
        self.texb = self.layer.peng.resourceMgr.getTex(self.layer.get_backname(), "card")

        self.pos: List[float] = [0, 0, 0]
        self.rot: List[float] = [0, 0, 0]  # In degrees, (short axis, long axis, z axis)

        # 4 vertices front, 4 vertices back
        self.vlist_back = self.layer.batch.add(4, GL_QUADS,
                                               pyglet.graphics.TextureGroup(
                                                   peng3d.gui.button._FakeTexture(*self.layer.peng.resourceMgr.getTex(self.layer.get_backname(), "card")),
                                                   parent=pyglet.graphics.OrderedGroup(1)
                                               ),
                                               "v3f",
                                               "t3f/static",
                                               )
        self.vlist_front = self.layer.batch.add(4, GL_QUADS,
                                               pyglet.graphics.TextureGroup(
                                                   _FakeTexture(self),
                                                   parent=pyglet.graphics.OrderedGroup(1),
                                               ),
                                               "v3f",
                                               "t3f/static",
                                               )

        self.vlist_pick = self.layer.batch_pick.add(4, GL_QUADS,
                                                    None,
                                                    "v3f",
                                                    ("c3B/static", self.color_id*4),
                                                    )

        self.should_redraw: bool = True
        self.selected: bool = False
        self.hovered: bool = False
        self.clicked: bool = False
        self.dragged: bool = False

    def on_transfer(self, new_slot: str):
        pass

    def start_anim(self, from_slot: str, to_slot: str, duration=DEFAULT_ANIM_DURATION):
        self.anim_state = ANIM_STATE_ACTIVE
        self.anim_stime = time.time()
        self.anim_fromslot = from_slot
        self.anim_frompos = self.pos
        self.anim_fromrot = self.rot
        self.anim_duration = duration
        self.slot = to_slot

        self.redraw()

    def update_anim(self):
        if self.anim_state == ANIM_STATE_DONE:
            return

        idx = self.game.slots[self.slot].index(self)
        tpos, trot = self.get_card_pos_rot(self.slot, idx, len(self.game.slots[self.slot]))

        if self.anim_fromslot == "stack":
            self.anim_state = ANIM_STATE_DONE
            self.pos = tpos
            self.rot = trot

            self.redraw()
            return

        t = time.time()-self.anim_stime  # Time since start of animation
        p = t/self.anim_duration  # Percentage of animation completed

        if p >= 1:
            # We are done with the animation, no need for further calculations
            self.anim_state = ANIM_STATE_DONE
            self.pos = tpos
            self.rot = trot

            self.redraw()
            return

        # Smoothstep copied from Wikipedia - https://en.wikipedia.org/wiki/Smoothstep
        p = p*p*(3-2*p)

        # Do a linear interpolation of all components of position and rotation
        self.pos = multi_interpolate(self.anim_frompos, tpos, p)
        self.rot = multi_interpolate(self.anim_fromrot, trot, p)

        self.redraw()

    def redraw(self):
        #self.layer.redraw()
        self.should_redraw = True

    def draw(self):
        if self.anim_state != "done":
            self.update_anim()

        if self.should_redraw:
            self.on_redraw()

            self.should_redraw = False

    def on_redraw(self):

        # First, set the texture coordinates
        self.texf = self.layer.peng.resourceMgr.getTex(self.get_texname(), "card")
        self.texb = self.layer.peng.resourceMgr.getTex(self.layer.get_backname(), "card")
        tf = self.texf[2]
        tb = self.texb[2]
        self.vlist_front.tex_coords = tf
        self.vlist_back.tex_coords = tb

        #if texf[1] != texb[1]:
        #    self.cg.warn(f"Front and back texture IDs for card {self.cardid} with value {self.value} do not match!")

        # Then, generate and set the vertices
        vf = self.get_vertices(0)
        vb = self.get_vertices(0.00002)  # 0.2mm

        self.vlist_front.vertices = vf
        self.vlist_pick.vertices = vf
        self.vlist_back.vertices = vb

    def get_card_pos_rot(self, slot: str, index: int, count: int = 1):
        # First, map virtual slots to physical slots
        slot = self.layer.norm_card_slot(slot)

        if slot == "stack":
            # TODO: Implement properly
            return [(index-count/2)*0.1, 0.01*index+0.2, 0.1], [0, 180, 0]
        elif slot == "table":
            # TODO: implement properly
            return [.5, 0.1+0.001*index, 0.1*index], [0, 180, 90]
        elif slot == "poverty":
            # TODO: implement properly
            return [-.5, index*0.05, 0], [0, 180, 0]
        elif slot == "player_self":
            pos, r = self.get_radial_pos_rot([0, 0.1, 4.5], index, count, 2, 180, 180, 3)
            return pos, [0, 180, r]
        elif slot == "player_left":
            pos, r = self.get_radial_pos_rot([-4.5, 0.1, 0], index, count, 2, 90, 180, 3)
            return pos, [0, 180, r]
        elif slot == "player_right":
            pos, r = self.get_radial_pos_rot([4.5, 0.1, 0], index, count, 2, 270, 180, 3)
            return pos, [0, 180, r]
        elif slot == "player_top":
            pos, r = self.get_radial_pos_rot([0, 0.1, -4.5], index, count, 2, 0, 180, 3)
            return pos, [0, 180, r]
        elif slot == "ptrick_self":
            # TODO: implement properly
            return [-2.5-0.1*index, 0.5+0.001*index, 0], [0, 180, 0]
        elif slot == "ptrick_left":
            # TODO: implement properly
            return [-2.5-0.1*index, 0.5+0.001*index, -1], [0, 180, 0]
        elif slot == "ptrick_right":
            # TODO: implement properly
            return [-2.5-0.1*index, 0.5+0.001*index, 1], [0, 180, 0]
        elif slot == "ptrick_top":
            # TODO: implement properly
            return [3.5+0.1*index, 0.5+0.001*index, 0], [0, 180, 0]
        else:
            self.cg.crash(f"Unknown card slot {slot}")

    def get_radial_pos_rot(self,
                           base: List[float],
                           index: int,
                           count: int,
                           angle_per_card: float,
                           base_angle: float,
                           max_angle: float,
                           radius: float,
                           ) -> Tuple[List[float], float]:
        if self.selected:
            radius += SELECTED_EXTENSION
        elif self.clicked:
            radius += CLICK_EXTENSION
        elif self.hovered:
            radius += HOVER_EXTENSION

        #if angle_per_card*count > max_angle:
            # Limits the "spread" of cards to a maximum angle
            # This prevents large amounts of cards from visually overflowing
        #    angle_per_card = max_angle/count

        # Calculate the effective angle of the card
        # Cards are arranged symmetrically around the base angle
        angle = base_angle + (index-count/2.)*angle_per_card
        rangle = math.radians(angle)

        #self.cg.info(f"Count: {count} Index: {index} Angle: {angle}")

        pos = [
            math.sin(rangle)*radius+base[0],
            base[1]+index*0.001,  # TODO: make this adjustable
            math.cos(rangle)*radius+base[2],
        ]

        return pos, angle

    def get_texname(self) -> str:
        if self.value == "":
            name = "unknown_front"
        elif self.value.startswith("j"):
            name = f"joker_{self.value[1]}"
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
        a_y = math.radians(self.rot[2])  # Angle along y axis in radians

        # Rotations are not "generic" and specifically optimized (for readability...) for
        # cards and how they are moved
        # The z axis is fixed to simplify the math. It is mainly used for card orientation
        # on screen
        # The long axis is used to flip cards
        # TODO: The short axis is currently not implemented

        # Generate and apply the y axis rotation matrix
        mz = rotation_matrix([0, 1, 0], a_y)
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
        self.vlist_back.delete()
        self.vlist_front.delete()
        self.vlist_pick.delete()


