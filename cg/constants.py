#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  constants.py
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

# Network modes / states

STATE_AUTH = 100
"""
The ``auth`` state signals that the client still has to authenticate itself.

Most packets cannot be sent in this state.
"""

STATE_ACTIVE = 101
"""
The ``active`` state signals that the client is active and authenticated.

This usually means that it is on the main screen of the server and neither ingame nor in
a lobby.

.. note::
   Clients in this state may or may not be in a party.
"""

STATE_LOBBY = 102
"""
The ``lobby`` state signals that the client is in a lobby.

This state is usually rather short-lived and followed by one of the :py:data:`STATE_GAME_*` states.
"""

STATE_GAME_DK = 110
"""
The ``game_dk`` state signals that this client is currently playing :term:`Doppelkopf`\\ .

This state is usually followed by either :py:data:`STATE_LOBBY` or :py:data:`STATE_ACTIVE`\\ .
"""

MODE_CG = 100

ROLE_REMOVE = -1
ROLE_NONE = 0
ROLE_SPECTATOR = 1
ROLE_PLAYER = 10
ROLE_CREATOR = 100

