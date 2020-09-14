#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  core.py
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
import collections
import logging as _logging
import os
import sys
import threading

from typing import Callable, Optional

import cg


class CardGame(object):
    client: Optional["cgclient.client.Client"]
    server: Optional["cgserver.server.DedicatedServer"]

    def __init__(self, instance_path, settings_path=None):
        self.instance_path = instance_path
        if settings_path is None:
            self.settings_path = cg.config.get_settings_path("cardgame")
        else:
            self.settings_path = settings_path
        # Ensure that the settings directory exists
        self.settings_path = os.path.abspath(self.settings_path)
        os.makedirs(self.settings_path, exist_ok=True)

        self.channel: str = "unknown"

        self._update_thread: Optional[threading.Thread] = None

        self._ev_queue = collections.deque()

        global c
        c = self
        cg.c = self

        # Define these here to prevent IDE from complaining
        self.client = None
        self.server = None

        self.config_manager = cg.config.ConfigManager(self)
        self.crash_reporter = cg.logging.CrashReporter(self)

        self.logger = _logging.getLogger(__name__)
        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warning = self.warn = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical
        self.exception = self.logger.exception
        self.log = self.logger.log
        self.debug("Initialized logging system")

        self.debug("Initializing event system")
        self.event_manager = cg.event.EventManager(self)
        self.debug("Initialized event system")

        self.register_event_handlers()

        self.debug("Calling core initialization callbacks")
        self.send_event("cg:core.initialized", {"cg": self})
        self.info(f"Settings path: {self.settings_path}")
        self.info("CG Core initialized")

    def get_config_option(self, key: str):
        return self.config_manager.get_config_option(key)

    def set_config_option(self, key: str, value):
        return self.config_manager.set_config_option(key, value)

    def get_version(self):
        if self.client is not None:
            import cgclient
            return cgclient.version.VERSION
        elif self.server is not None:
            import cgserver
            return cgserver.version.VERSION
        else:
            raise RuntimeError("Neither server or client have been initialized, version information is not available")

    def get_version_string(self):
        if self.client is not None:
            import cgclient
            return cgclient.version.VERSIONSTRING
        elif self.server is not None:
            import cgserver
            return cgserver.version.VERSIONSTRING
        else:
            raise RuntimeError("Neither server or client have been initialized, version information is not available")

    def get_proto_version(self):
        if self.client is not None:
            import cgclient
            return cgclient.version.PROTO_VERSION
        elif self.server is not None:
            import cgserver
            return cgserver.version.PROTO_VERSION
        else:
            raise RuntimeError("Neither server or client have been initialized, version information is not available")

    def get_semver(self):
        if self.client is not None:
            import cgclient
            return cgclient.version.SEMVER
        elif self.server is not None:
            import cgserver
            return cgserver.version.SEMVER
        else:
            raise RuntimeError("Neither server or client have been initialized, version information is not available")

    def send_event(self, event: str, data=None):
        return self.event_manager.send_event(event, data)

    def add_event_listener(self, event: str, func: Callable, flags=0, group=None):
        self.event_manager.add_event_listener(event, func, flags, group)

    def del_event_listener(self, event: str, func: Callable):
        self.event_manager.del_event_listener(event, func)

    def process_async_events(self):
        while len(self._ev_queue) > 0:
            event, data = self._ev_queue.popleft()
            self.send_event(event, data)

    def crash(self, msg: str, **kwargs):
        self.crash_reporter.generate_report(msg, **kwargs)

    def get_instance_path(self):
        return self.instance_path

    def get_settings_path(self, fname=None) -> str:
        if fname is None:
            return self.settings_path
        else:
            return os.path.join(self.settings_path, fname)

    def init_client(self, username=None, pwd=None, default_server=None):
        import cgclient

        self.info("Initializing client")
        self.client = cgclient.client.Client(self, username, pwd, default_server)
        self.client.init_gui()

    def init_server(self, addr=None):
        import cgserver

        self.info("Initializing Server")
        self.server = cgserver.server.DedicatedServer(self, addr)

        try:
            self.server.load_server_data()
        except Exception:
            self.error("Could not load saved server data, re-initializing everything")
            self.exception("Exception while loading saved server data: ")

        self.info("Initialized Server")

    def set_channel_from_file(self, fname):
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            # We are running from pyinstaller
            fname = os.path.join(sys._MEIPASS, fname)
        else:
            fname = os.path.abspath(fname)
        self.debug(f"Reading release channel from file {fname}")

        if not os.path.exists(fname):
            self.warn("Could not find release channel file, update-checker will not work")
            self.channel = "unknown"
            return

        with open(fname, "r") as f:
            channel = f.read().strip()

        self.channel = channel
        self.debug(f"Set release channel to {channel}")

        if self.channel == "dev":
            self.warning("Development build, expect bugs and stability issues")
        elif "beta" in self.channel:
            self.warning("Beta build, please mention this when reporting bugs")

    def check_for_updates(self):
        self._update_thread = threading.Thread(
            name="Update Checker",
            target=self._check_for_updates,
            daemon=True,
        )
        self._update_thread.start()

    def _check_for_updates(self):
        if self.channel == "dev":
            # dev channel is only ever local, skip update check
            self.warning("Skipping update check since we are a development build")
            self.send_async("cg:update.check_skipped", {"reason": "dev"})
            return

        if self.channel == "unknown":
            # unknown channel is skipped
            # TODO: maybe display a warning to the user here
            self.warning("Skipping update check since the channel is unknown")
            self.send_async("cg:update.check_skipped", {"reason": "unknown"})
            return

        latest = cg.util.itch.get_latest_version(self, self.channel)

        if latest is None:
            # update check failed
            # TODO: maybe display a warning to the user here
            self.error("Update check failed")
            self.send_async("cg:update.check_failed", {"reason": "unknown"})
            return

        if latest != self.get_semver():
            self.warning(f"New version {latest} found, please update")

            self.send_async("cg:update.available", {"cur": self.get_semver(), "latest": latest})
            return

        self.info(f"Update check succeeded, {latest} is the latest version of channel {self.channel}")
        self.send_async("cg:update.uptodate", {"latest": latest})

    def send_async(self, event, data):
        self._ev_queue.append((event, data))

    # Event Handlers

    def register_event_handlers(self):
        self.add_event_listener("cg:shutdown", self.handler_shutdown)

    def handler_shutdown(self, event: str, data: dict):
        _logging.shutdown()


c = None
