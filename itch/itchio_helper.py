#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  itchio_helper.py
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
import shutil
import subprocess
import platform
import sys
import importlib.util

OUTPUT_DIR_BASE = "itchio-dist"
OUTPUT_DIR_PLAT = os.path.join(OUTPUT_DIR_BASE, platform.system())

CHANNEL_WIN = "win"
CHANNEL_LINUX = "linux"

CHANNEL_SUFFIX_BETA = "-beta"
CHANNEL_SUFFIX_SERVER = "-server"

GAME_NAME = "notna/cardgame"

ITCH_TOML_TEMPLATE = """
[[actions]]
name = "play"
path = "{executable}"
"""


def compile_dist(server, beta):
    if platform.system() in "Windows":
        channel = CHANNEL_WIN
    elif platform.system() == "Linux":
        channel = CHANNEL_LINUX
    else:
        print(f"ERROR: unsupported platform {platform.system()}")
        return

    if server:
        channel = channel+CHANNEL_SUFFIX_SERVER
        mode = "--onefile"
    else:
        mode = "--onedir"
    if beta:
        channel = channel+CHANNEL_SUFFIX_BETA

    print(f"Compiling for channel '{channel}'")

    OUTPUT_DIR = os.path.join(OUTPUT_DIR_BASE, channel)

    # Check that we are in the correct directory
    d = os.listdir(".")
    for r in ["itch", "client", "server"]:
        if r not in d:
            print(f"ERROR: directory {r} is missing, are you in the correct directory?")
            print("This script should be started as 'python itch/itchio_helper.py'")
            return

    print("Creating/Cleaning output directory...")
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    print("Compiling with PyInstaller...")

    # Create channel file
    with open(f"{OUTPUT_DIR_BASE}/channel.txt", "w") as f:
        f.write(channel)

    if not server:
        args = [
                "pyinstaller",
                mode,                   # Single File/Directory output
                "--clean",              # Clean temp files
                "--windowed",           # Windowed mode, no console window
                "--name", "Cardgame",   # Binary Name
                "--add-data", f"./client/assets/{os.pathsep}assets/",   # Include all assets
                "--add-data", f"{OUTPUT_DIR_BASE}/channel.txt{os.pathsep}.",
                "--distpath", os.path.join(OUTPUT_DIR, "bin"),
            ]
    else:
        args = [
            "pyinstaller",
            mode,
            "--clean",
            "--console",
            "--name", "Cardgame",
            "--add-data", f"{OUTPUT_DIR_BASE}/channel.txt{os.pathsep}.",
            "--distpath", os.path.join(OUTPUT_DIR, "bin"),
        ]

    if False and platform.system() in "Windows":
        args.append("--icon")
        args.append("./client/assets/cg/icon/icon_256.png")

    if not server:
        args.append("client/main.py")
    else:
        args.append("server/main.py")

    # Set the hash seed for pyinstaller
    # Allows for reproducible builds
    env = os.environ
    env["PYTHONHASHSEED"] = "1"

    ret = subprocess.call(
        args,
        env=env,
    )

    if ret != 0:
        print("ERROR: non-zero return code from pyinstaller\nExiting")
        return

    print("Creating itch.io manifest...")
    if mode == "--onefile":
        executable = "bin/Cardgame"
    else:
        executable = "bin/Cardgame/Cardgame"

    if platform.system() in "Windows":
        executable += ".exe"
        executable = executable.replace("\\", "\\\\")
    to_write = ITCH_TOML_TEMPLATE.format(executable=executable)
    with open(os.path.join(OUTPUT_DIR, ".itch.toml"), "w") as f:
        f.write(to_write)

    print("Copying additional files...")
    shutil.copytree("itch/common", OUTPUT_DIR, dirs_exist_ok=True)

    if platform.system() in "Windows":
        print("Copying Windows-specific files...")
        shutil.copytree("itch/win", OUTPUT_DIR, dirs_exist_ok=True)
    elif platform.system() == "Linux":
        print("Copying Linux-specific files...")
        shutil.copytree("itch/linux", OUTPUT_DIR, dirs_exist_ok=True)

    print("Creating Version file...")
    if server:
        n = "client"
    else:
        n = "server"
    sys.path.append(f"./{n}")

    # Directly import the version file, without importing the rest of CG
    spec = importlib.util.spec_from_file_location(f"cg{n}.version",
                                                  os.path.join(f"{n}", f"cg{n}", "version.py")
                                                  )
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"cg{n}.version"] = module
    spec.loader.exec_module(module)

    with open(os.path.join(OUTPUT_DIR_BASE, "version.txt"), "w") as f:
        f.write(module.SEMVER)

    print(f"Done for channel '{channel}'!")

    return 0


