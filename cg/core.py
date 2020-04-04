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

import logging as _logging

from typing import Callable

import cg


class CardGame(object):
    def __init__(self, instance_path):
        self.instance_path = instance_path

        global c
        c = self
        cg.c = self

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
        self.info("CG Core initialized")

    def get_config_option(self, key: str):
        return self.config_manager.get_config_option(key)

    def set_config_option(self, key: str, value):
        return self.config_manager.set_config_option(key, value)

    @staticmethod
    def get_version():
        return cg.version.VERSION

    @staticmethod
    def get_version_string():
        return cg.version.VERSIONSTRING

    @staticmethod
    def get_proto_version():
        return cg.version.PROTO_VERSION

    def send_event(self, event: str, data=None):
        return self.event_manager.send_event(event, data)

    def add_event_listener(self, event: str, func: Callable, flags=0):
        self.event_manager.add_event_listener(event, func, flags)

    def del_event_listener(self, event: str, func: Callable):
        self.event_manager.del_event_listener(event, func)

    def crash(self, msg: str, **kwargs):
        self.crash_reporter.generate_report(msg, **kwargs)

    def get_instance_path(self):
        return self.instance_path

    def init_client(self, username=None, pwd=None, default_server=None):
        import cgclient

        self.info("Starting client")
        #self.client = cgclient.client.Client(self, username, pwd, default_server)
        #self.client.init_gui()

    # Event Handlers

    def register_event_handlers(self):
        self.add_event_listener("cg:shutdown", self.handler_shutdown)

    def handler_shutdown(self, event: str, data: dict):
        _logging.shutdown()


c = None
