#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RunTASCIIc -- a tiny "digital rain" screensaver.

Opens a full-screen black window, picks a colour and a visual mode, and either
rains glyphs down in falling columns (Matrix-style) or streams random lines of
text. Press any key to lock the screen and quit.

Originally a Python 2 / Tkinter exercise; rewritten for Python 3 to run on
macOS and Linux (and Windows too).

Usage:
    python3 runtasciic.py                      # random mode + colour
    python3 runtasciic.py --mode rain --color green
    python3 runtasciic.py --mode binary
    python3 runtasciic.py --no-lock            # don't lock the screen on exit
"""

import argparse
import platform
import random
import string
import subprocess
import tkinter as tk
import tkinter.font as tkfont

__author__ = "Vadim Toptunov"
__version__ = "2.1.0"

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

# Base RGB used to tint the rain (and its bright head).
COLOR_RGB = {
    "red": (255, 60, 60),
    "green": (0, 255, 70),
    "blue": (90, 130, 255),
    "violet": (200, 120, 255),
    "white": (235, 235, 235),
    "yellow": (255, 235, 60),
    "cyan": (60, 255, 235),
    "orange": (255, 160, 40),
}

MODES = ("rain", "unicode", "ascii", "binary", "slash")


def _unicode_pool():
    """Every printable code point from the exotic blocks above, as a string."""
    chars = []
    for start, end in UNICODE_RANGES:
        for code in range(start, end):
            ch = chr(code)
            if ch.isprintable():
                chars.append(ch)
    return "".join(chars)


def rain_gradient(base, length):
    """A list of `length` hex colours: bright/near-white head fading to dark.

    Index 0 is the head (base blended toward white); later indices fade the
    base colour toward black along the trailing tail.
    """
    r, g, b = base
    colors = [f"#{int(r + (255 - r) * 0.75):02x}"
              f"{int(g + (255 - g) * 0.75):02x}"
              f"{int(b + (255 - b) * 0.75):02x}"]
    for i in range(1, length):
        # fade from full brightness (i==1) down to ~10% at the tail
        f = 1.0 - (i - 1) / max(length - 1, 1) * 0.9
        colors.append(f"#{int(r * f):02x}{int(g * f):02x}{int(b * f):02x}")
    return colors


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
    """A full-screen Tkinter window: Matrix-style rain or streaming text."""

    MAX_LINES = 200          # cap the text buffer so memory stays bounded
    MAX_LINE_LEN = 140       # longest generated line
    RAIN_INTERVAL = 70       # ms per rain frame
    RAIN_FONT_SIZE = 20

    def __init__(self, mode=None, color=None, lock=True):
        self.lock = lock
        self._unicode_chars = _unicode_pool()

        # text modes: name -> (generator, interval_ms)
        self._text_modes = {
            "unicode": (self._gen_unicode, 250),
            "ascii": (self._gen_ascii, 250),
            "binary": (self._gen_binary, 120),
            "slash": (self._gen_slash, 120),
        }

        self.mode = mode if mode in MODES else random.choice(MODES)
        self.color_name = color if color in COLORS else random.choice(COLORS)

        self.root = tk.Tk()
        self.root.title(f"RunTASCIIc v{__version__}")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Key>", self._on_key)

        self._after_id = None
        if self.mode == "rain":
            self._build_rain()
        else:
            self._build_text()

    # -- text renderer -----------------------------------------------------

    def _build_text(self):
        self.text = tk.Text(
            self.root,
            font="Courier 20",
            bg="black",
            fg=self.color_name,
            bd=0,
            highlightthickness=0,
            cursor="none",
            wrap="char",
        )
        self.text.pack(expand=True, fill="both")

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

    def _tick(self):
        generate, interval = self._text_modes[self.mode]
        self.text.insert(tk.END, generate() + "\n")
        self._trim()
        self.text.see(tk.END)
        self._after_id = self.root.after(interval, self._tick)

    def _trim(self):
        """Delete the oldest lines once the buffer exceeds MAX_LINES."""
        last = int(self.text.index("end-1c").split(".")[0])
        if last > self.MAX_LINES:
            self.text.delete("1.0", f"{last - self.MAX_LINES}.0")

    # -- rain renderer -----------------------------------------------------

    def _build_rain(self):
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        self.canvas = tk.Canvas(
            self.root, bg="black", bd=0, highlightthickness=0, cursor="none"
        )
        self.canvas.pack(expand=True, fill="both")

        self.rain_font = tkfont.Font(
            family="Courier", size=self.RAIN_FONT_SIZE, weight="bold"
        )
        self.cell_w = max(self.rain_font.measure("W"), 8)
        self.cell_h = max(self.rain_font.metrics("linespace"), 8)
        self.rows = self.height // self.cell_h + 2
        self.base = COLOR_RGB.get(self.color_name, COLOR_RGB["green"])

        # One falling drop per column; each item is anchored at the column's x,
        # so glyph width never breaks column alignment.
        self._columns = []
        n_cols = self.width // self.cell_w
        for i in range(n_cols):
            self._columns.append(self._new_column(i, warm_start=True))

    def _new_column(self, index, warm_start=False):
        trail = random.randint(6, 24)
        start = -random.randint(0, self.rows) if warm_start else -random.randint(0, trail)
        return {
            "index": index,
            "x": index * self.cell_w + self.cell_w // 2,
            "y": start,                       # head row (may be above screen)
            "trail": trail,
            "step": random.choice((1, 1, 2, 2, 3)),  # ticks per row -> speed
            "items": [],                      # canvas ids, oldest first
            "colors": rain_gradient(self.base, trail),
        }

    def _rain_tick(self):
        self._frame += 1
        c = self.canvas
        for i, col in enumerate(self._columns):
            if self._frame % col["step"] != 0:
                continue

            row = col["y"]
            col["y"] += 1
            item = c.create_text(
                col["x"], row * self.cell_h,
                text=random.choice(self._unicode_chars),
                fill=col["colors"][0],
                font=self.rain_font,
                anchor="n",
            )
            col["items"].append(item)

            # keep only the trail; drop the glyph that fell off the tail
            while len(col["items"]) > col["trail"]:
                c.delete(col["items"].pop(0))

            # recolour the trail: head bright, tail fading to dark
            n = len(col["items"])
            for j, it in enumerate(col["items"]):
                dist = (n - 1) - j          # 0 == head
                c.itemconfigure(it, fill=col["colors"][min(dist, col["trail"] - 1)])

            # recycle the column once its head is well past the bottom
            if row * self.cell_h > self.height + col["trail"] * self.cell_h:
                for it in col["items"]:
                    c.delete(it)
                self._columns[i] = self._new_column(col["index"])

        self._after_id = self.root.after(self.RAIN_INTERVAL, self._rain_tick)

    # -- lifecycle ---------------------------------------------------------

    def _on_key(self, _event):
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
        if self.lock:
            lock_screen()
        self.root.destroy()

    def run(self):
        if self.mode == "rain":
            self._frame = 0
            self._after_id = self.root.after(self.RAIN_INTERVAL, self._rain_tick)
        else:
            _, interval = self._text_modes[self.mode]
            self._after_id = self.root.after(interval, self._tick)
        self.root.mainloop()


def parse_args():
    parser = argparse.ArgumentParser(
        description="RunTASCIIc -- a tiny digital-rain screensaver."
    )
    parser.add_argument(
        "--mode",
        choices=MODES,
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
