#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  serverselect.py
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
import queue
import threading
import time
import uuid
from typing import Any, Dict

import peng3d

import cgclient.gui
import pyglet

import cg
from cg.util.serializer import msgpack


class ServerSelectMenu(peng3d.gui.GUIMenu):
    def __init__(self, name, window, peng, gui):
        super().__init__(name, window, peng,
                         font="Times New Roman",
                         font_size=25,
                         font_color=[255, 255, 255, 100]
                         )

        self.gui = gui
        self.cg = gui.cg

        self.setBackground(peng3d.gui.button.FramedImageBackground(
            peng3d.gui.FakeWidget(self),
            bg_idle=self.peng.resourceMgr.getTex("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(0.3, 0.3),
            tex_size=self.peng.resourceMgr.getTexSize("cg:img.bg.bg_brown", "gui")
        )
        )
        self.bg.vlist_layer = -3

        self.s_titlescreen = TitleScreenSubMenu("titlescreen", self, self.window, self.peng)
        self.addSubMenu(self.s_titlescreen)

        self.s_serverselect = ServerSelectionSubMenu("serverselect", self, self.window, self.peng)
        self.addSubMenu(self.s_serverselect)

        self.changeSubMenu("titlescreen")


class TitleScreenSubMenu(peng3d.gui.SubMenu):
    menu: ServerSelectMenu

    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.addAction("send_form", self.on_send_form)

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [3, 8], [60, 30])

        # Background
        self.setBackground(peng3d.gui.FramedImageBackground(
            self,
            bg_idle=("cg:img.bg.bg", "bg"),
            frame=[[0, 1, 0], [0, 1, 0]],
            scale=(.5, .5),
            repeat_edge=True, repeat_center=True,
        )
        )
        self.bg.vlist_layer = -2

        # Left sidebar (background)
        self.sidebar = peng3d.gui.Widget(
            "sidebar", self, self.window, self.peng,
            pos=(0, 0),
            size=(lambda sw, sh: (sw / 3, sh)),
        )
        self.sidebar.setBackground(peng3d.gui.FramedImageBackground(
            self.sidebar,
            bg_idle=("cg:img.bg.sidebar", "gui"),
            frame=[[1, 1, 10], [0, 1, 0]],
            scale=(.3, 0),
        )
        )
        self.sidebar.bg.vlist_layer = -1
        self.addWidget(self.sidebar)

        # Screen Edge
        self.screen_edge = peng3d.gui.Widget(
            "screen_edge", self, self.window, self.peng,
            pos=(0, 0),
            size=(lambda sw, sh: (sw, sh))
        )
        self.screen_edge.setBackground(peng3d.gui.FramedImageBackground(
            self.screen_edge,
            bg_idle=("cg:img.bg.bg_trans", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )
        self.addWidget(self.screen_edge)

        # Play Button
        # This button switches to the serverselect submenu
        self.playbtn = cgclient.gui.CGButton(
            "playbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 4], [1, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.title.playbtn.label"),
        )
        self.addWidget(self.playbtn)

        self.playbtn.addAction("click", self.send_form)

        # Settings Button
        # This button switches to the settings submenu
        self.settingsbtn = cgclient.gui.CGButton(
            "settingsbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 3], [1, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.title.settingsbtn.label"),
        )
        self.addWidget(self.settingsbtn)

        def f():
            self.window.changeMenu("settings")
            self.window.menu.prev_menu = "serverselect"

        self.settingsbtn.addAction("click", f)

    def on_send_form(self):
        self.menu.changeSubMenu("serverselect")


