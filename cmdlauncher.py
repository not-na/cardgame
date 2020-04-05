#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
#  
#  Copyright 2020 notna <notna@apparat.org>
#  
#  This file is part of cardgame-cmdlauncher.
#
#  cardgame-cmdlauncher is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  cardgame-cmdlauncher is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with cardgame-cmdlauncher.  If not, see <http://www.gnu.org/licenses/>.

import os
import platform
import sys
import subprocess

import time
import re
import queue
import traceback
import shlex
import threading
import string

from abc import ABCMeta, abstractmethod

import curses
import _curses

import psutil

PAGELENGTH = 4

ALLOW_DEBUG_EVAL = True

PROCINFO_UPDATEINTERVAL = 0.5  # Seconds
AUTO_REDRAW_PERIOD = 2  # Seconds

VIRTUALENV = os.path.join(".", "cardgame-py")
MAIN_FILE_CLIENT = os.path.join(".", "client", "main.py")
MAIN_FILE_SERVER = os.path.join(".", "server", "main.py")

HELP_TEXT = "Help for the Cardgame CLI Launcher\n" \
            "\n" \
            "Shortcuts\n" \
            "---------\n" \
            "" \
            "h          Open this help page\n" \
            "q          Quit the CLI launcher\n" \
            "s          Spawn a new client or server\n" \
            "v          View the console of a specific process\n" \
            "i          Input a single line to the current process\n" \
            "Shift+i    Input to the current process until 'END' is typed\n" \
            "d          (Re-)build the sphinx documentation\n" \
            "r          Restart the current process, even if it already runs\n" \
            "a          Add an account for easy login\n" \
            "b          Scroll to the bottom\n" \
            "g          Toggle OpenGL Debug mode via Apitrace\n" \
            "p          Toggle Profiling\n" \
            "F3         Open a debug prompt\n" \
            "\n" \
            "Other Controls\n" \
            "--------------\n" \
            "" \
            "Arrow Keys: Scroll horizontally and vertically within an active console\n" \
            "Escape:     Cancel the current action, if possible\n"

LOG_REGEX = re.compile(r"""(?P<time>\[[0-9]{2}:[0-9]{2}:[0-9]{2}\])\      # Matches time of format [HH:MM:SS]
                       (?P<tag>\[(?P<plugin>\w+)/(?P<severity>[A-Z]+)\])\ # Matches plugin/severity +
                       (?P<msg>.*$)                                       # Matches message
                       """,
                       re.VERBOSE)

if platform.system() == "Linux":
    COMMAND_SPHINXDOC = ["bash", "./build_sphinxdocs.sh"]
    COMMAND_APITRACE = ["apitrace", "trace", "--output", "cardgame_apitrace.trace"]
    PYTHON_BINARY = os.path.abspath(os.path.join(VIRTUALENV, "bin", "python"))
elif platform.system() == "Windows":
    COMMAND_SPHINXDOC = ["build_sphinxdocs.bat"]
    COMMAND_AUTHSERVER = ["start_authserver.bat"]
    COMMAND_APITRACE = None  # Not supported yet
    PYTHON_BINARY = os.path.abspath(os.path.join(VIRTUALENV, "Scripts", "python.exe"))
else:
    print(f"The Cardgame CLI Launcher does not support {platform.system()} yet."
          f"Please file a bug report under https://github.com/not-na/cardgame/issues")
    sys.exit(1)

LOGIN_COOLDOWN = 60  # seconds

# Globals:
# launcher, procs, clients, servers, docs
# C_RED, C_GREEN, C_YELLOW

# Dummy definitions for IDE
launcher = procs = clients = servers = docs = cur_proc = None
redraw = console_redraw = True
C_RED = C_GREEN = C_YELLOW = None
STYLE_SEVERITY = {}

# Style definitions for log messages
LOG_STYLES = {
    "time": curses.A_DIM,
    "tag": 0,
    "plugin": 0,
    "msg": 0,
}


# Helper Functions

def gen_new_id(pool, start=1):
    out = start

    while out in pool:  # Count up until a free slot is found
        out += 1

    return out


# Sub Process Classes

