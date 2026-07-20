#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RunTASCIIc -- a tiny "digital rain" screensaver.

Opens a full-screen black window, picks a random colour and a random visual
mode, and streams characters down the screen. Press any key to lock the screen
and quit.

Originally a Python 2 / Tkinter exercise; rewritten for Python 3 to run on
macOS and Linux (and Windows too).

Usage:
    python3 runtasciic.py
    python3 runtasciic.py --mode binary --color green
    python3 runtasciic.py --no-lock        # don't lock the screen on exit
"""

import argparse
import platform
import random
import string
import subprocess
import tkinter as tk

__author__ = "Vadim Toptunov"
__version__ = "2.0.0"

BANNER = r'''
88888888ba                     888888888888   db        ad88888ba    ,ad8888ba,  88 88   ,ad8888ba,
88      "8b                         88       d88b      d8"     "8b  d8"'    `"8b 88 88  d8"'    `"8b
88      ,8P                         88      d8'`8b     Y8,         d8'           88 88 d8'
88aaaaaa8P' 88       88 8b,dPPYba,  88     d8'  `8b    `Y8aaaaa,   88            88 88 88
88""""88'   88       88 88P'   `"8a 88    d8YaaaaY8b     `"""""8b, 88            88 88 88
88    `8b   88       88 88       88 88   d8""""""""8b          `8b Y8,           88 88 Y8,
88     `8b  "8a,   ,a88 88       88 88  d8'        `8b Y8a     a8P  Y8a.    .a8P 88 88  Y8a.    .a8P
88      `8b  `"YbbdP'Y8 88       88 88 d8'          `8b "Y88888P"    `"Y8888Y"'  88 88   `"Y8888Y"'
'''


# Unicode blocks that produce good-looking, glyph-rich noise.
UNICODE_RANGES = (
    (0x16A0, 0x16F0),  # Runic
    (0x10A0, 0x10C0),  # Georgian
    (0x0F00, 0x0F6C),  # Tibetan
    (0x0E00, 0x0E50),  # Thai
    (0x1780, 0x17DD),  # Khmer
)

COLORS = ("red", "green", "blue", "violet", "white", "yellow", "cyan", "orange")


def _unicode_pool():
    """Every printable code point from the exotic blocks above, as a string."""
    chars = []
    for start, end in UNICODE_RANGES:
        for code in range(start, end):
            ch = chr(code)
            if ch.isprintable():
                chars.append(ch)
    return "".join(chars)


def lock_screen():
    """Best-effort screen lock. Tries platform-appropriate commands in order.

    Returns True if one succeeded, False otherwise. Never raises.
    """
    system = platform.system()

    if system == "Darwin":
        candidates = [
            ["/System/Library/CoreServices/Menu Extras/User.menu"
             "/Contents/Resources/CGSession", "-suspend"],
            ["pmset", "displaysleepnow"],
        ]
    elif system == "Linux":
        candidates = [
            ["loginctl", "lock-session"],
            ["xdg-screensaver", "lock"],
            ["gnome-screensaver-command", "-l"],
            ["dm-tool", "lock"],
        ]
    elif system == "Windows":
        candidates = [["rundll32.exe", "user32.dll,LockWorkStation"]]
    else:
        candidates = []

    for cmd in candidates:
        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except (OSError, subprocess.SubprocessError):
            continue
    return False


class Screensaver:
    """A full-screen Tkinter window that streams random text downward."""

    MAX_LINES = 200          # cap the text buffer so memory stays bounded
    MAX_LINE_LEN = 140       # longest generated line

    def __init__(self, mode=None, color=None, lock=True):
        self.lock = lock
        self._unicode_chars = _unicode_pool()

        # name -> (generator, interval_ms)
        self._modes = {
            "unicode": (self._gen_unicode, 250),
            "ascii": (self._gen_ascii, 250),
            "binary": (self._gen_binary, 120),
            "slash": (self._gen_slash, 120),
        }

        self.mode = mode if mode in self._modes else random.choice(list(self._modes))
        chosen_color = color if color in COLORS else random.choice(COLORS)

        self.root = tk.Tk()
        self.root.title(f"RunTASCIIc v{__version__}")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Key>", self._on_key)

        self.text = tk.Text(
            self.root,
            font="Courier 20",
            bg="black",
            fg=chosen_color,
            bd=0,
            highlightthickness=0,
            cursor="none",
            wrap="char",
        )
        self.text.pack(expand=True, fill="both")

        self._after_id = None

    # -- content generators ------------------------------------------------

    def _gen_unicode(self):
        n = random.randint(1, self.MAX_LINE_LEN)
        return "".join(random.choice(self._unicode_chars) for _ in range(n))

    def _gen_ascii(self):
        alphabet = (
            string.ascii_letters + string.digits + string.punctuation + "   "
        )
        n = random.randint(1, self.MAX_LINE_LEN)
        return "".join(random.choice(alphabet) for _ in range(n))

    def _gen_binary(self):
        n = random.randint(1, self.MAX_LINE_LEN)
        return "".join(random.choice("01 ") for _ in range(n))

    def _gen_slash(self):
        symbols = r"/\?XO|~<>[]  "
        n = random.randint(1, self.MAX_LINE_LEN)
        return "".join(random.choice(symbols) for _ in range(n))

    # -- animation loop ----------------------------------------------------

    def _tick(self):
        generate, interval = self._modes[self.mode]
        self.text.insert(tk.END, generate() + "\n")
        self._trim()
        self.text.see(tk.END)
        self._after_id = self.root.after(interval, self._tick)

    def _trim(self):
        """Delete the oldest lines once the buffer exceeds MAX_LINES."""
        last = int(self.text.index("end-1c").split(".")[0])
        if last > self.MAX_LINES:
            self.text.delete("1.0", f"{last - self.MAX_LINES}.0")

    # -- lifecycle ---------------------------------------------------------

    def _on_key(self, _event):
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
        if self.lock:
            lock_screen()
        self.root.destroy()

    def run(self):
        _, interval = self._modes[self.mode]
        self._after_id = self.root.after(interval, self._tick)
        self.root.mainloop()


def parse_args():
    parser = argparse.ArgumentParser(
        description="RunTASCIIc -- a tiny digital-rain screensaver."
    )
    parser.add_argument(
        "--mode",
        choices=("unicode", "ascii", "binary", "slash"),
        help="Visual mode (default: random).",
    )
    parser.add_argument(
        "--color",
        choices=COLORS,
        help="Text colour (default: random).",
    )
    parser.add_argument(
        "--no-lock",
        action="store_true",
        help="Do not lock the screen when exiting.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print(BANNER)
    print(f"RunTASCIIc v{__version__} -- press any key to exit.")
    Screensaver(mode=args.mode, color=args.color, lock=not args.no_lock).run()


if __name__ == "__main__":
    main()
