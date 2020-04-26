#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dev.py
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
import cgserver


class DevCommand(cgserver.command.Command):
    alt_permissions = ["cg:command.dev"]

    def get_help(self):
        return "Usage: dev"

    def get_description(self):
        return "dev\tI bet you'd like to know, wouldn't you? ;)"

    def run(self, ctx: cgserver.command.CommandContext, args: list):
        if len(args) < 4:
            ctx.output(f"The dev command takes at least 3 arguments, not {len(args) - 1}")
            return

        try:
            fake_player = int(args[1])
        except ValueError:
            ctx.output(f"The first argument (fake player) must be an integer, not {args[1]}")
            return

        command = args[2]
        choice = args[3]
        data = ""
        if len(args) >= 5:
            if command in ["solo", "poverty_return_trumps"] and len(args) == 5:
                data = args[4]
            elif command in ["poverty_trump_choice", "poverty_return_choice"]:
                if len(args) != 6:
                    ctx.output(f"The command '{command}' takes 5 arguments!")
                    return
                else:
                    data = args[3:]
            else:
                ctx.output(f"The command '{command}' only takes 3 arguments!")
                return

        if command == "reservation":
            if choice == "y":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation",
                    "player": fake_player,
                    "type": "reservation_yes"
                })
            elif choice == "n":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation",
                    "player": fake_player,
                    "type": "reservation_no"
                })

        elif command == "solo":
            if choice == "y":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_solo",
                    "player": fake_player,
                    "type": "solo_yes",
                    "data": data
                })
            elif choice == "n":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_solo",
                    "player": fake_player,
                    "type": "solo_no",
                })

        elif command == "throw":
            if choice == "y":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_throw",
                    "player": fake_player,
                    "type": "throw_yes",
                })
            elif choice == "n":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_throw",
                    "player": fake_player,
                    "type": "throw_no",
                })

        elif command == "pigs":
            if choice == "y":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_pigs",
                    "player": fake_player,
                    "type": "pigs_yes",
                })
            elif choice == "n":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_pigs",
                    "player": fake_player,
                    "type": "pigs_no",
                })

        elif command == "superpigs":
            if choice == "y":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_superpigs",
                    "player": fake_player,
                    "type": "superpigs_yes",
                })
            elif choice == "n":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_superpigs",
                    "player": fake_player,
                    "type": "superpigs_no",
                })

        elif command == "poverty":
            if choice == "y":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_poverty",
                    "player": fake_player,
                    "type": "poverty_yes",
                })
            elif choice == "n":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_poverty",
                    "player": fake_player,
                    "type": "poverty_no",
                })

        elif command == "poverty_accept":
            if choice == "y":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_poverty_accept",
                    "player": fake_player,
                    "type": "poverty_accept",
                })
            elif choice == "n":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_poverty_accept",
                    "player": fake_player,
                    "type": "poverty_decline",
                })

        elif command == "poverty_trump_choice":
            self.cg.send_event("cg:game.dk.command", {
                "packet": "reservation_poverty_pass_card",
                "player": fake_player,
                "type": "pass_card",
                "card": data
            })

        elif command == "poverty_return_choice":
            self.cg.send_event("cg:game.dk.command", {
                "packet": "reservation_poverty_pass_card",
                "player": fake_player,
                "type": "return_card",
                "card": data
            })

        elif command == "poverty_return_trumps":
            self.cg.send_event("cg:game.dk.command", {
                "packet": "reservation_poverty_accept",
                "player": fake_player,
                "type": "poverty_return",
                "data": choice
            })

        elif command == "wedding":
            if choice == "y":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_wedding",
                    "player": fake_player,
                    "type": "wedding_yes",
                })
            elif choice == "n":
                self.cg.send_event("cg:game.dk.command", {
                    "packet": "reservation_wedding",
                    "player": fake_player,
                    "type": "wedding_no",
                })

        elif command == "wedding_clarification_trick":
            self.cg.send_event("cg:game.dk.command", {
                "packet": "reservation_wedding_clarification_trick",
                "player": fake_player,
                "type": "wedding_clarification_trick",
                "data": choice
            })