class SubProcess(object, metaclass=ABCMeta):
    def __init__(self, sid, name):
        self.sid = sid
        self.name = name

        self.pid = None
        self.proc = None
        self.running = False

        self.stdout_lines = []

        self.scroll_v = 0
        self.scroll_v_lock = True
        self.scroll_h = 0

        # PSUtil cache
        self.ps_cpu_percent = 0
        self.ps_ram_mb = 0
        self.ps_create_time = 0
        self.ps_last_update = 0
        self._ps_virgin = True  # Has not been populated yet

    def start(self):
        self.pid = self._launch()  # Trigger launch

        if self.pid == -1:  # Start failed, no process created
            return False

        self.proc = psutil.Process(self.pid)
        return True  # Success

    def add_stdout(self, line, attr=None):
        self.stdout_lines.append([str(line), attr])  # Add to buffer

        global console_redraw
        console_redraw = True

        if self.scroll_v != 0 and self.scroll_v_lock:
            self.scroll_v += 1

    @abstractmethod
    def refresh_stdout(self):
        pass

    @abstractmethod
    def write_to_stdin(self, msg):
        pass

    @abstractmethod
    def _launch(self):
        pass

    @abstractmethod
    def kill(self):
        pass


class PopenSubProcess(SubProcess):
    def __init__(self, sid, name, args):
        super().__init__(sid, name)

        self.args = args

        self.popen = None

        self._stdout_queue = queue.Queue()

    def get_params(self):
        return [["exit", "0"], os.environ]  # Must be a tuple of (cmdline, env)

    def _launch(self):
        try:
            # Try to get parameters
            cmdline, env = self.get_params()
        except Exception:
            # Gather error message and display it
            errstring = traceback.format_exc()
            launcher.add_stdout("Error while gathering parameters:", curses.A_BOLD | C_RED)
            for line in errstring.split("\n"):
                launcher.add_stdout(line, C_RED)

            return -1  # Indicate fail to start()

        # Create the subprocess
        try:
            self.popen = subprocess.Popen(cmdline,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          stdin=subprocess.PIPE,
                                          env=env,
                                          )
            self.running = True
        except OSError:
            launcher.add_stdout("Could not start subprocess: ", curses.A_BOLD | C_RED)
            for l in traceback.format_exc().split("\n"):
                launcher.add_stdout(l, C_RED)
            return -1

        global redraw
        redraw = True

        # Start stdout and stderr capture threads
        # Loosely based on https://stackoverflow.com/a/4896288/
        self._stdout_thread = threading.Thread(name=f"stdout Thread of {self.name}",
                                               target=self._stdout_async,
                                               )
        self._stdout_thread.daemon = True
        self._stdout_thread.start()

        # stderr
        self._stderr_thread = threading.Thread(name=f"stderr Thread of {self.name}",
                                               target=self._stderr_async,
                                               )
        self._stderr_thread.daemon = True
        self._stderr_thread.start()

        return self.popen.pid  # Return the pid to start()

    def kill(self):
        self.popen.terminate()
        self.add_stdout("Killed child process using SIGTERM", curses.A_BOLD | C_RED)

        global redraw
        redraw = True

    def write_to_stdin(self, msg):
        if self.popen.stdin is not None:
            try:
                self.popen.stdin.write(msg.encode("utf-8"))
                self.popen.stdin.flush()
            except Exception:
                self.add_stdout("Could not write to input", C_RED | curses.A_BOLD)
        else:
            self.add_stdout("Input not active!", C_RED)

    def refresh_stdout(self):
        # Get lines queued from the I/O threads
        while not self._stdout_queue.empty():  # Runs in an infinite loop until the queue is empty
            try:
                line, attr = self._stdout_queue.get_nowait()
            except queue.Empty:
                break  # Should be rare due to the loop condition
            else:
                self.add_stdout(line.decode(sys.stdout.encoding).replace("\r", ""), attr)

        # Check if the process is still running and we don't know it yet
        if self.running and self.popen.poll() is not None:
            self.running = False  # Set the flag to prevent multiple notifications

            global redraw
            redraw = True

            returncode = self.popen.returncode
            if returncode == 0:
                # Normal exit
                self.add_stdout("Process exited with return code 0", C_GREEN)
            else:
                self.add_stdout(f"Process exited with return code {returncode}", C_RED)

    def _stdout_async(self):
        # Will be run in a separate thread to collect stdout data
        stdout = self.popen.stdout

        for line in iter(stdout.readline, b""):
            self._stdout_queue.put([line, None])

        stdout.close()  # Properly close the queue if the iteration stops

    def _stderr_async(self):
        # Will be run in a separate thread to collect stderr data
        stderr = self.popen.stderr

        for line in iter(stderr.readline, b""):
            self._stdout_queue.put([line, C_RED])

        stderr.close()  # Properly close the queue if the iteration stops


