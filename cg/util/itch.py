#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  itch
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
from typing import Union, Optional

import requests

ITCH_LATEST_URL = "https://itch.io/api/1/x/wharf/latest"

ITCH_GAME = "notna/cardgame"


def get_latest_version(cg, channel: str) -> Optional[str]:
    try:
        r = requests.get(ITCH_LATEST_URL,
                         params={
                             "target": ITCH_GAME,
                             "channel_name": channel,
                         },
                         )

        latest = r.json()["latest"]

    except Exception:
        latest = None
        cg.exception("Exception while getting latest version:")
        try:
            cg.error(f"HTTP Status code: {r.status_code}")
            cg.error(f"Raw Response data:\n{r.text}")
        except Exception:
            pass

    return latest
