#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  accounts
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
The ``accounts`` command can be used to manage user accounts on the server.

Usage
-----

The ``accounts`` command supports multiple sub-commands.

First, the ``add`` subcommand can be used to add a user to the server. Its syntax is as
follows::

    /accounts add <username> <password> [uuid] [profile image]

The ``add`` subcommand can also be called as ``register``\\ .

.. note::
    No validation is performed on any of the parameters, allowing for creation of accounts
    with names that are normally not available.

The second subcommand is the ``delete`` or ``remove`` subcommand. It can be used to
permanently remove a user from the server. Note that any adjourned games with this user
in them will become unplayable, even if a new user registers using the same name. The syntax
is as follows::

    /accounts delete <username>

The third subcommand is the ``list`` subcommand. It can be used to view all or a subset of
all registered accounts. The syntax is as follows::

    /accounts list [pattern]

Another subcommand is the ``block`` (and ``unblock``\\ ) subcommand. These subcommands can
be used to temporarily block users from accessing the server. Note that blocking a logged in
user does not kick them automatically, see the ``/kick`` command for that. The syntax is as follows::

    /accounts block <username>
    /accounts unblock <username>

Further subcommands may be added in the future.

Privileges
----------

It requires either a privilege level of ``1000`` or the permission :cg:perm:``cg:command.accounts``\\ .
It can be run by any user meeting the privilege requirements at any time, though it may
cause games to be interrupted and/or data to be lost.

Examples
--------

.. todo::
   Write this section

"""
import re
import uuid

import cg
import cgserver

from cg.util import uuidify


class AccountsCommand(cgserver.command.Command):
    """
    Implementation of the ``accounts`` command.

    See the module-level documentation for usage details.
    """
    min_privilege = 1000
    alt_permissions = ["cg:command.accounts"]

    def get_help(self):
        return "Usage: accounts add <username> <pwd> [uuid] [profile img]\n\t\taccounts delete <username>"

    def get_description(self):
        return "accounts\tManage accounts"

    def run(self, ctx: cgserver.command.CommandContext, args: list):
        if len(args) == 1:
            # No args, just the command
            ctx.output("A subcommand is required for the accounts command")
            return

        if args[1] in ["add", "register"]:
            if len(args) not in [4, 5, 6]:
                ctx.output(f"The accounts add command requires between 2 and 4 parameters, not {len(args)-2}")
                return

            username = args[2]
            password = args[3]
            if len(args) >= 5:
                uid = uuidify(args[4])
            else:
                uid = uuid.uuid4()
            if len(args) >= 6:
                profile_img = args[5]
            else:
                profile_img = "default"

            self.cg.info(f"Creating new account with name '{username}'")
            u = cgserver.user.User(self.cg.server, self.cg, username, {
                "pwd": password,
                "uuid": uid,
                "profile_img": profile_img,
            })
            self.cg.server.users[username.lower()] = u
            self.cg.server.users_uuid[u.uuid] = u

            self.cg.server.save_server_data()

            self.cg.send_event("cg:network.client.register", {"client": -1})
            ctx.output(f"Successfully created new account {username}")
        elif args[1] in ["delete", "remove"]:
            # TODO: implement account removal
            ctx.output("Account deletion is currently not implemented")
            return
        elif args[1] in ["list"]:
            if len(args) >= 3:
                pattern = re.compile(args[2])
            else:
                pattern = re.compile(".*")

            for u in self.cg.server.users_uuid.values():
                if pattern.fullmatch(u.username):
                    # TODO: add more info here
                    # Prints out basic information about the user
                    ctx.output(f"{u.username} ({u.uuid})")
            else:
                ctx.output(f"No users matched the given query!")
        elif args[1] in ["block"]:
            if len(args) != 3:
                ctx.output("Subcommand 'block' needs exactly one parameter!")
                return

            username = args[2].lower()
            if username not in self.cg.server.users:
                ctx.output(f"Username {username} does not belong to any user account!")
                return

            u = self.cg.server.users[username]
            if u.uuid.hex in self.cg.server.settings["blocklist"]:
                ctx.output("User is already blocked")
                return

            self.cg.server.settings["blocklist"].append(u.uuid.hex)
            ctx.output(f"Blocked account {u.username}")
            self.cg.server.save_settings()
        elif args[1] in ["unblock"]:
            if len(args) != 3:
                ctx.output("Subcommand 'unblock' needs exactly one parameter!")
                return

            username = args[2].lower()
            if username not in self.cg.server.users:
                ctx.output(f"Username {username} does not belong to any user account!")
                return

            u = self.cg.server.users[username]
            if u.uuid.hex not in self.cg.server.settings["blocklist"]:
                ctx.output("User is already unblocked")
                return

            self.cg.server.settings["blocklist"].remove(u.uuid.hex)
            ctx.output(f"Unblocked account {u.username}")
            self.cg.server.save_settings()
        else:
            # TODO: add more subcommands to allow changing an account
            # e.g. pwd resets and so on
            ctx.output(f"Invalid subcommand '{args[1]}' for the accounts command")
            return
