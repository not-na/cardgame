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
import uuid

import peng3d

import cg

import pyglet
from pyglet.gl import *

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

class Card(object):
    def __init__(self,
                 c: cg.CardGame,
                 layer: peng3d.Layer,
                 slot: str,
                 cardid: uuid.UUID, value: str,
                 ):

        self.cg = c

        self.layer: peng3d.Layer = layer

        self.slot: str = slot
        self.cardid: uuid.UUID = cardid
        self.value: value = value

        self.should_redraw: bool = True

    def on_transfer(self, new_slot: str):
        pass

    def redraw(self):
        self.should_redraw = True

    def do_redraw(self):
        if self.should_redraw:
            self.on_redraw()

    def on_redraw(self):
        pass

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


