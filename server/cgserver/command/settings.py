#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  settings
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
The ``settings`` command can be used to get and set various settings on the server.

Usage
-----

The general syntax of this command is as follows::

    /settings <key> [value]

If no value is given, the current value will be shown. Otherwise, the new value will be
set. Valid values depend on the given key.

Available Keys
''''''''''''''

``name`` is the *internal* name of the server. It is usually not shown to the user.
All strings are valid for this key, though spaces and special characters should be avoided.

``visiblename`` is the *visible* name of the server. This is the name shown to users in
the server list. All strings are valid for this key, including special characters.
Note that some clients may not be able to render some characters, especially emojis.

``allow_new_accounts`` determines whether or not new accounts may be created. Only ``true``
and ``false`` are allowed.

``max_players`` limits the amount of players that can be connected simultaneously. Only
positive integers are allowed.

``slogan`` is the text shown below the name of the server. While it can be multiple lines,
this command interface currently only supports single-line slogans. All strings are valid here.

More keys may be added in the future.

Privileges
----------

It requires either a privilege level of ``1000`` or the permission :cg:perm:``cg:command.settings``\\ .
It can be run by any user meeting the privilege requirements at any time, though it may
cause games to be interrupted and/or data to be lost.

Examples
--------

.. todo::
   Write this section

"""

import cg
import cgserver

from cg.util import uuidify


class SettingsCommand(cgserver.command.Command):
    """
    Implementation of the ``settings`` command.

    See the module-level documentation for usage details.
    """
    min_privilege = 1000
    alt_permissions = ["cg:command.settings"]

    def get_help(self):
        return "Usage: settings <key> [value]"

    def get_description(self):
        return "settings\tManage settings"

    def run(self, ctx: cgserver.command.CommandContext, args: list):
        if len(args) == 1:
            # No args, just the command
            ctx.output("At least a key is required for the settings command")
            return
        elif len(args) == 2:
            # Show settings value
            k = args[1].lower()
            o = "<ERROR>"
            if k == "name":
                o = self.cg.server.settings["name"]
            elif k == "visiblename":
                o = self.cg.server.settings["visiblename"]
            elif k == "allow_new_accounts":
                o = self.cg.server.settings["allow_new_accounts"]
                if o:
                    o = "true"
                else:
                    o = "false"
            elif k == "max_players":
                o = str(self.cg.server.settings["max_players"])
            elif k == "slogan":
                o = self.cg.server.settings["slogan"]
            else:
                ctx.output(f"Invalid settings key '{k}'")
                return

            ctx.output(f"{k}: {o}")
        else:
            # Set settings value
            k = args[1].lower()
            v = " ".join(args[2:])
            if k == "name":
                self.cg.server.settings["name"] = v
            elif k == "visiblename":
                self.cg.server.settings["visiblename"] = v
            elif k == "allow_new_accounts":
                if v.lower() == "true":
                    self.cg.server.settings["allow_new_accounts"] = True
                elif v.lower() == "false":
                    self.cg.server.settings["allow_new_accounts"] = False
                else:
                    ctx.output(f"Invalid settings value for allow_new_accounts")
                    return
            elif k == "max_players":
                try:
                    v = int(v)
                except ValueError:
                    ctx.output("Invalid settings value for max_players (could not decode int)")
                    return
                if v < 0:
                    ctx.output("Invalid settings value for max_player (must be positive)")
                    return

                self.cg.server.settings["max_players"] = v
            elif k == "slogan":
                # TODO: implement multi-line slogans
                self.cg.server.settings["slogan"] = v
            else:
                ctx.output(f"Invalid settings key '{k}'")

            self.cg.server.save_settings()
            ctx.output(f"Successfully set setting '{k}'")
