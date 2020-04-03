#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  cg_ext.py
#  
#  Copyright 2020 notna <notna@apparat.org>
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

import sphinxcontrib
from sphinxcontrib.domaintools import custom_domain

# Monkeypatch for Python 3 compatibility
def get_objects(self):
        for (type, name), info in self.data['objects'].items():
            yield (name, name, type, info[0], info[1],
                   self.object_types[type].attrs['searchprio'])
sphinxcontrib.domaintools.CustomDomain.get_objects = get_objects

def setup(app):
    app.add_domain(custom_domain('cgDomain',
        name  = 'cg',
        label = "CardGame",

        elements = dict(
            event  = dict(
                objname = "cg Event",
                indextemplate = "pair: %s; cg Event",
            ),
            packet = dict(
                objname = "cg Packet",
                indextemplate = "pair: %s; cg Packet",
            ),
            dtype = dict(
                objname = "cg Data Type",
                indextemplate = "pair: %s; cg DataType",
            ),
            command = dict(
                objname = "cg Command",
                indextemplate = "pair: %s; cg Command",
            ),
            confval = dict(
                objname = "cg Config Value",
                indextemplate = "pair: %s; cg ConfigValue"
            ),
            permission = dict(
                objname = "cg Permission",
                indextemplate = "pair: %s; cg Permission"
            )
        )))
    return {"version":"1.0"}