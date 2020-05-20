#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  help.py
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
The ``help`` command can be used to both display a list of available commands as
well as their basic usage.

Usage
-----

The ``help`` command has three different signatures.

If it is executed without any argument, it is equivalent to running ``help 1``\\ ,
displaying the first help overview page.

If it is executed with a number as its first argument, the appropriate help overview
page is shown. The number of commands per page is determined by the constant
:py:data:`COMMANDS_PER_PAGE` which defaults to ``5``\\ .

It it is executed with a word as its first argument, the long description of that
command is shown. This description will usually include the basic usage and signature
of the command.

Privileges
----------

It requires either a privilege level of ``100`` or the permission :cg:permission:`cg:command.help`
and can be run by any user at any time. The results will only be displayed to the calling user.

Examples
--------

Following below are some examples illustrating how to use the ``help`` command.

.. todo::
   Write this section when more commands are implemented, to use them as examples.
"""

import re

import cg
import cgserver

NUM_REGEX = re.compile("[0-9]+")
"""
Regular expression used to match help page numbers.

It is pre-compiled here to increase performance when parsing commands.

The regular expression defaults to ``[0-9]+``\\ .
"""

COMMANDS_PER_PAGE = 5
"""
Determines how many commands should be shown per page.

This constant defaults to ``5``\\ .
"""


class HelpCommand(cgserver.command.Command):
    """
    Implementation of the ``help`` command.

    See the module-level documentation for usage details.
    """

    alt_permissions = ["cg:command.help"]

    def get_help(self):
        return "Usage: help [page]\n\t\thelp <command>"

    def get_description(self):
        return "help\tPrints a quick reference"

    def run(self, ctx: cgserver.command.CommandContext, args: list):
        out = ""

        mode = "page"
        page = 1
        cmd = "help"

        if len(args) == 1:
            # No arguments, only the command itself
            mode = "page"
            page = 1
        elif len(args) == 2 and NUM_REGEX.match(args[1]):
            mode = "page"
            page = int(args[1])
        elif len(args) == 2:
            mode = "cmdhelp"
            cmd = args[1]
        else:
            ctx.output(f"The help command only takes either one or zero arguments, not {len(args)-1}")
            return

        if mode == "page":
            allcmds = list(self.cg.server.command_manager.commands.keys())

            for cmd in allcmds[:]:
                if not self.cg.server.command_manager.commands[cmd].get_description():
                    del allcmds[allcmds.index(cmd)]  # Only deletes the command locally

            cmds = allcmds[(page-1)*COMMANDS_PER_PAGE:page*COMMANDS_PER_PAGE]
            maxhelppage = int((len(allcmds)-1)/COMMANDS_PER_PAGE)+1

            if page < 1 or page > maxhelppage:
                ctx.output("Invalid help page")
                return
            elif page != maxhelppage:
                out += f"Help Page {page}/{maxhelppage}, type help {page+1} for next page"
            else:
                out += f"Help Page {page}/{maxhelppage}"

            for cmd in cmds:
                out += "\n" + self.cg.server.command_manager.commands[cmd].get_description()

            ctx.output(out)
        elif mode == "cmdhelp":
            if cmd not in self.cg.server.command_manager.commands:
                ctx.output(f"Command {cmd} could not be found")
                return
            elif not self.cg.server.command_manager.commands[cmd].get_help():
                ctx.output(f"Command {cmd} has no help")
                return

            out += f"Help for command {cmd}:\n"
            out += self.cg.server.command_manager.commands[cmd].get_help()

            ctx.output(out)