class ServerSelectionSubMenu(peng3d.gui.SubMenu):
    def __init__(self, name, menu, window, peng):
        super().__init__(name, menu, window, peng)

        self.register_event_handlers()

        self.active_server = None
        self.server_data = {}

        self.server_lock = threading.Lock()

        self.addAction("send_form", self.on_send_form)

        self.server_queue = queue.Queue()
        pyglet.clock.schedule_interval(self._update_serverlist, 0.1)

        self.setBackground(peng3d.gui.button.FramedImageBackground(
            peng3d.gui.FakeWidget(self),
            bg_idle=("cg:img.bg.bg_dark_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )

        self.grid = peng3d.gui.GridLayout(self.peng, self, [4, 9], [60, 30])

        # Upper Bar
        self.w_upper_bar = peng3d.gui.Widget(
            "upper_bar", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 8], [4, 1], border=0),
        )
        self.w_upper_bar.setBackground(peng3d.gui.FramedImageBackground(
            self.w_upper_bar,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3)
        ))
        self.addWidget(self.w_upper_bar)

        # Lower Bar
        self.w_lower_bar = peng3d.gui.Widget(
            "lower_bar", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [4, 2], border=0),
        )
        self.w_lower_bar.setBackground(peng3d.gui.FramedImageBackground(
            self.w_lower_bar,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3)
        ))
        self.addWidget(self.w_lower_bar)

        # Buttons
        # Server Connect Button
        self.connectbtn = cgclient.gui.CGButton(
            "connectbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 1], [2, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.connectbtn.label")
        )
        self.addWidget(self.connectbtn)
        self.connectbtn.enabled = False

        self.connectbtn.addAction("click", self.send_form)

        # Server Add Button
        self.addbtn = cgclient.gui.CGButton(
            "addbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([2, 1], [2, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.addbtn.label")
        )
        self.addWidget(self.addbtn)

        def f():
            if not self.c_edit.visible:
                self.c_add.visible = True

        self.addbtn.addAction("click", f)

        # Server Edit Button
        self.editbtn = cgclient.gui.CGButton(
            "editbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.editbtn.label")
        )
        self.addWidget(self.editbtn)
        self.editbtn.enabled = False

        def f():
            if not self.c_add.visible:
                self.c_edit.visible = True
                self.c_edit.refresh(self.server_data[self.active_server])

        self.editbtn.addAction("click", f)

        # Server Delete Button
        self.deletebtn = cgclient.gui.CGButton(
            "deletebtn", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.deletebtn.label")
        )
        self.addWidget(self.deletebtn)
        self.deletebtn.enabled = False

        def f():
            if not self.c_add.visible and not self.c_edit.visible:
                with self.server_lock:
                    del self.server_data[self.active_server]

                self.save_server_list()
                self.load_servers()

        self.deletebtn.addAction("click", f)

        # Server Refresh Button
        self.refreshbtn = cgclient.gui.CGButton(
            "refreshbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([2, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.refreshbtn.label")
        )
        self.addWidget(self.refreshbtn)

        def f():
            if not self.c_add.visible and not self.c_edit.visible:
                self.load_servers()

        self.refreshbtn.addAction("click", f)

        # Cancel Button
        self.cancelbtn = cgclient.gui.CGButton(
            "cancelbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([3, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.cancelbtn.label")
        )
        self.addWidget(self.cancelbtn)

        self.cancelbtn.addAction("click", self.menu.changeSubMenu, "titlescreen")

        # Server List
        self.serverbtns = []
        for i in range(6):
            btn = ServerButton(
                f"serverbtn{i}", self, self.window, self.peng,
                pos=self._serverbtn_pos(i),
                size=(lambda sw, sh:
                      (self.grid.get_cell([0, 0], [4, 1], border=0).size[0] - 6,
                       self.grid.get_cell([0, 0], [4, 1], border=0).size[1])
                      )
            )
            self.addWidget(btn)

            def f(button):
                for b in self.serverbtns:
                    if b != button:
                        b.pressed = False
                        b.doAction("press_up")
                        b.redraw()

                self.active_server = button.uuid

                self.connectbtn.enabled = True
                self.editbtn.enabled = True
                self.deletebtn.enabled = True

            btn.addAction("press_down", f, btn)

            def f():
                self.active_server = None

                self.connectbtn.enabled = True
                self.editbtn.enabled = True
                self.deletebtn.enabled = True

            btn.addAction("press_up", f)

            self.serverbtns.append(btn)

        # Add Container
        self.c_add = ServerAddContainer(
            "c_add", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 3], [2, 4]),
            size=None
        )
        self.addWidget(self.c_add)

        # Edit Container
        self.c_edit = ServerEditContainer(
            "c_edit", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 3], [2, 4]),
            size=None
        )
        self.addWidget(self.c_edit)

    def form_valid(self, ctx=None):
        return not self.c_add.visible and not self.c_edit.visible

    def add_server(self, data):
        for btn in self.serverbtns:
            if btn.uuid is None:
                self.server_data[data["uuid"]] = data

                btn.serverdata = data
                btn.label_name.label = btn.serverdata["name"]
                btn.label_last_played.label = "Never played"
                if btn.serverdata["lastplayed"] >= 1:
                    btn.label_last_played.label = \
                        f"Last played {cg.util.time.tdiff_format_smart(data['lastplayed'], p_abs='on ')}"
                btn.connection_icon.switchImage("connecting")
                btn.redraw()

                self.save_server_list()

                self.peng.cg.client.async_ping_server(data["address"], data["uuid"])
                self.peng.cg.debug(f"Added Server with UUID {btn.uuid} to server list")
                return

    def update_server(self, data):
        for btn in self.serverbtns:
            if btn.uuid == data["uuid"]:
                self.server_data[data["uuid"]] = data

                btn.serverdata = data
                btn.label_name.label = btn.serverdata["name"]
                btn.connection_icon.switchImage("connecting")
                btn.redraw()

                self.save_server_list()

                self.peng.cg.client.async_ping_server(data["address"], data["uuid"])
                self.peng.cg.debug(f"Added Server with UUID {btn.uuid} to server list")
                return
        self.peng.cg.warn("Didn't find the serverbutton, that should be updated!")

    def save_server_list(self):
        with self.server_lock:
            try:
                with open(self.menu.cg.get_settings_path("serverlist.csl"), "wb") as f:
                    msgpack.dump({"serverlist": self.server_data}, f)
                    self.menu.cg.info(f"Successfully saved server list with {len(self.server_data)} items")
            except Exception:
                self.menu.cg.warning("Could not save server list, trying again in one second")
                self.menu.cg.exception("Exception during server metadata save:")

    def load_servers(self):
        # Delete all previous server items
        for btn in self.serverbtns:
            btn.serverdata = {"uuid": None}
            btn.label_name.label = ""
            btn.label_slogan.label = ""
            btn.label_last_played.label = ""
            btn.connection_icon.switchImage("transparent")
            btn.pressed = False
            btn.doAction("press_up")

        # Removes old selected server
        self.active_server = None
        self.deletebtn.enabled = False
        self.connectbtn.enabled = False
        self.editbtn.enabled = False

        self.server_data = {}

        # Load the server list
        try:
            with open(self.menu.cg.get_settings_path("serverlist.csl"), "rb") as f:
                d = msgpack.load(f)
                self.menu.cg.debug(f"Successfully deserialized server list, raw data: {d}")
        except FileNotFoundError:
            self.menu.cg.warning("Server list not found, creating a new one")
            d = {"serverlist": {}}
        except Exception:
            self.menu.cg.error("Error during server list load")
            self.menu.cg.exception("Exception while loading server list:")
            self.menu.changeSubMenu("titlescreen")
            return

        slist = []
        for suuid, data in d.get("serverlist", {}).items():
            if not isinstance(data.get("lastplayed", None), float):
                data["lastplayed"] = -1
            self.menu.cg.client.async_ping_server(data["address"], suuid)
            self.server_data[suuid] = data
            self.server_data[suuid]["status"] = "running"
            slist.append(data)

        # Sort the server list by most recently played
        def f(item):
            return item.get("lastplayed", -1)

        slist.sort(key=f, reverse=True)

        for server in slist:
            try:
                self.add_server(server)
            except Exception:
                self.menu.cg.exception("Could not add server to list:")

        self.menu.cg.info(f"Successfully loaded/reloaded server list, {len(slist)} servers")

    def _update_serverlist(self, dt=None):
        while not self.server_queue.empty():
            self._update_server(self.server_queue.get_nowait())

    def _update_server(self, server: str):
        if server not in self.server_data:
            return  # Not managed by the server list

        data = self.server_data[server]

        btn = None
        for btn in self.serverbtns:
            if data["uuid"] == btn.uuid:
                break
        if btn is None:
            self.menu.cg.error("Received server update for server without button, ignoring")
            return

        pdata = data.get("pingdata", {})

        name = pdata.get("visiblename", "")
        if name.strip() == "" or name == "None":
            name = data["name"]
        if name.strip() == "":
            name = "A CardGame Server"
        btn.label_name.label = name

        btn.label_slogan.label = pdata.get("slogan", "A CG Server")

        if data["status"] == "error":
            conn_symbol = "not_connected"
        elif data["status"] == "running":
            conn_symbol = "connecting"
        elif data["status"] == "complete":
            delay = pdata.get("delay", -1) * 1000

            q = 0
            if delay < 10:
                q = 100
            elif delay < 20:
                q = 75
            elif delay < 40:
                q = 50
            elif delay < 80:
                q = 25
            conn_symbol = f"conn_{q}"
        else:
            raise ValueError(f"Unsupported status {data['status']} for server with uuid {server}")

        btn.connection_icon.switchImage(conn_symbol)
        btn.redraw()

        self.save_server_list()

    def _serverbtn_pos(self, i):
        cell = self.grid.get_cell([0, 7 - i], [4, 1], border=0)
        return lambda sw, sh, bw, bh: (3, cell.pos[1])

    def on_enter(self, old):
        self.load_servers()

    def on_exit(self, new):
        self.c_add.visible = False
        self.c_edit.visible = False

        for i in self.serverbtns:
            i.pressed = False
            i.doAction("press_up")
        self.active_server = None
        self.connectbtn.enabled = True
        self.editbtn.enabled = True
        self.deletebtn.enabled = True

    def on_send_form(self):
        self.menu.cg.client.connect_to(self.server_data[self.active_server]["address"], self.active_server)
        self.window.changeMenu("servermain")
        self.window.menus["servermain"].changeSubMenu("load")

    def register_event_handlers(self):
        self.menu.cg.add_event_listener("cg:client.ping.complete", self.handle_serverpingcomplete)
        self.menu.cg.add_event_listener("cg:client.ping.error", self.handle_serverpingerror)
        self.menu.cg.add_event_listener("cg:network.client.conn_establish", self.handle_clientconnestablish)

    def handle_serverpingcomplete(self, event: str, data: dict):
        if data["ref"] not in self.server_data:
            return  # Ping was probably caused by something else

        self.server_data[data["ref"]]["pingdata"] = data["data"]
        self.server_data[data["ref"]]["status"] = "complete"
        self.server_queue.put(data["ref"])

    def handle_serverpingerror(self, event: str, data: dict):
        if data["ref"] not in self.server_data:
            return  # Ping was probably caused by something else

        self.server_data[data["ref"]]["pingdata"] = data["data"]
        self.server_data[data["ref"]]["status"] = "error"
        self.server_queue.put(data["ref"])

    def handle_clientconnestablish(self, event: str, data: dict):
        with self.server_lock:
            if data["ref"] in self.server_data:
                self.server_data[data["ref"]]["lastplayed"] = time.time()
        self.save_server_list()


