#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  cache.py
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
import os
import sys
import time

from cg.util.serializer import json, yaml, msgpack

# Any error code < 128 is OK and error codes >= 128 indicate errors
# Additionaly, error code 0 can always be safely ignored

CHECK_OK = 0
CHECK_FIXED = 1
CHECK_ERROR = 128


class Cache(object):
    def __init__(self, name=None):
        self.name = name
        self.cache = {}

    def get_by_key(self, key):
        if self.key_exists(key):
            return self.cache[key]
        else:
            return self.refresh_key(key)

    def set_by_key(self, key, value):
        self.cache[key] = value

    def refresh_key(self, key):
        self.set_by_key(key, self.load_by_key(key))
        return self.get_by_key(key)

    def remove_key(self, key):
        del self.cache[key]

    def flush(self):
        self.cache = {}

    def check_integrity(self):
        return CHECK_OK

    def check_key(self, key):
        return CHECK_OK

    def load_by_key(self, key):
        return None  # Dummy method; to be overwritten by subclasses

    def key_exists(self, key):
        self.check_key(key)
        return key in self.cache

    def list_keys(self):
        return self.cache.keys()

    def __getitem__(self, key):
        return self.get_by_key(key)

    def __setitem__(self, key, value):
        self.set_by_key(key, value)

    def __contains__(self, key):
        return self.key_exists(key)

    def __len__(self):
        return len(self.cache)

    def __dict__(self):
        return self.cache


class TimedCache(Cache):
    def __init__(self, name=None, maxage=100):
        Cache.__init__(self, name)
        self.maxage = maxage

    def get_by_key(self, key):
        if self.key_exists(key) and time.time() - self.cache[key][1] <= self.maxage:
            return self.cache[key][0]
        else:
            return self.refresh_key(key)

    def set_by_key(self, key, value):
        self.cache[key] = [value, time.time()]

    def reset_age_by_key(self, key):
        self.cache[key][1] = time.time()

    def check_key_age(self, key):
        if time.time() - self.cache[key][1] > self.maxage:
            return CHECK_ERROR
        return CHECK_OK

    def check_integrity(self):
        retkey = CHECK_OK
        for k in self.list_keys():
            if self.check_key_age(k) == CHECK_ERROR:
                self.remove_key(k)
                retkey = CHECK_FIXED
        return retkey


class SizedCache(Cache):
    def __init__(self, name=None, maxsize=1024):
        Cache.__init__(self, name)
        if maxsize > sys.maxsize:
            raise ValueError("maxsize may be at most sys.maxsize")
        elif not isinstance(maxsize, int):
            raise TypeError("maxsize may only be an integer")
        self.cache = collections.OrderedDict()
        self.maxsize = maxsize

    def flush(self):
        self.cache = collections.OrderedDict()

    def set_by_key(self, key, value):
        if len(self.cache) >= self.maxsize:
            self.cache.popitem(False)
        self.cache[key] = value

    def check_integrity(self):
        retval = CHECK_OK
        while len(self.cache) > self.maxsize:
            retval = CHECK_FIXED
            self.cache.popitem(False)
        return retval


class TimeSizedCache(SizedCache):
    def __init__(self, name=None, maxage=100, maxsize=1024):
        super(TimeSizedCache, self).__init__(name, maxsize)
        TimedCache.__init__(self, name, maxage)

    def set_by_key(self, key, value):
        if len(self.cache) >= self.maxsize:
            self.cache.popitem(False)
        self.cache[key] = [value, time.time()]

    def check_integrity(self):
        retval = super(TimeSizedCache, self).check_integrity()
        retval2 = TimedCache.check_integrity(self)
        if retval == CHECK_FIXED or retval2 == CHECK_FIXED:
            return CHECK_FIXED
        else:
            return CHECK_OK


class FileCache(TimedCache):
    def __init__(self, name=None, maxage=500, root=os.curdir):
        TimedCache.__init__(self, name, maxage)
        self.root = root

    def load_by_key(self, key):
        fpath = self.get_file_path_by_key(key)

        with open(fpath, "r") as f:
            data = f.read()

        return data

    def get_by_key(self, key):
        return TimedCache.get_by_key(self, self.get_file_path_by_key(key))

    def get_file_path_by_key(self, key):
        if os.path.isabs(key):
            fpath = key
        elif key.startwith("~"):
            fpath = os.path.expandvars(key)
        else:
            fpath = os.path.relpath(key, self.root)
        fpath = os.path.abspath(fpath)
        return fpath

    def get_file_data(self, fname):
        return self.get_by_key(fname)


class JSONCache(FileCache):
    def load_by_key(self, key):
        return json.load(self.get_file_path_by_key(key))


class YAMLCache(FileCache):
    def load_by_key(self, key):
        return yaml.safe_load(self.get_file_path_by_key(key))


class MsgPackCache(FileCache):
    def load_by_key(self, key):
        return msgpack.load(self.get_file_path_by_key(key))