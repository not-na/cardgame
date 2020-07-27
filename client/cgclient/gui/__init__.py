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

import functools
import glob
import os
import re
import ctypes
import platform

import peng3d
import peng3dnet
import pyglet
from pyglet.gl import *

import cg
import cgclient

from . import card

from . import loadingscreen
from . import serverselect
from . import servermain
from . import settings
from . import ingame

SHOW_FPS = True

DEFAULT_LANGUAGE = "de"

# Some partial class substitutions to allow easy creation of standardised buttons and text inputs
CGTextInput = functools.partial(peng3d.gui.TextInput,
                                parent_bgcls=peng3d.gui.button.FramedImageBackground,
                                bg_idle=("cg:img.btn.fld_idle", "gui"),
                                bg_hover=("cg:img.btn.fld_hov", "gui"),
                                bg_pressed=("cg:img.btn.fld_press", "gui"),
                                frame=[
                                    [150, 700, 150],
                                    [0, 1, 0],
                                ],
                                repeat_edge=True,
                                repeat_center=True,
                                scale=[None, 0],
                                border=[6, 0],
                                )

CGPasswordInput = functools.partial(peng3d.gui.PasswordInput,
                                parent_bgcls=peng3d.gui.button.FramedImageBackground,
                                bg_idle=("cg:img.btn.fld_idle", "gui"),
                                bg_hover=("cg:img.btn.fld_hov", "gui"),
                                bg_pressed=("cg:img.btn.fld_press", "gui"),
                                frame=[
                                    [150, 700, 150],
                                    [0, 1, 0],
                                ],
                                repeat_edge=True,
                                repeat_center=True,
                                scale=[None, 0],
                                border=[6, 0],
                                )

CGButton = functools.partial(peng3d.gui.FramedImageButton,  # Button like on the titlescreen
                             bg_idle=("cg:img.btn.btn_idle", "gui"),
                             bg_hover=("cg:img.btn.btn_hov", "gui"),
                             bg_pressed=("cg:img.btn.btn_press", "gui"),
                             bg_disabled=("cg:img.btn.btn_disabled", "gui"),
                             frame=[[1, 2, 1], [0, 1, 0]],
                             scale=(None, 0),
                             repeat_edge=True, repeat_center=True,
                             )

CGButtonBG = functools.partial(peng3d.gui.FramedImageBackground,  # Button like on the titlescreen
                               bg_idle=("cg:img.btn.btn_idle", "gui"),
                               bg_hover=("cg:img.btn.btn_hov", "gui"),
                               bg_pressed=("cg:img.btn.btn_press", "gui"),
                               bg_disabled=("cg:img.btn.btn_disabled", "gui"),
                               frame=[[1, 2, 1], [0, 1, 0]],
                               scale=(None, 0),
                               repeat_edge=True, repeat_center=True,
                               )