class ServerAddContainer(peng3d.gui.Container):
    def __init__(self, name, submenu, window, peng, pos, size):
        super().__init__(name, submenu, window, peng, pos, size)

        self.visible = False

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [2, 4], [30, 20])

        self.bg_widget = peng3d.gui.Widget("add_bg", self, self.window, self.peng,
                                           pos=(0, 0),
                                           size=(lambda sw, sh: (sw, sh)))
        self.bg_widget.setBackground(peng3d.gui.button.FramedImageBackground(
            self.bg_widget,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )
        self.addWidget(self.bg_widget, 10)

        # Heading
        self.heading = peng3d.gui.Label(
            "add_heading", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 3], [2, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.add.heading"),
            font_size=25,
            label_layer=11,
        )
        self.addWidget(self.heading)

        # Input filed for server name
        self.input_name = cgclient.gui.CGTextInput(
            "name_input", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 2], [2, 1]),
            default=self.peng.tl("cg:gui.menu.serverselect.serverselect.add.name.default"),
            font_color_default=[255, 255, 255, 50],
            font_size=25
        )
        self.input_name.bg.parent.vlist_layer = 11
        self.input_name.bg.vlist_cursor_layer = 12
        self.addWidget(self.input_name)

        # Input field for server address
        self.input_addr = cgclient.gui.CGTextInput(
            "addr_input", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 1], [2, 1]),
            default=self.peng.tl("cg:gui.menu.serverselect.serverselect.add.addr.default"),
            font_color_default=[255, 255, 255, 50],
            font_size=25
        )
        self.input_addr.bg.parent.vlist_layer = 11
        self.input_addr.bg.vlist_cursor_layer = 12
        self.addWidget(self.input_addr)

        # Ok Button
        self.okbtn = cgclient.gui.CGButton(
            "add_okbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.add.okbtn.label"),
            label_layer=12,
        )
        self.okbtn.bg.vlist_layer = 11
        self.addWidget(self.okbtn)

        def f():
            if self.input_addr.text.strip() == "":
                return
            else:
                servername = self.input_name.text

                data = {
                    "name": servername,
                    "address": self.input_addr.text,
                    "uuid": uuid.uuid4().hex,
                    "lastplayed": -1
                }

            self.submenu.add_server(data)

            self.input_addr.text = ""
            self.input_name.text = ""
            self.visible = False

        self.okbtn.addAction("click", f)

        # Cancel Button
        self.cancelbtn = cgclient.gui.CGButton(
            "add_cancelbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.add.cancelbtn.label"),
            label_layer=12,
        )
        self.cancelbtn.bg.vlist_layer = 11
        self.addWidget(self.cancelbtn)

        def f():
            self.input_addr.text = ""
            self.input_name.text = ""
            self.visible = False

        self.cancelbtn.addAction("click", f)