class ClientSubProcess(PopenSubProcess):
    def __init__(self, sid, name, args, account):
        super().__init__(sid, name, args)

        self.serverid = None
        self.account = account

    def get_params(self):
        # Store the command line base, everything else is appended
        if not profile:
            cmdline = [PYTHON_BINARY, "-u", "-O", MAIN_FILE_CLIENT]
        else:
            cmdline = [PYTHON_BINARY, "-u", "-O", "-m", "cProfile", "-o", "cardgame_profile.txt", "-s", "cumtime", MAIN_FILE_CLIENT, "--client"]

        # Add authentication token if there is an associated account
        if self.account is not None:
            cmdline.extend(["--username", self.account.name,
                            "--pwd", self.account.pwd,
                            ])

        cmdline.extend(self.args)

        if gl_trace:
            cmdline = [*COMMAND_APITRACE, *cmdline]

        env = {}
        env.update(os.environ)
        # Future env updates go here

        return cmdline, env


class ServerSubProcess(PopenSubProcess):
    def get_params(self):
        cmdline = [PYTHON_BINARY, "-u", "-O", MAIN_FILE_SERVER]
        cmdline.extend(self.args)
        #cmdline.extend(["--authserver", self.authserver])

        env = {}
        env.update(os.environ)
        # Future env updates go here

        return cmdline, env


class SphinxDocumentationSubProcess(PopenSubProcess):
    def __init__(self, sid, name, args):
        super().__init__(sid, name, args)

        self.serverid = "N/A"

    def get_params(self):
        cmdline = COMMAND_SPHINXDOC
        cmdline.extend(self.args)

        env = {}
        env.update(os.environ)
        # Future env updates go here

        return cmdline, env


class LauncherSubProcess(SubProcess):
    def _launch(self):
        # Dummy method to fit standard interface
        self.add_stdout("Launched launcher...")
        self.running = True
        return os.getpid()

    def refresh_stdout(self):
        pass  # No queue pulling required

    def kill(self):
        self.add_stdout("Cannot kill Launcher, use q to quit.", C_RED)

    def write_to_stdin(self, msg):
        self.add_stdout("STDIN: "+msg)


# Account Class

class Account(object):
    def __init__(self, aid, name, pwd):
        self.err = None

        self.aid = aid
        self.name = name
        self.pwd = pwd

        self.lasterr = 0

    def get_state(self):
        """if self.session.is_logged_in:
            return C_GREEN
        elif self.session._token is None:  # No token at all
            return C_RED
        elif time.time() - self.lasterr > LOGIN_COOLDOWN:  # Session expired
            try:
                self.session.login()
            except Exception:
                # Print the error message to the launcher console
                launcher.add_stdout("Exception during account re-authentication:", curses.A_BOLD | C_RED)
                for l in traceback.format_exc().split("\n"):
                    launcher.add_stdout(l, C_RED)
                launcher.add_stdout(f"Next check in {LOGIN_COOLDOWN}s", curses.A_BOLD | C_RED)
                self.lasterr = time.time()

            if self.session.valid_until >= time.time():
                return C_GREEN
            else:
                return C_RED
        else:
            return C_RED  # If re-auth has been skipped due to time-out"""
        return C_YELLOW

    def get_displayname(self):
        return self.name


