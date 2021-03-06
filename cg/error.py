#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  error.py
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


class CGException(Exception):
    pass


class ConfigKeyNotFoundException(CGException):
    pass


class CardTransferError(CGException):
    pass


class GameStateError(CGException):
    pass


class WrongPlayerError(CGException):
    pass


class InvalidMoveError(CGException):
    pass


class RuleError(CGException):
    pass
