#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  doppelkopf.py
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
from game import CGame


class DoppelkopfGame(CGame):
    GAMERULES = {
        "general.wrongmove": {
            "type": "select",
            "default": "prohibit",
            "options": [
                "prohibit",
                "allow_points",
                "allow_stopgame",
            ],
            "requirements": {},
        },
        "dk.heart10": {
            "type": "bool",
            "default": True,
            "requirements": {},
        },
        "dk.heart10_prio": {
            "type": "select",
            "default": "first",
            "options": [
                "first",
                "second",
            ],
            "requirements": {
                "dk.heart10": [True],
            },
        },
        "dk.heart10_lasttrick": {
            "type": "select",
            "default": "first",
            "options": [
                "first",
                "second",
            ],
            "requirements": {
                "dk.heart10": [True],
            },
        },
        "dk.doppelkopf": {
            "type": "bool",
            "default": True,
            "requirements": {},
        },
        "dk.fox": {
            "type": "bool",
            "default": True,
            "requirements": {},
        },
        "dk.fox_lasttrick": {
            "type": "bool",
            "default": False,
            "requirements": {
                "dk.fox": [True],
            },
        },
        "dk.pigs": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "one_first",
                "one_on_play",
                "one_on_fox",
                "two_reservation",
                "two_on_play",
            ],
            "requirements": {
                "dk.fox": [True],
            },
        },
        "dk.superpigs": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "reservation",  # dk.pigs: two_reservation
                "on_pig",
                "on_play",
            ],
            "requirements": {
                "dk.fox": [True],
                "dk.pigs": ["two_reservation", "two_on_play"],
            },
        },
        "dk.charlie": {
            "type": "bool",
            "default": True,
            "requirements": {},
        },
        "dk.charlie_broken": {
            "type": "bool",
            "default": False,
            "requirements": {
                "dk.charlie": [True],
            },
        },
        "dk.jane": {  # Lieschen Müller
            "type": "bool",
            "default": False,
            "requirements": {
                "dk.charlie": [True],
                "dk.charlie_broken": [True],
            },
        },
        "dk.charlie_prio": {
            "type": "select",
            "default": "first",
            "options": [
                "first",
                "second",
            ],
            "requirements": {
                "dk.charlie": [True],
            },
        },
        "dk.without9": {
            "type": "select",
            "default": "with_all",
            "options": [
                "with_all",
                "with_four",
                "without",
            ],
            "requirements": {},
        },
        "dk.heart_trick": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.sec_black_trick": {
            "type": "bool",
            "default": False,
            "requirements": {
                "dk.without9": ["with_all"],
            },
        },
        "dk.joker": {
            "type": "select",
            "default": "None",
            "options": [
                "over_h10",  # dk.heart10: True
                "over_pigs",  # dk.pigs: not None
                "over_superpigs",  # dk.superpigs: not None
            ],
            "requirements": {},
        },
        "dk.hobgoblin": {  # Klabautermann
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.poverty": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "sell",
                "circulate",
                "circulate_duty",
            ],
            "requirements": {},
        },
        "dk.poverty_no_partner": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "black_sow",
                "ramsch",
            ],
        },
        "dk.throw": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "reservation",
                "throw",
            ]
        },
        "dk.throw_cases": {
            "type": "active",
            "default": [],
            "options": [
                "5_9",
                "5_k",
                "4_9+4_k",
                "9_all_c",
                "k_all_c",
                "7full",
                "t<=jd",
                "t<=ad"
            ],
            "requirements": {
                "dk.throw": ["reservation", "throw"],
            },
        },
        "dk.coward": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "210_no_re",
                "240_no_u90",
            ],
            "requirements": {},
        },
        "dk.wedding": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "3_trick",
                "wish_trick",
            ],
            "requirements": {},
        },
        "dk.repeat_game": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.re_kontra": {
            "type": "select",
            "default": "+2",
            "options": [
                "+2",
                "*2",
                "*2_extra"
            ],
            "requirements": {},
        },
        "dk.knock": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.buck_round": {
            "type": "select",
            "default": "None",
            "options": [
                "None",
                "succession",
                "parallel",
            ],
            "requirements": {},
        },
        "dk.buck_cause": {
            "type": "active",
            "default": [],
            "options": [
                "4hearts",
                "draw",
                "0points",  # repeat_game: False
                "re_kontra_lost",
                "solo_lost",
            ],
            "requirements": {
                "dk.buck_round": ["succession", "parallel"],
            },
        },
        "dk.solo_shift_h10": {
            "type": "bool",
            "default": False,
            "requirements": {
                "dk.heart10": [True],
            },
        },
        "dk.solo.null": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.pure_color": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.king": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.brothel": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.noble_brothel": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.picture": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.monastery": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.10s": {
            "type": "bool",
            "default": False,
            "requirements": {},
        },
        "dk.solo.9s": {
            "type": "bool",
            "default": False,
            "requirements": {
                "dk.without9": ["with_all"]
            },
        },
    }

    def start(self):
        pass

    def register_event_handlers(self):
        super().register_event_handlers()

        # Add event handler registration here

