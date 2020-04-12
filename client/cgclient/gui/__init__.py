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

import peng3d
import peng3dnet
import pyglet
from pyglet.gl import *

import cg
import cgclient

from . import loadingscreen
from . import serverselect
from . import servermain
from . import custombuttons


class PengGUI(object):
    loadingscreen: loadingscreen.LoadingScreenMenu
    serverselect: serverselect.ServerSelectMenu
    servermain: servermain.ServerMainMenu

    def __init__(self, client, c: cg.CardGame):
        self.client = client
        self.cg = c

        self.run = False

        self.peng = peng3d.Peng()
        self.peng.cg = self.cg

        self.peng.cfg["rsrc.maxtexsize"] = 4096
        self.peng.cfg["graphics.clearColors"] = 1.0, 1.0, 0.0, 1.0

        self.window = self.peng.createWindow(
            width=self.cg.get_config_option("cg:graphics.resolution.width"),
            height=self.cg.get_config_option("cg:graphics.resolution.height"),
            caption_t="cg:window.caption",
            resizable=True,
            vsync=self.cg.get_config_option("cg:graphics.vsync"),
            fullscreen=self.cg.get_config_option("cg:graphics.fullscreen"),
        )
        self.window.maximize()

        self.peng.resourceMgr.addCategory("gui")
        self.peng.resourceMgr.addCategory("bg")

        self.peng.resourceMgr.categoriesSettings["gui"]["minfilter"] = GL_NEAREST

        self.peng.resourceMgr.loadTex("cg:img.cursor.cursor20p", "gui")
        self.window.set_mouse_cursor(pyglet.window.ImageMouseCursor(
            self.peng.resourceMgr.categories["gui"]["cg:img.cursor.cursor20p"], 0, 20
        ))

        #pyglet.clock.set_fps_limit(self.cg.get_config_option("cg:graphics.fps"))
        pyglet.clock.schedule_interval(self.update, 1 / 60)

        self.t = self.peng.t
        self.tl = self.peng.tl

        self.register_event_handlers()

    def init(self):
        self.register_menus()

    def register_menus(self):
        self.loadingscreen = loadingscreen.LoadingScreenMenu(
            "loadingscreen",
            self.window, self.peng, self,
        )
        self.window.addMenu(self.loadingscreen)

        self.serverselect = serverselect.ServerSelectMenu(
            "serverselect",
            self.window, self.peng, self,
        )
        self.window.addMenu(self.serverselect)

        self.servermain = servermain.ServerMainMenu(
            "servermain",
            self.window, self.peng, self,
        )
        self.window.addMenu(self.servermain)

        # Change to loadingscreen after everything is initialized
        self.window.changeMenu("loadingscreen")

    def update(self, dt=None):
        if self.window.menu.name == "loadingscreen":
            self.window.changeMenu("serverselect")

        if self.client._client is not None:
            self.client._client.process()

    def start_main_loop(self):
        self.run = True
        self.peng.run()

    # Event Handlers

    def register_event_handlers(self):
        self.cg.add_event_listener("cg:shutdown.do", self.handler_shutdowndo)

        self.peng.addEventListener("peng3d:i18n.miss", self.handler_i18nmiss)

    def handler_shutdowndo(self, event: str, data: dict):
        pyglet.app.exit()

    def handler_i18nmiss(self, event: str, data: dict):
        self.cg.debug(f"Missing i18n key {data['key']} for language {data['lang']}")