def show_help(stdscr):
    # Starts a temporary loop inside the main loop
    stdscr.clear()
    n = 0

    for line in HELP_TEXT.split("\n"):
        stdscr.addstr(n, 0, line)
        n += 1

    run = True
    while run:
        h, w = stdscr.getmaxyx()

        stdscr.addstr(h-1, 0, "Press q to exit this help menu")
        stdscr.chgat(h-1, 0, -1, curses.A_REVERSE)

        c = stdscr.getch()
        if c == curses.ERR:
            curses.napms(1000//30)  # Low FPS, acceptable here
        elif c == ord("q"):
            run = False

    global redraw
    redraw = True


def main(stdscr):
    global C_GREEN, C_YELLOW, C_RED, STYLE_SEVERITY
    global launcher, procs, clients, servers, docs, cur_proc, redraw, console_redraw, gl_trace, profile

    s_time = time.time()

    # Initialization of curses styles/colors
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_RED, -1)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

    C_GREEN = curses.color_pair(1)
    C_YELLOW = curses.color_pair(2)
    C_RED = curses.color_pair(3)

    STYLE_SEVERITY = {
        "DEBUG": curses.A_DIM,
        "INFO": 0,
        "WARNING": C_YELLOW,
        "ERROR": C_RED,
        "CRITICAL": curses.color_pair(4)  # Red with black background
    }

    # Curses initialization
    stdscr.clear()
    stdscr.nodelay(True)
    stdscr.leaveok(True)

    gl_trace = False
    profile = False

    # Sub Process registries
    # Clients
    clients = {}
    client_count = 1

    # Servers
    servers = {}
    server_count = 1

    # All subprocesses
    procs = {}

    # Accounts
    accounts = {}
    #auth_email = ""

    # Initialize Launcher fake subprocess
    launcher = LauncherSubProcess(0, "Launcher")
    launcher.start()
    procs[launcher.sid] = launcher

    # Initialize dormant sphinx docs subprocess
    docs = SphinxDocumentationSubProcess(1, "Docs", [])
    procs[docs.sid] = docs
    clients[docs.sid] = docs

    # Pagination state
    client_pg = 1
    server_pg = 1
    account_pg = 1

    # Various input state variables, used to present and validate input
    in_prompt = ""
    in_mode = "char"
    in_type = "str"
    in_out = ""
    in_str = ""
    in_status = ""
    #auth_server = DEFAULT_AUTHSERVER

    # Cursor position (only horizontally movable)
    curs_pos = 0, 0
    curs_indent = 0

    spawn_data = {}

    # Launcher is 0, everything else some subprocess
    selected_proc = 0
    cur_proc = procs[selected_proc]

    redraw = True
    console_redraw = True

    last_redraw = 0

    old_size = 0, 0

    run = True
    while run:
        # Poll newest screen size
        h, w = stdscr.getmaxyx()
        if (h, w) != old_size:
            redraw = True
        old_size = h, w

        # Refresh stdout of all procs
        for proc in procs.values():
            proc.refresh_stdout()

        # Refresh static elements if redraw is neccessary
        if redraw or time.time()-last_redraw >= AUTO_REDRAW_PERIOD:
            redraw = False
            last_redraw = time.time()
            console_redraw = True

            # Clear first
            stdscr.clear()

            # Top Help Line
            stdscr.addstr(0, 0, "(h)elp  (q)uit  (s)pawn process  (k)ill process  (r)estart process")
            stdscr.chgat(0, 0, -1, curses.A_REVERSE)

            # Bottom Help Line
            stdscr.addstr(h - 1, 0, "(v)iew process  write to std(i)n  (a)dd account")
            stdscr.chgat(h - 1, 0, -1, curses.A_REVERSE)

            # Client List
            client_pg = max(1, client_pg % max(1, len(clients) // PAGELENGTH + 1))

            for n, clientid in enumerate(sorted(clients.keys())[(client_pg - 1) * PAGELENGTH:client_pg * PAGELENGTH], 1):
                # Each client is 18 Chars wide
                # Client ID: 3 Chars
                stdscr.addstr(n, 0, f"{clientid:>2}", curses.A_DIM)

                # Client Name: 10 Chars
                if clients[clientid].running:
                    stdscr.addstr(n, 4, f"{clients[clientid].name:10.10}", curses.A_BOLD)
                else:
                    stdscr.addstr(n, 4, f"{clients[clientid].name:10.10}", curses.A_DIM)

                # Arrow: 1 Char
                stdscr.addch(n, 15, curses.ACS_RARROW, curses.A_BOLD)

                # Server Indicator: 2 Chars
                if clients[clientid].serverid is None:
                    sid = "X"
                else:
                    sid = clients[clientid].serverid
                stdscr.addstr(n, 16, f"{sid:>2}")

            # Client List pagination footer
            stdscr.addstr(6, 0, f"Page {client_pg} of {max(1, len(clients)//PAGELENGTH+1)}")

            # Server List
            server_pg = max(1, server_pg % max(1, len(servers) // PAGELENGTH + 1))

            for n, serverid in enumerate(sorted(servers.keys())[(server_pg - 1) * PAGELENGTH:server_pg * PAGELENGTH], 1):
                # Each server is 13 Chars wide
                # Server ID: 3 Chars
                stdscr.addstr(n, w - 15 - 13, f"{serverid:>2}", curses.A_DIM)

                # Server Name: 10 Chars
                if servers[serverid].running:
                    stdscr.addstr(n, w - 15 - 10, f"{servers[serverid].name:10.10}", curses.A_BOLD)
                else:
                    stdscr.addstr(n, w - 15 - 10, f"{servers[serverid].name:10.10}", curses.A_DIM)

            # Server List pagination footer
            stdscr.addstr(6, w - 15 - 13, f"Page {server_pg} of {max(1, len(servers)//PAGELENGTH+1)}")

            # Account List
            account_pg = max(1, account_pg % max(1, len(accounts) // PAGELENGTH + 1))
            for n, accid in enumerate(sorted(accounts.keys())[(account_pg - 1) * PAGELENGTH:account_pg * PAGELENGTH], 1):
                if accounts[accid].err is not None:
                    # TODO: prevent dropping of errors in case of multiple errors at the same time
                    in_status = accounts[accid].err
                    accounts[accid].err = None

                # Each account is 15 Chars wide
                # Account ID: 3 Chars
                stdscr.addstr(n, w - 15, f"{accid:>2} ", curses.A_DIM)

                # Account Name: 12 Chars
                stdscr.addstr(n, w - 12, f"{accounts[accid].get_displayname():12.12}", accounts[accid].get_state())

            stdscr.chgat(6, 0, -1, curses.A_REVERSE)

        # Stuff that is always refreshed

        # Refresh Usage Stats of active process
        if time.time() - cur_proc.ps_last_update > PROCINFO_UPDATEINTERVAL and cur_proc.running:
            # Updates every PROCINFO_UPDATEINTERVAL seconds and caches the data until the next update
            p = cur_proc.proc
            with p.oneshot():  # Causes data to be fetched only once for the context
                try:
                    cur_proc.ps_cpu_percent = p.cpu_percent()
                    cur_proc.ps_ram_mb = p.memory_info().rss / 1024 / 1024  # All memory in MiB
                    cur_proc.ps_create_time = p.create_time()
                    cur_proc.ps_last_update = time.time()  # Reset the timestamp
                except psutil.NoSuchProcess:
                    # Process has stopped, update running flag
                    cur_proc.running = False
                if cur_proc._ps_virgin:
                    cur_proc.ps_last_update -= max(PROCINFO_UPDATEINTERVAL - 0.1, 0.1)  # Causes second update in 100ms
                    cur_proc._ps_virgin = False

        # Draw Usage Stats of active process
        t = time.time() - cur_proc.ps_create_time
        t_h, t = divmod(t, 3600)
        t_m, t_s = divmod(t, 60)
        t_h, t_m, t_s = int(t_h), int(t_m), int(t_s)
        stdscr.addstr(7, 0, f"Console of {cur_proc.name:9.9} {cur_proc.ps_cpu_percent:5.2f}% CPU"
                            f"{cur_proc.ps_ram_mb:7.2f}MiB RAM {t_h:02}:{t_m:02}:{t_s:02}")
        stdscr.chgat(7, 0, -1, curses.A_REVERSE)

        # Optionally redraw the console window
        if console_redraw:
            console_redraw = False

            console_h = h - PAGELENGTH - 6  # 6 lines occupied by other information
            # Normalize and clamp vertical scroll
            cur_proc.scroll_v = max(0,
                                    min(
                                        len(cur_proc.stdout_lines) - console_h,
                                        cur_proc.scroll_v
                                        )
                                    )

            # Calculate h-scroll data and normalize and clamp horizontal scroll
            visible_lines = list(reversed(cur_proc.stdout_lines))[cur_proc.scroll_v:cur_proc.scroll_v + console_h]
            longest_line = max(map((lambda l: len(l[0])), visible_lines), default=0)
            cur_proc.scroll_h = max(0, min(cur_proc.scroll_h, longest_line-w))

            n = h-3
            # Iterate through the lines and draw them
            for line, attr in visible_lines:
                stdscr.addstr(n, 0, " "*w, 0)
                if attr is not None:
                    # Line has an explicit style, overrides everything else
                    stdscr.addstr(n, 0, line[cur_proc.scroll_h:cur_proc.scroll_h+w], attr)
                else:
                    # Line has no style, auto-style it
                    stdscr.addstr(n, 0, line[cur_proc.scroll_h:cur_proc.scroll_h+w])

                    # Use a regex to extract positions of different parts of the log message
                    m = LOG_REGEX.match(line)
                    if m is not None:  # In case it is not a log message
                        # Iterate through all groups and apply their corresponding style
                        for key, value in m.groupdict().items():
                            if key == "severity":
                                style = STYLE_SEVERITY.get(m.group("severity"), 0)
                            else:
                                style = LOG_STYLES.get(key, 0)

                            # Only apply the style if it is non-zero, e.g. has an effect
                            if style != 0:
                                s, e = m.span(key)
                                # Formulas below have been tested and known to work
                                stdscr.chgat(n,
                                             max(s-cur_proc.scroll_h, 0),
                                             min(w-cur_proc.scroll_h-s, e-s-max(cur_proc.scroll_h-s, 0)),
                                             style,
                                             )

                # Lines are iterated in reverse
                n -= 1

        # Input Prompt Drawing
        # IMPORTANT: has to be done last, to ensure correct cursor positioning
        stdscr.addstr(h-2, 0, " "*w)
        in_status = str(in_status)  # To prevent crashes if an int etc. is passed here
        if in_status != "":
            # Bold font for the whole length of the status
            stdscr.addstr(h-2, w-len(in_status), in_status, curses.A_BOLD)

        # Append either password prompt or normal prompt
        if in_type == "password":
            stdscr.addstr(h-2, 0, in_prompt+("*"*len(in_str)))
        else:
            stdscr.addstr(h-2, 0, in_prompt+in_str)

        if in_out != "":
            # Position the cursor
            curs_pos = (h-2, len(in_prompt+in_str) + curs_indent)
            stdscr.move(*curs_pos)
            curses.curs_set(1)
        else:
            curses.curs_set(0)

        # Input collection
        if in_mode == "char":
            c = stdscr.getch()
            if c == curses.ERR:
                curses.napms(1000//60)  # May happen, because we use nodelay mode
                # This also reduces CPU load, since the program will only wake up shortly to check input
            elif c == ord("h"):
                # Help Shortcut
                show_help(stdscr)
                pass
            elif c == ord("q"):
                # Quit
                run = False
            elif c == ord("s"):
                # Spawn Client/Server
                # Multi-staged
                # 1. Select Client/Server
                # 2. Additional parameters, e.g. account, cmdline
                stdscr.leaveok(False)

                in_prompt = "Type [c/s]: "
                in_str = ""  # Clear input buffer
                in_mode = "str"
                in_type = "spawn_select_type"
                in_out = "spawn_select_type"
                curs_indent = 0
            elif c == ord("v"):
                # View Client/Server/other subprocs
                stdscr.leaveok(False)
                in_prompt = "Console ID or 0 for Launcher: "
                in_str = ""
                in_mode = "str"
                in_type = "int"
                in_out = "view"
                curs_indent = 0
            elif c == ord("k"):
                # Kill active process
                cur_proc.kill()
            elif c == ord("i"):
                # Input data to the current console
                if selected_proc != 0:
                    stdscr.leaveok(False)
                    in_prompt = "> "
                    in_str = ""
                    in_mode = "str"
                    in_type = "str"
                    in_out = "stdin_singleline"
                    in_status = ""
                    curs_indent = 0
            elif c == ord("I"):
                # Continously input data to the current console
                if selected_proc != 0:
                    stdscr.leaveok(False)
                    in_prompt = ">> "
                    in_str = ""
                    in_mode = "str"
                    in_type = "str"
                    in_out = "stdin_multiline"
                    in_status = ""
                    curs_indent = 0
            elif c == ord("r"):
                # Restart current process
                if selected_proc != 0:
                    if cur_proc.running:
                        cur_proc.kill()
                    cur_proc.add_stdout("Restarted sub-process", curses.A_BOLD | C_GREEN)
                    cur_proc.start()
                else:
                    in_status = "Cannot restart launcher"
            elif c == ord("d"):
                # Rebuild Sphinx Docs
                if docs.running:
                    in_status = "Docs are already running"
                else:
                    docs.add_stdout("Rebuilding documentation", curses.A_BOLD | C_GREEN)
                    docs.start()
            elif c == ord("a"):
                # Add auth account
                """if HAVE_AUTHLIB:
                    stdscr.leaveok(False)
                    in_prompt = "Authserver Base-URL: "
                    in_str = ""
                    in_mode = "str"
                    in_type = "str"
                    in_out = "auth_server"
                    in_status = ""
                    curs_indent = 0
                else:"""
                in_prompt = "Account Name: "
                in_str = ""
                in_mode = "str"
                in_type = "str"
                in_out = "auth_name"
                in_status = ""
            elif c == ord("b"):
                # Scroll to the bottom
                cur_proc.scroll_v = 0
                console_redraw = True
            elif c == ord("g"):
                # Toggle OpenGL Tracing
                if COMMAND_APITRACE is None:
                    in_status = "OpenGL Trace is not available on this platform yet"
                else:
                    gl_trace = not gl_trace
                    if gl_trace:
                        in_status = "Activated OpenGL Trace"
                    else:
                        in_status = "Deactivated OpenGL Trace"
            elif c == ord("p"):
                # Toggle Profiling
                profile = not profile
                if profile:
                    in_status = "Activated Profiling"
                else:
                    in_status = "Deactivated Profiling"
            elif c == curses.KEY_LEFT:
                cur_proc.scroll_h -= 1
                console_redraw = True
                # Normalized in next frame
            elif c == curses.KEY_RIGHT:
                cur_proc.scroll_h += 1
                console_redraw = True
                # Normalized in next frame
            elif c == curses.KEY_DOWN:
                cur_proc.scroll_v -= 1
                console_redraw = True
            elif c == curses.KEY_UP:
                cur_proc.scroll_v += 1
                console_redraw = True
            elif c == curses.KEY_F3:
                stdscr.leaveok(False)
                in_prompt = "Debug key: "
                in_str = ""
                in_mode = "str"
                in_type = "str"
                in_out = "debug"
                curs_indent = 0
        elif in_mode == "str":
            try:
                c = stdscr.getkey()  # Instead of getch, since we want special keys as strings
            except _curses.error:
                c = ""

            if c == "\n":
                # Input finished, process it
                in_reset = True

                # Check in_out for target
                if in_out == "stdin_singleline":
                    # Give to stdin of active process
                    if selected_proc > 0:
                        cur_proc.write_to_stdin(in_str+"\n")
                elif in_out == "stdin_multiline":
                    if selected_proc > 0:
                        if in_str == "END":
                            in_reset = True
                        else:
                            cur_proc.write_to_stdin(in_str+"\n")
                            in_str = ""
                            in_reset = False
                elif in_out == "view":
                    if in_str == "":
                        in_status = "Invalid, cannot be empty"
                    elif int(in_str) in procs.keys():
                        selected_proc = int(in_str)
                        cur_proc = procs[selected_proc]
                        redraw = True
                        in_status = f"Selected Process: {selected_proc}"
                    else:
                        in_status = "Unknown Console ID"
                    redraw = True
                elif in_out == "spawn_select_type":
                    if in_str in "cs" and len(in_str) == 1:
                        spawn_data["type"] = in_str
                        in_reset = False
                        if in_str == "c":
                            # Client, also gets account id
                            in_prompt = "Account ID: "
                            in_str = ""
                            in_mode = "str"
                            in_type = "int"
                            in_out = "spawn_accountid"
                        else:
                            # Everything else, only gets params
                            in_reset = False
                            in_prompt = "Additional Parameters: "
                            in_str = ""
                            in_mode = "str"
                            in_type = "str"
                            in_out = "spawn_params"
                    else:
                        in_status = "Aborted, invalid type"
                elif in_out == "spawn_accountid":
                    if in_str == "" or in_str == "0":
                        spawn_data["accountid"] = None
                    else:
                        # TODO: maybe add safety checks here too
                        spawn_data["accountid"] = int(in_str)

                    in_reset = False
                    in_prompt = "Additional parameters: "
                    in_str = ""
                    in_mode = "str"
                    in_type = "str"
                    in_out = "spawn_params"
                elif in_out == "spawn_params":
                    spawn_data["args"] = shlex.split(in_str)
                    if spawn_data["type"] == "c":
                        # Game Client
                        client = ClientSubProcess(
                            gen_new_id(procs),
                            f"Client #{client_count}",
                            spawn_data["args"],
                            accounts.get(spawn_data["accountid"], None),
                        )

                        if client.start():
                            # Only increment counter if successful
                            client_count += 1
                            clients[client.sid] = client
                            procs[client.sid] = client
                            selected_proc = client.sid
                            cur_proc = client
                        else:
                            in_status = "Could not start the client"
                    elif spawn_data["type"] == "s":
                        # Game Server
                        server = ServerSubProcess(
                            gen_new_id(procs),
                            f"Server #{server_count}",
                            spawn_data["args"],
                        )
                        #server.authserver = auth_server

                        if server.start():
                            server_count += 1
                            servers[server.sid] = server
                            procs[server.sid] = server
                            selected_proc = server.sid
                            cur_proc = server
                        else:
                            in_status = "Could not start the server"
                    """elif spawn_data["type"] == "a":
                        # Auth Server
                        server = AuthserverSubProcess(
                            gen_new_id(procs),
                            f"AuthS #{server_count}",
                            spawn_data["args"]
                        )

                        if server.start():
                            server_count += 1
                            servers[server.sid] = server
                            procs[server.sid] = server
                            selected_proc = server.sid
                            cur_proc = server"""
                elif False:
                    """elif in_out == "spawn_authserver":
                    if in_str == "":
                        auth_server = DEFAULT_AUTHSERVER
                    else:
                        auth_server = in_str
                    in_reset = False
                    in_prompt = "Additional Parameters: "
                    in_str = ""
                    in_mode = "str"
                    in_type = "str"
                    in_out = "spawn_params\""""
                elif in_out == "debug":
                    if in_str == "eval":
                        in_reset = False
                        in_prompt = ">>> "
                        in_type = "str"
                        in_str = ""
                        in_out = "debug_eval"
                    else:
                        in_status = "Unknown debug code"
                elif in_out == "debug_eval":
                    # WARNING: extremely dangerous if unauthorized people can enter commands
                    if ALLOW_DEBUG_EVAL:
                        try:
                            exec(in_str)
                        except Exception:
                            launcher.add_stdout("Error during eval: ", curses.A_BOLD | C_RED)
                            for l in traceback.format_exc().split("\n"):
                                launcher.add_stdout(l, C_RED)
                elif in_out == "auth_name":
                    if in_str != "":
                        auth_name = in_str
                        in_reset = False
                        in_prompt = "Password: "
                        in_str = ""
                        in_mode = "str"
                        in_type = "password"
                        in_out = "auth_pwd"
                    else:
                        in_status = "Empty username, cancelling"
                elif in_out == "auth_pwd":
                    """if not HAVE_AUTHLIB:
                        in_status = "Auth Lib could not be loaded!\""""
                    if in_str != "":
                        acc = Account(gen_new_id(accounts), auth_name, in_str)
                        accounts[acc.aid] = acc
                        redraw = True
                else:
                    # No target specified
                    in_status = "Input target unknown, please report this"
                    launcher.add_stdout(f"DEBUG: in_out='{in_out}' in_prompt='{in_prompt}'", curses.A_BOLD | C_RED)

                # Optionally reset the in_* vars
                if in_reset:
                    in_out = ""
                    in_str = ""
                    in_mode = "char"
                    in_prompt = ""
                    stdscr.leaveok(True)

            elif c == "":
                pass

            elif c in ["KEY_BACKSPACE", "\b"]:
                if -curs_indent != len(in_str):
                    r_index = len(in_str) - 1 + curs_indent  # Index of the item to remove in in_str
                    in_str = in_str[:r_index] + in_str[r_index+1:]  # Remove the char left to the cursor

            elif in_type == "str":
                if c == "KEY_RIGHT":
                    if curs_indent < 0:
                        curs_indent += 1
                elif c == "KEY_LEFT":
                    if -curs_indent < len(in_str):
                        curs_indent -= 1
                elif c == "KEY_ESC" or c == "KEY_ESCAPE":
                    in_mode = "char"

                elif len(c) == 1 and ord(c) <= 127:  # Sort out any non-ascii characters
                    i_index = len(in_str) + curs_indent  # Index at which the char should be inserted
                    in_str = in_str[:i_index] + c + in_str[i_index:]  # Insert the new char left of the cursor

            elif in_type == "int":
                # Check for positive ints only
                if c in "0123456789":
                    i_index = len(in_str) + curs_indent
                    in_str = in_str[:i_index] + c + in_str[i_index:]
                    in_status = ""
                elif c == "KEY_RIGHT":
                    if curs_indent < 0:
                        curs_indent += 1
                elif c == "KEY_LEFT":
                    if -curs_indent < len(in_str):
                        curs_indent -= 1
                else:
                    in_status = "0-9 Only"

            elif in_type == "spawn_select_type":
                if len(in_str) == 0:
                    if c in "csa":
                        in_str += c
                        in_status = ""
                    else:
                        in_status = "c, s or a only"
                else:
                    in_status = "One Char only"

            elif in_type == "email":
                if "@" in in_str:
                    if c in string.ascii_letters+string.digits+".":
                        i_index = len(in_str) + curs_indent
                        in_str = in_str[:i_index] + c + in_str[i_index:]
                        in_status = ""
                    else:
                        in_status = "Only letters, numbers and dot after @"
                else:
                    if c in string.ascii_letters+string.digits+".+@":  # The + allows for sub-inbox support
                        i_index = len(in_str) + curs_indent
                        in_str = in_str[:i_index] + c + in_str[i_index:]
                        in_status = ""
                    else:
                        in_status = "Only letters, numbers and .+@ allowed"
                if c == "KEY_RIGHT":
                    if curs_indent < 0:
                        curs_indent += 1
                elif c == "KEY_LEFT":
                    if -curs_indent < len(in_str):
                        curs_indent -= 1

            elif in_type == "password":
                in_str += c

        else:
            in_mode = "char"

        curses.napms(1000//60)


if __name__ == "__main__":
    sys.exit(curses.wrapper(main))