def push(dry_run):
    channels = get_channels()

    if dry_run:
        print("Performing dry run, nothing will actually be pushed")
    input("Press enter to continue or Ctrl+C to cancel")

    for channel in channels:
        print(f"Pushing channel {channel}...")
        if input("Press enter to push, type anything to skip this channel: ").strip() != "":
            print("Skipping channel")
            continue
        args = [
            "butler",
            "push",
            os.path.abspath(os.path.join(OUTPUT_DIR_BASE, channel)),
            f"{GAME_NAME}:{channel}",
            "--userversion-file", os.path.join(OUTPUT_DIR_BASE, "version.txt"),
        ]
        if dry_run:
            args.append("--dry-run")

        ret = subprocess.call(args)

        if ret != 0:
            print(f"ERROR: butler returned non-zero exit code {ret}")
            input("Press enter to continue or Ctrl+C to cancel further pushes")


def get_channels():
    print("Gathering built channels...")

    dirs = os.listdir(OUTPUT_DIR_BASE)

    channels = []

    for dir in dirs:
        d = os.path.join(OUTPUT_DIR_BASE, dir)
        if not os.path.isdir(d):
            continue
        print(f"Found channel {dir}")
        channels.append(dir)

    print(f"Found {len(channels)} in total")

    return channels


def validate():
    channels = get_channels()

    for channel in channels:
        print(f"Validating channel {channel}...")
        args = [
            "butler",
            "validate",
            os.path.abspath(os.path.join(OUTPUT_DIR_BASE, channel)),
        ]

        if CHANNEL_WIN in channel:
            args.append("--platform")
            args.append("windows")

        if CHANNEL_LINUX in channel:
            args.append("--platform")
            args.append("linux")

        ret = subprocess.call(args)

        if ret != 0:
            print(f"ERROR: butler returned non-zero exit code {ret}")
            input("Press enter to continue or Ctrl+C to cancel further validations")


def main():
    # TODO: clean up this parameter tree

    if "--help" in sys.argv:
        print("""
        Compilation and upload script for itch.io
        
        Options:
        
        --help          Print this help and exit
        --push          Push all compiled channels using butler
        --dry-run       Don't actually push, just print what would be pushed
        --validate      Run butler in validation mode on all compiled channels
        --clean         Remove all files in output directory. Usually not necessary
        --beta          Mark all compilations in this run as beta
        --server        Also compile the server as well. Takes longer
        """)
        return

    if "--push" in sys.argv:
        print("Pushing using butler")
        push("--dry-run" in sys.argv)
        return

    if "--validate" in sys.argv:
        print("Validating using butler")
        validate()
        return

    if "--clean" in sys.argv:
        print("Cleaning up...")
        shutil.rmtree(OUTPUT_DIR_BASE, ignore_errors=True)
        print("Successfully cleaned up!")
        return

    beta = "--beta" in sys.argv
    if compile_dist(False, beta) != 0:
        return

    if "--server" in sys.argv:
        compile_dist(True, beta)


if __name__ == '__main__':
    main()
