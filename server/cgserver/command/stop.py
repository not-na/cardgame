#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  stop.py
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
"""
The ``stop`` command can be used to stop the server cleanly.

Usage
-----

The ``stop`` command is very simple, since it does not accept any arguments

Privileges
----------

It requires either a privilege level of ``1000`` or the permission :cg:perm:``cg:command.stop``\\ .
It can be run by any user meeting the privilege requirements at any time, though it may
cause games to be interrupted.

Examples
--------

Since it is so simple, there should be no examples necessary.

"""

import cg
import cgserver


class StopCommand(cgserver.command.Command):
    """
    Implementation of the ``stop`` command.

    See the module-level documentation for usage details.
    """
    min_privilege = 1000
    alt_permissions = ["cg:command.stop"]

    def get_help(self):
        return "Usage: stop"

    def get_description(self):
        return "stop\tStop the server"

    def run(self, ctx: cgserver.command.CommandContext, args: list):
        self.cg.info("Stop command received, stopping immediately")
        self.cg.send_event("cg:command.stop.do")
