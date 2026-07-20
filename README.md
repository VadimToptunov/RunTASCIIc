# RunTASCIIc

```
88888888ba                     888888888888   db        ad88888ba    ,ad8888ba,  88 88   ,ad8888ba,
88      "8b                         88       d88b      d8"     "8b  d8"'    `"8b 88 88  d8"'    `"8b
88      ,8P                         88      d8'`8b     Y8,         d8'           88 88 d8'
88aaaaaa8P' 88       88 8b,dPPYba,  88     d8'  `8b    `Y8aaaaa,   88            88 88 88
88""""88'   88       88 88P'   `"8a 88    d8YaaaaY8b     `"""""8b, 88            88 88 88
88    `8b   88       88 88       88 88   d8""""""""8b          `8b Y8,           88 88 Y8,
88     `8b  "8a,   ,a88 88       88 88  d8'        `8b Y8a     a8P  Y8a.    .a8P 88 88  Y8a.    .a8P
88      `8b  `"YbbdP'Y8 88       88 88 d8'          `8b "Y88888P"    `"Y8888Y"'  88 88   `"Y8888Y"'
```

A tiny "digital rain" screensaver, written as a Python GUI exercise.

It opens a full-screen black window, picks a random colour and a random visual
mode, and streams characters down the screen. Press **any key** to lock the
screen and quit.

Originally a Python 2 / Tkinter toy; now rewritten for **Python 3** and runs on
macOS and Linux (and Windows too).

![RunTASCIIc in unicode mode](assets/screenshot.png)

## Contents

- [Modes](#modes)
- [Requirements](#requirements)
- [Usage](#usage)
- [How it works](#how-it-works)
- [History](#history)
- [License](#license)

## Modes

| Mode      | What it streams                                              |
|-----------|-------------------------------------------------------------|
| `unicode` | glyphs from the Runic, Georgian, Tibetan, Thai & Khmer blocks |
| `ascii`   | random printable ASCII                                       |
| `binary`  | a stream of `0`, `1` and spaces                             |
| `slash`   | slashes and assorted symbols                                 |

When no mode is given, one is picked at random.

## Requirements

- **Python 3** with Tk (the `tkinter` module).
  - **macOS** — the system Python includes it. With Homebrew Python:
    `brew install python-tk` (match your minor version, e.g. `python-tk@3.14`).
  - **Debian/Ubuntu** — `sudo apt install python3-tk`.
  - **Fedora** — `sudo dnf install python3-tkinter`.

Verify it's available:

```sh
python3 -c "import tkinter; print(tkinter.TkVersion)"
```

## Usage

```sh
python3 runtasciic.py                       # random mode + colour, locks on exit
python3 runtasciic.py --mode binary --color green
python3 runtasciic.py --no-lock             # don't lock the screen on exit
```

Options:

- `--mode {unicode,ascii,binary,slash}` — visual mode (default: random)
- `--color {red,green,blue,violet,white,yellow,cyan,orange}` — text colour (default: random)
- `--no-lock` — skip locking the screen when exiting

Press **any key** to exit. Unless `--no-lock` is passed, the screen is locked on
the way out.

## How it works

- A single `Screensaver` class owns the full-screen Tk window and a `Text`
  widget rendered in monospaced `Courier`.
- Each mode is a small generator that returns one line of characters; a
  `root.after()` loop appends a line, auto-scrolls, and reschedules itself.
- The text buffer is capped (`MAX_LINES`), so old lines are trimmed and memory
  stays bounded no matter how long it runs.
- On exit, `lock_screen()` tries platform-appropriate lock commands in order
  (macOS `CGSession`/`pmset`, Linux `loginctl`/`xdg-screensaver`/…, Windows
  `rundll32`) and never raises if none are available.

## History

Started life as a Python 2 GUI-programming exercise (`RunTASCIIc-v-1.0.3.py`).
Version 2.0.0 is a full Python 3 rewrite: class-based, cross-platform, with CLI
flags and a bounded buffer. The old file-reading mode was dropped.

## License

Provided as-is for fun and learning.
