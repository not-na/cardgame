#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
#
#  Copyright 2020 contributors of CardGame
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

import os
import sys

import time
stime = time.time()

import traceback

import cgclient

from plumbum import cli

class CardgameApp(cli.Application):
    PROGNAME = "CardGame"
    VERSION = cgclient.version.VERSIONSTRING

    addr = cli.SwitchAttr(["-a", "--address"],
                          argtype=str,
                          default=None,
                          help="Connect to a server immediately",
                          )

    username = cli.SwitchAttr(["-u", "--username"],
                              argtype=str,
                              default=None,
                              help="Sets the pre-filled username",
                              )

    pwd = cli.SwitchAttr(["-p", "--pwd"],
                         argtype=str,
                         default=None,
                         help="Sets the pre-filled password",
                         )

    def main(self):
        print("Client starting...")
        sys.stdout.flush()

        # TODO...
        print(f"--address={self.addr} --username={self.username} --pwd={self.pwd}")

        return 0


def main():
    try:
        # Try to run the main app
        CardgameApp.run()
    except Exception:
        # Catch all errors and print them
        print("Exception occured:")
        traceback.print_exc()
        try:
            # Try to "file" a crash report
            # TODO: implement crash reporter
            pass
        except Exception:
            # Report if that fails
            print("Exception during crash report:")
            traceback.print_exc()
    finally:
        try:
            # Always try to send out a shutdown event
            # TODO: clean shutdown
            pass
        except Exception:
            # Report on any exceptions
            print("Exception during shutdown handler:")
            traceback.print_exc()

        try:
            # Finally, print out this goodbye message
            print(f"Exiting after {time.time()-stime:.3f} seconds")
        except Exception:
            pass  # When print() fails...

    # Exit with an error code
    sys.exit(1)


if __name__ == "__main__":
    main()
