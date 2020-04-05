#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  config.py
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
import platform
import peng3d

import cg.error
import cg.util.cache
from cg.util.serializer import yaml


def get_settings_path(name):
    # Lifted from https://github.com/pyglet/pyglet/blob/master/pyglet/resource.py
    # Allowing for usage in headless servers without pyglet
    if platform.system() in 'Windows':
        if 'APPDATA' in os.environ:
            return os.path.join(os.environ['APPDATA'], name)
        else:
            return os.path.expanduser(f'~/{name}')
    elif platform.system() == 'Darwin':
        return os.path.expanduser('~/Library/Application Support/%s' % name)
    elif platform.system() == "Linux":
        if 'XDG_CONFIG_HOME' in os.environ:
            return os.path.join(os.environ['XDG_CONFIG_HOME'], name)
        else:
            return os.path.expanduser('~/.config/%s' % name)
    else:
        return os.path.expanduser('~/.%s' % name)


class ConfigCache(cg.util.cache.Cache):
    def __init__(self, parent, name=None):
        self.parent = parent

        super().__init__(name)

    def load_by_key(self, key):
        return self.parent.load_key(key)


class ConfigManager(object):
    def __init__(self, c):
        self.cg = c

        self.cache = ConfigCache(self, "cfgcache")

    def get_config_option(self, key: str):
        return self.cache.get_by_key(key)

    def set_config_option(self, key: str, value):
        self.cg.warn("set_config_option currently does not save")
        self.cache.set_by_key(key, value)

    def load_key(self, key: str):
        plugin, cat = key.split(":")

        files = self.gen_paths(key)

        success = False

        for cfgfile in files:
            if os.path.exists(cfgfile[0]):
                try:
                    data = yaml.safe_load(cfgfile[0])
                except Exception:
                    continue  # Just ignore corrupt YAML files
                    # TODO: investigate whether or not this could cause a vulnerability

                data, s = self.walk_yaml_tree(data, cfgfile[2], searchfor=key)

                # TODO: maybe find a more performant solution for this
                # Give preference to "older" data, e.g. files higher processed earlier
                data.update(self.cache.cache)
                self.cache.cache.update(data)

                success = success or s

        if not success:
            raise cg.error.ConfigKeyNotFoundException(f"Config key '{key}' could not be found")

        return self.cache.cache[key]  # Direct access to prevent infinity recursion

    def gen_paths(self, key: str):
        spaths = [
            # No F-Strings used here, since the placeholders are replaced multiple times
            os.path.join(self.cg.get_instance_path(), "config", "{domain}", "{fname}.yaml"),
            # os.path.join(self.roum.get_instance_path(), "plugins", "{plugin}", "config", "{fname}.yaml"),
            # os.path.join(self.roum.get_instance_path(), "plugins", "{plugin}", "{fname}.yaml"),
        ]

        domain, f = key.split(":")
        fsplit = f.split(".")

        files = []

        for n in range(1, len(fsplit)):
            fname = os.path.join(*fsplit[:n])

            k = ".".join(fsplit[n:])
            prefix = f"{domain}:{'.'.join(fsplit[:n])}"
            files.append([fname, k, prefix])

        out = [
            [os.path.join(get_settings_path("CardGame"), "config.yaml"), domain+"."+".".join(fsplit), ""],
        ]
        for spath in spaths:
            for f in files:
                out.append([spath.format(domain=domain, fname=f[0]), f[1], f[2]])

        return out

    def walk_yaml_tree(self, data, prefix, searchfor=None):
        searchfor = searchfor.strip()
        out = {}
        success = False
        todo = []

        for k in data:
            todo.append([f"{prefix}.{k}", data[k]])

        while todo:
            name, data = todo.pop()
            name = name.strip()

            if name == searchfor:
                success = True

            if isinstance(data, dict):
                for k in data:
                    todo.append([f"{name}.{k}", data[k]])
            else:
                out[name] = data

        return out, success
