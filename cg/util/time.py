#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  time.py
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
import time

SMART_FORMAT = "%x"


def tdiff_format(t1, t2=None):
    # TODO: support translation
    # t1 is the older time
    # t2 is now
    if t2 is None:
        t2 = time.time()

    tdiff = t1-t2
    if tdiff == 0:
        return "right now"
    elif tdiff < 0:
        # in the past
        tdiff = -tdiff
        t_m = int(tdiff / 60)
        t_h = int(tdiff / 60 / 60)  # hours
        t_d = int(tdiff / 60 / 60 / 24)
        t_w = int(tdiff / 60 / 60 / 24 / 7)  # weeks
        t_y = int(tdiff / 60 / 60 / 24 / 365)  # years; TODO: leap years...

        if tdiff < 10:
            return "a few seconds ago"
        elif t_m < 1:
            return f"{int(tdiff)} seconds ago"
        elif t_m == 1:
            return "a minute ago"
        elif t_h < 1:
            return f"{t_m} minutes ago"
        elif t_h == 1:
            return "an hour ago"
        elif t_d < 1:
            return f"{t_h} hours ago"
        elif t_d == 1:
            return "yesterday"
        elif t_w < 1:
            return f" {t_d} days ago"
        elif t_w == 1:
            return "last week"
        elif t_y < 1:
            return f"{t_w} weeks ago"
        elif t_y == 1:
            return "a year ago"
        elif t_y == 10:
            return "a decade ago"
        elif t_y == 100:
            return "a century ago"
        elif t_y == 1000:  # Let's hope python still exists then
            return "a millennium ago"
        else:
            return f"{t_y} years ago"

    elif tdiff > 0:
        # in the future
        raise NotImplementedError("Times in the future cannot yet be formatted")

    return "error"


def tdiff_format_smart(t1, t2=None, p_abs="", p_rel=""):
    if t2 is None:
        t2 = time.time()

    if t1 > t2:
        raise NotImplementedError("Smart formatting only supports past dates")

    tdiff = t2 - t1

    if tdiff < (60 * 60 * 24 * 7):  # week
        return p_rel + tdiff_format(t1, t2)
    else:
        return p_abs + time.strftime(SMART_FORMAT, time.localtime(t1))