class ServerEditContainer(peng3d.gui.Container):
    def __init__(self, name, submenu, window, peng, pos, size):
        super().__init__(name, submenu, window, peng, pos, size)

        self.visible = False

        self.data = {}

        self.grid = peng3d.gui.layout.GridLayout(self.peng, self, [2, 4], [30, 20])

        self.bg_widget = peng3d.gui.Widget("edit_bg", self, self.window, self.peng,
                                           pos=(0, 0),
                                           size=(lambda sw, sh: (sw, sh)))
        self.bg_widget.setBackground(peng3d.gui.button.FramedImageBackground(
            self.bg_widget,
            bg_idle=("cg:img.bg.bg_brown", "gui"),
            frame=[[10, 1, 10], [10, 1, 10]],
            scale=(.3, .3),
        )
        )
        self.bg_widget.bg.vlist_layer = 10
        self.addWidget(self.bg_widget)

        # Heading
        self.heading = peng3d.gui.Label(
            "edit_heading", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 3], [2, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.edit.heading"),
            font_size=25,
            label_layer=11,
        )
        self.addWidget(self.heading)

        # Input filed for server name
        self.input_name = cgclient.gui.CGTextInput(
            "name_input", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 2], [2, 1]),
            default=self.peng.tl("cg:gui.menu.serverselect.serverselect.edit.name.default"),
            font_color_default=[255, 255, 255, 50],
            font_size=25
        )
        self.input_name.bg.parent.vlist_layer = 11
        self.input_name.bg.vlist_cursor_layer = 12
        self.addWidget(self.input_name)

        # Input field for server address
        self.input_addr = cgclient.gui.CGTextInput(
            "addr_input", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 1], [2, 1]),
            default=self.peng.tl("cg:gui.menu.serverselect.serverselect.edit.addr.default"),
            font_color_default=[255, 255, 255, 50],
            font_size=25
        )
        self.input_addr.bg.parent.vlist_layer = 11
        self.input_addr.bg.vlist_cursor_layer = 12
        self.addWidget(self.input_addr)

        # Ok Button
        self.okbtn = cgclient.gui.CGButton(
            "edit_okbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([0, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.edit.okbtn.label"),
            label_layer=12,
        )
        self.okbtn.bg.vlist_layer = 11
        self.addWidget(self.okbtn)

        def f():
            if self.input_addr.text.strip() == "":
                return

            self.data["name"] = self.input_name.text
            self.data["address"] = self.input_addr.text
            self.submenu.update_server(self.data)

            self.data = {}
            self.input_addr.text = ""
            self.input_name.text = ""
            self.visible = False

        self.okbtn.addAction("click", f)

        # Cancel Button
        self.cancelbtn = cgclient.gui.CGButton(
            "edit_cancelbtn", self, self.window, self.peng,
            pos=self.grid.get_cell([1, 0], [1, 1]),
            label=self.peng.tl("cg:gui.menu.serverselect.serverselect.edit.cancelbtn.label"),
            label_layer=12,
        )
        self.cancelbtn.bg.vlist_layer = 11
        self.addWidget(self.cancelbtn)

        def f():
            self.data = {}
            self.input_addr.text = ""
            self.input_name.text = ""
            self.visible = False

        self.cancelbtn.addAction("click", f)

    def refresh(self, data):
        self.data = data

        self.input_name.text = data["name"]
        self.input_name.cursor_pos = len(self.input_name.text)

        self.input_addr.text = data["address"]
        self.input_addr.cursor_pos = len(self.input_addr.text)


