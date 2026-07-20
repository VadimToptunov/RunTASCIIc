# RunTASCIIc

A tiny "digital rain" screensaver, written as a Python GUI exercise.

It opens a full-screen black window, picks a random colour and a random visual
mode, and streams characters down the screen. Press **any key** to lock the
screen and quit.

Originally a Python 2 / Tkinter toy; now rewritten for **Python 3** and runs on
macOS and Linux (and Windows too).

## Modes

- `unicode` — glyphs from the Runic, Georgian, Tibetan, Thai and Khmer blocks
- `ascii` — random printable ASCII
- `binary` — a stream of `0`, `1` and spaces
- `slash` — slashes and assorted symbols

## Requirements

- Python 3 with Tk (the `tkinter` module). On macOS the system Python includes
  it; with Homebrew Python install it via `brew install python-tk`. On Debian/
  Ubuntu: `sudo apt install python3-tk`.

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
