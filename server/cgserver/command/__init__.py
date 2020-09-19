#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
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

import abc
import collections
import sys
from typing import OrderedDict

import cg
import cg.error

import cgserver
#import cgserver.user


class CommandContext(object, metaclass=abc.ABCMeta):
    """
    Abstract basic command context.

    A command context is always required when executing a command. It decides where
    the output is directed and to check privileges. It may also be used by commands
    to e.g. perform an action on the calling user.

    This class cannot be instantiated and used directly, since some of its methods are
    abstract. One should should subclass this class and implement them properly before
    usage.
    """
    def __init__(self, c: cg.CardGame):
        self.cg = c

    @abc.abstractmethod
    def output(self, msg: str) -> None:
        """
        Called when output should be displayed or otherwise be given back to this context.

        Note that the message may contain one or more lines. Lines will always be separated
        by ``\\n`` newlines, never ``\\r``\\ .

        :param str msg: String containing the output
        :return: None
        """
        pass

    @abc.abstractmethod
    def has_permission(self, name: str) -> bool:
        """
        Called to check whether a permission has been granted within the context.

        Permissions are of the usual ``<domain>:<category>.<subcategory>.<item>`` form.
        For example, chat permissions take the form ``cg:chat.<channel>.<right>``\\ .

        For maximum access, it is allowed for this method to always return ``True``\\ .

        :param str name: Name of the permission in question
        :return: bool
        """
        pass

    @abc.abstractmethod
    def get_privilege_level(self) -> int:
        """
        Gets the numerical privilege level granted by this context.

        Bigger numbers mean more privileges.

        Usually, new users will have a privilege level of ``100`` and administrators
        ``1000``\\ .

        :return: int describing the privilege level
        """
        pass


class LocalCommandContext(CommandContext):
    def output(self, msg: str) -> None:
        for line in msg.strip().split("\n"):
            self.cg.info(f"[Console] {line}")

    def has_permission(self, name: str) -> bool:
        return True

    def get_privilege_level(self) -> int:
        return 2**31-1


class Command(object, metaclass=abc.ABCMeta):
    min_privilege: int = 100
    alt_permissions: list = []

    def __init__(self, c: cg.CardGame):
        self.cg = c

    @abc.abstractmethod
    def get_help(self):
        pass

    @abc.abstractmethod
    def get_description(self):
        pass

    @abc.abstractmethod
    def run(self, ctx: CommandContext, args: list):
        pass


class CommandManager(object):
    local_ctx: CommandContext

    def __init__(self, c: cg.CardGame):
        self.cg = c

        self.commands: OrderedDict[str, Command] = collections.OrderedDict()

        self.local_ctx = LocalCommandContext(self.cg)

        self.register_default_commands()

    def register_default_commands(self):
        import cgserver.command.help
        self.register_command("help", cgserver.command.help.HelpCommand(self.cg))

        import cgserver.command.stop
        self.register_command("stop", cgserver.command.stop.StopCommand(self.cg))

        import cgserver.command.accounts
        self.register_command("accounts", cgserver.command.accounts.AccountsCommand(self.cg))

        import cgserver.command.settings
        self.register_command("settings", cgserver.command.settings.SettingsCommand(self.cg))

        if cgserver.game.CGame.DEV_MODE:
            import cgserver.command.dev
            self.register_command("dev", cgserver.command.dev.DevCommand(self.cg))

        # TODO: implement more commands, like perf

    def register_command(self, command: str, obj: Command) -> None:
        self.commands[command] = obj

        self.cg.send_event("cg:command.register", {"command": command, "obj": obj})
        self.cg.send_event(f"cg:command.register.{command}", {"command": command, "obj": obj})

    def del_command(self, command: str) -> None:
        del self.commands[command]

        self.cg.send_event("cg:command.remove", {"command": command})
        self.cg.send_event(f"cg:command.remove.{command}", {"command": command})

    def exec_command(self, command: str, ctx: CommandContext) -> None:
        cmds = command.split(" ")[0]
        if cmds not in self.commands:
            ctx.output(f"Command {cmds} could not be found!")
            return

        cmd = self.commands[cmds]
        args = command.split(" ")

        if ctx.get_privilege_level() < cmd.min_privilege \
                and not any([ctx.has_permission(p) for p in cmd.alt_permissions]):
            ctx.output(f"Command {cmds} requires either a privilege of at least {cmd.min_privilege}"
                       f"or special permissions")
            return

        try:
            cmd.run(ctx, args)
            self.cg.send_event("cg:command.exec", {"command": cmds, "ctx": ctx, "args": args})
            self.cg.send_event(f"cg:command.exec.{command}", {"command": cmds, "ctx": ctx, "args": args})
        except Exception:
            self.cg.exception(f"Exception occured during execution of command {cmds}:")
            ctx.output("Error while running command")