class ServerButton(peng3d.gui.LayeredWidget):
    submenu: ServerSelectionSubMenu

    def __init__(self, name, submenu, window, peng, pos, size):
        super().__init__(name, submenu, window, peng, pos, size)

        self.serverdata: Dict[str, Any] = {
            "uuid": None,
        }

        # Background
        self.bg_layer = peng3d.gui.DynImageWidgetLayer(
            "bg_layer", self, z_index=1,
            imgs={
                "idle": ("cg:img.bg.transparent", "gui"),
                "hover": ("cg:img.bg.gray_brown", "gui"),
                "press": ("cg:img.bg.dark_gray_brown", "gui")
            }
        )
        self.addLayer(self.bg_layer)
        self.bg_layer.switchImage("idle")

        def f():
            if not self.pressed and not self.submenu.c_add.visible and not self.submenu.c_edit.visible:
                self.bg_layer.switchImage("hover")

        self.addAction("hover_start", f)

        def f():
            if not self.pressed:
                self.bg_layer.switchImage("idle")

        self.addAction("hover_end", f)

        def f():
            self.bg_layer.switchImage("press")

        self.addAction("press_down", f)

        def f():
            if not self.is_hovering:
                self.bg_layer.switchImage("idle")
            else:
                self.bg_layer.switchImage("hover")

        self.addAction("press_up", f)

        # Server name
        self.label_name = peng3d.gui.LabelWidgetLayer(
            "label_name", self, z_index=2,
            offset=(lambda ww, wh, sw, sh: (-sw / 2 + 60, 0)),
            # border=(lambda ww, wh, sw, sh: (sw, 0)),
            font_size=35
        )
        self.addLayer(self.label_name)
        self.label_name._label.bold = True
        self.label_name._label.anchor_x = "left"
        self.label_name._label.anchor_y = "baseline"

        # Server Slogan
        self.label_slogan = peng3d.gui.HTMLLabelWidgetLayer(
            "label_slogan", self, z_index=2,
            offset=(lambda ww, wh, sw, sh: (-sw / 2 + 60, -10)),
            font_color=[255, 255, 255, 50],
            font_size=25,
            font="Times New Roman"
        )
        self.addLayer(self.label_slogan)
        self.label_slogan._label.anchor_x = "left"
        self.label_slogan._label.anchor_y = "top"

        # Last Played
        self.label_last_played = peng3d.gui.LabelWidgetLayer(
            "label_last_played", self, z_index=2,
            offset=(lambda ww, wh, sw, sh: (sw * 5 / 12, sh * -1 / 6 - 3)),
            font_color=[255, 255, 255, 50],
            font_size=16,
        )
        self.addLayer(self.label_last_played)
        self.label_last_played._label.anchor_y = "top"

        # Connection icon
        self.connection_icon = peng3d.gui.DynImageWidgetLayer(
            "connection_symbol", self, z_index=2,
            offset=(lambda ww, wh, sw, sh: (sw * 5 / 12, sh * 1 / 12)),
            border=(lambda ww, wh, sw, sh: ((sw - (sh * 1 / 2)) / 2, sh * 1 / 4)),
            imgs={
                "transparent": ["cg:img.bg.transparent", "gui"],
                "connecting": ["cg:img.server.connecting", "server"],
                "not_connected": ["cg:img.server.not_connected", "server"],
                "conn_0": ["cg:img.server.conn_0", "server"],
                "conn_25": ["cg:img.server.conn_25", "server"],
                "conn_50": ["cg:img.server.conn_50", "server"],
                "conn_75": ["cg:img.server.conn_75", "server"],
                "conn_100": ["cg:img.server.conn_100", "server"],
            },
            default="transparent",
        )
        self.addLayer(self.connection_icon)
        self.connection_icon.switchImage("transparent")

    @property
    def clickable(self):
        return super().clickable and not self.submenu.c_add.visible and not self.submenu.c_edit.visible

    @property
    def visible(self):
        return super().visible and self.uuid is not None

    @property
    def uuid(self):
        return self.serverdata["uuid"]

    def _mouse_aabb(self, mpos, size, pos):
        return pos[0] <= mpos[0] <= pos[0] + size[0] and pos[1] <= mpos[1] <= pos[1] + size[1]

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.clickable:
            return
        elif self._mouse_aabb([x, y], self.size, self.pos):
            if button == pyglet.window.mouse.LEFT:
                self.doAction("click")
                self.pressed = not self.pressed
                if self.pressed:
                    self.doAction("press_down")
                else:
                    self.doAction("press_up")
            elif button == pyglet.window.mouse.RIGHT:
                self.doAction("context")
            self.redraw()

    def on_mouse_release(self, x, y, button, modifiers):
        pass
