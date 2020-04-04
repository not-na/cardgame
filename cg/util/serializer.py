#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  serializer.py
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

class Serializer(object):
    def __init__(self, module=None):
        self.module = module

    def load(self, fname):
        return self.module.load(fname)

    def loads(self, data):
        return self.module.loads(data)

    def dump(self, data, fname):
        return self.module.dump(data, fname)

    def dumps(self, data):
        return self.module.dump(data)


class JSONSerializer(Serializer):
    def __init__(self, module=None):
        super().__init__(module)

        try:
            import ujson as json
        except ImportError:
            import json

        try:
            # Tries to add comment capability to the load mechanism
            import jsoncomment
            json = jsoncomment.JsonComment(json)
        except ImportError:
            pass  # Not mandatory

        self.module = json


class YAMLSerializer(Serializer):
    def __init__(self, module=None):
        super().__init__(module)

        import yaml
        self.module = yaml

    def safe_load(self, fname):
        with open(fname, "r") as f:
            out = self.module.safe_load(f)
        return out

    def safe_loads(self, data):
        return self.module.safe_load(data)

    def loads(self, data):
        return self.module.load(data)


class MsgPackSerializer(Serializer):
    def __init__(self, module=None):
        super().__init__(module)

        try:
            import msgpack
        except ImportError:
            import umsgpack as msgpack

        self.module = msgpack

    def load(self, fname):
        return self.module.load(fname, raw=False)

    def loads(self, data):
        return self.module.loads(data, raw=False)


json = JSONSerializer()
yaml = YAMLSerializer()
msgpack = MsgPackSerializer()