class PengGUI(object):
    CG_APPID = "cg.cg.cardgame.1"

    # Types are hinted here to allow for better autocompletion elsewhere
    # Since the menus are not created in the constructor
    loadingscreen: loadingscreen.LoadingScreenMenu
    serverselect: serverselect.ServerSelectMenu
    servermain: servermain.ServerMainMenu
    settings: settings.SettingsMenu
    ingame: ingame.IngameMenu

    def __init__(self, client, c: cg.CardGame):
        self.client = client
        self.cg = c

        self.run = False

        # Initialize our Peng singleton
        self.peng = peng3d.Peng()
        self.peng.cg = self.cg

        # TODO: add dynamic max texture size
        self.peng.cfg["rsrc.maxtexsize"] = 4096
        # Set the clear color to a easily recognizable color to ensure we see it if it leaks through somewhere
        self.peng.cfg["graphics.clearColor"] = (1.0, 0.0, 1.0, 1.0)

        # Get the primary display size
        # Used when creating the window to speed up initial resizing
        display = pyglet.canvas.get_display()
        screens = display.get_screens()
        w, h = screens[0].width, screens[0].height

        # Output some debug information about screen sizes and positions
        self.cg.debug(f"Found {len(screens)} screens:")
        for n, screen in enumerate(screens):
            self.cg.debug(f"#{n}: {screen.width}x{screen.height}, offset {screen.x}, {screen.y}")

        # Create the main window
        self.window = self.peng.createWindow(
            #width=self.cg.get_config_option("cg:graphics.resolution.width"),
            #height=self.cg.get_config_option("cg:graphics.resolution.height"),
            width=w, height=h,
            #caption_t="cg:window.caption",
            caption="Card Game",
            resizable=True,
            vsync=self.cg.get_config_option("cg:graphics.vsync"),
            fullscreen=self.cg.get_config_option("cg:graphics.fullscreen"),
        )

        # Set Icons, may not work everywhere
        self.window.setIcons("cg:icon.icon_{size}")
        if platform.system() == "Linux":
            # set_minimum_size currently crashes under windows
            # not strictly necessary, so not fixed yet
            # TODO: make this work under windows
            self.window.set_minimum_size(640, 480)
        # Based on https://stackoverflow.com/a/1552105
        if platform.system() in "Windows":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.CG_APPID)
        self.window.maximize()

        # Set Language before loading everything
        # Avoids having to redraw every label due to a language change
        self.peng.i18n.setLang(self.client.settings.get("language", DEFAULT_LANGUAGE))

        if SHOW_FPS:
            self.fps_display = pyglet.window.FPSDisplay(self.window)

            self.window.registerEventHandler("on_draw", self.fps_display.draw)

        self.peng.keybinds.add("f12", "cg:set_fullscreen", self.toggle_fullscreen)

        self.peng.resourceMgr.addCategory("gui")    # GUI elements like buttons etc.
        self.peng.resourceMgr.addCategory("bg")     # Backgrounds
        self.peng.resourceMgr.addCategory("icn")    # Game icons for play menu
        self.peng.resourceMgr.addCategory("card")   # Cards
        self.peng.resourceMgr.addCategory("profile")  # Profile images
        self.peng.resourceMgr.addCategory("server")

        self.peng.resourceMgr.categoriesSettings["icn"]["minfilter"] = GL_LINEAR_MIPMAP_LINEAR
        self.peng.resourceMgr.categoriesSettings["icn"]["magfilter"] = GL_LINEAR

        self.peng.resourceMgr.categoriesSettings["profile"]["minfilter"] = GL_NEAREST
        self.peng.resourceMgr.categoriesSettings["profile"]["magfilter"] = GL_LINEAR

        self.peng.resourceMgr.categoriesSettings["card"]["minfilter"] = GL_LINEAR_MIPMAP_NEAREST
        self.peng.resourceMgr.categoriesSettings["card"]["magfilter"] = GL_LINEAR

        self.peng.resourceMgr.categoriesSettings["gui"]["minfilter"] = GL_NEAREST

        self.update_cursor()

        #pyglet.clock.set_fps_limit(self.cg.get_config_option("cg:graphics.fps"))
        # TODO: implement custom FPS limits
        pyglet.clock.schedule_interval(self.update, 1 / self.client.settings.get("target_fps", 60))

        self.t = self.peng.t
        self.tl = self.peng.tl

        self.register_event_handlers()

    def init(self):
        self.loadingscreen = loadingscreen.LoadingScreenMenu(
            "loadingscreen",
            self.window, self.peng, self,
        )
        self.window.addMenu(self.loadingscreen)

        # Change to loadingscreen as soon as possible
        self.window.changeMenu("loadingscreen")

        self.cg.debug("Initialized loading screen, waiting for other menus")

    def register_menus(self, dt=None):
        self.cg.debug("Initializing remaining menus")

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

        self.settings = settings.SettingsMenu(
            "settings",
            self.window, self.peng, self,
        )
        self.window.addMenu(self.settings)

        self.ingame = ingame.IngameMenu(
            "ingame",
            self.window, self.peng, self,
        )
        self.window.addMenu(self.ingame)

        self.window.changeMenu("serverselect")

    def update(self, dt=None):
        if self.window.activeMenu == "loadingscreen":
            self.loadingscreen.s_loadingscreen.w_label.label = self.peng.tl("cg:gui.menu.load.progress.load_menus")

        if self.client._client is not None:
            self.client._client.process()

    def start_main_loop(self):
        self.run = True
        self.peng.run()

    def discover_profile_images(self, domain="cg"):
        rsrc = "{domain}:profile.{name}".format(domain=domain, name="*")
        pattern = self.peng.rsrcMgr.resourceNameToPath(rsrc, ".png")
        files = glob.glob(pattern)

        names = set()
        r = re.compile(r".*?/profile/(?P<name>[a-zA-Z0-9_ -]{1,64})\.png")

        for f in files:
            m = r.fullmatch(f.replace("\\", "/"))
            if m is not None:
                names.add(m.group("name"))

        return list(names)

    def toggle_fullscreen(self, symbol, modifiers, release):
        if release:
            self.window.set_fullscreen(not self.window.fullscreen)

    def update_cursor(self):
        cursor = self.client.settings.get("cursor", "spades")

        if cursor == "spades":
            # Ensure that the cursor texture has been loaded
            self.peng.resourceMgr.getTex("cg:img.cursor.cursor20p", "gui")
            # TODO: add getTexReg() to resource manager to replace the direct access
            self.window.set_mouse_cursor(pyglet.window.ImageMouseCursor(
                self.peng.resourceMgr.categories["gui"]["cg:img.cursor.cursor20p"], 0, 20
            )
            )
        elif cursor == "system_default":
            # Default System cursor
            self.window.set_mouse_cursor(
                self.window.get_system_mouse_cursor(
                    pyglet.window.Window.CURSOR_DEFAULT
                )
            )
        else:
            self.cg.error(f"Unknown mouse cursor type {cursor}")
            self.window.set_mouse_cursor(
                self.window.get_system_mouse_cursor(
                    pyglet.window.Window.CURSOR_DEFAULT
                )
            )

    # Event Handlers

    def register_event_handlers(self):
        self.cg.add_event_listener("cg:shutdown.do", self.handler_shutdowndo)

        self.peng.addEventListener("peng3d:i18n.miss", self.handler_i18nmiss)
        self.peng.addEventListener("peng3d:rsrc.missing.category", self.handler_rsrccat)
        self.peng.addEventListener("peng3d:rsrc.missing.tex", self.handler_rsrctex)

    def handler_shutdowndo(self, event: str, data: dict):
        pyglet.app.exit()

    def handler_i18nmiss(self, event: str, data: dict):
        self.cg.info(f"Missing i18n key {data['key']} for language {data['lang']}")

    def handler_rsrccat(self, event: str, data: dict):
        self.cg.info(f"Missing resource category {data['cat']} for resource {data['name']}")

    def handler_rsrctex(self, event: str, data: dict):
        self.cg.info(f"Missing resource {data['cat']} for resource {data['name']}")
