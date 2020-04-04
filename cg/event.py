#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  event.py
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
import os
from typing import Callable, Dict

REMOVE_ERRHANDLER = True
MAX_IGNORE = 3  # Only outputs debug messages this many times for unhandled events

F_RAISE_ERRORS = 1 << 0
F_REMOVE_ONERROR = 1 << 1
F_SILENT = 1 << 2


class EventManager(object):
    def __init__(self, cg):
        self.cg = cg

        self.event_handlers = {}
        self.handler_flags = {}
        self.ignored = {}

        self.event_list = set()

        self.add_event_listener("cg:shutdown", self.handle_shutdown)

    def send_event(self, event, data=None):
        if data is None:
            data = {}

        if self.cg.get_config_option("cg:debug.event.dump_file") != "" and event not in self.event_list:
            self.cg.debug(f"Found event {event}")
            self.event_list.add(event)

        if event not in self.event_handlers:
            if event not in self.ignored or self.ignored[event] <= MAX_IGNORE:
                # Prevents spamming logging with repeated unhandled messages
                self.cg.debug(f"Ignored event of type {event} because there were no handlers registered for this event")
                self.ignored[event] = self.ignored.get(event, 0) + 1
            return

        for handler in self.event_handlers[event]:
            flags = self.handler_flags[(event, handler)]
            try:
                handler(event, data)  # Call the event handler
            except Exception:
                if flags & F_RAISE_ERRORS:  # raise_errors parameter
                    raise
                elif not (flags & F_SILENT):
                    self.cg.info(f"Ignored error raised by event handler {handler} of event {event}")
                elif flags & F_REMOVE_ONERROR:
                    self.del_event_listener(event, handler)

    def add_event_listener(self, event: str, func: Callable[[str, Dict], None], flags=0):
        if not isinstance(event, str):
            raise TypeError("Event types must always be strings")

        if not (flags & F_SILENT)\
                and self.cg.get_config_option("cg:debug.event.dump_file") != ""\
                and event not in self.event_list:
            self.cg.debug(f"Found event listener {event}")
            self.event_list.add(event)

        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.handler_flags[(event, func)] = flags
        self.event_handlers[event].append(func)

    def del_event_listener(self, event: str, func: Callable):
        if event not in self.event_handlers:
            raise NameError(f"No handlers exist for event {event}")

        if func in self.event_handlers[event]:
            del self.event_handlers[event][self.event_handlers[event].index(func)]
            del self.handler_flags[(event, func)]
        else:
            raise NameError(f"This handler is not registered for event {event}")

        if not self.event_handlers[event]:
            # Clean up empty event handlers to prevent memory leaks
            del self.event_handlers[event]

    def handle_shutdown(self, event: str, data: dict):
        if self.cg.get_config_option("cg:debug.event.dump_file") != "":
            with open(
                    os.path.join(self.cg.get_instance_path(),
                                 self.cg.get_config_option("cg:debug.event.dump_file")
                                 ),
                    "w"
                    ) as f:
                f.write("\n".join(sorted(list(self.event_list))))
