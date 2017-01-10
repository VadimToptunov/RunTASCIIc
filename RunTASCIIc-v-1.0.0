#"__author__" == "Vadim Toptunov"
# "__name__" = "RunThASCIIc-v1.0.0"
"""
RunThASCIIc-v1.0.0

This screensaver was constructed by me not only just for fun, but also as an excercise for
 GUI programming on Python.

 The screensaver opens a full-screen GUI window (black), randomly chooses a colour for text,
 randomly chooses version and shows you some random characters printed. It can be closed with any key pressed.

 The project will be improved in such ways:

 1. It will lock the screen for Linux if you do nothing;
 2. It will get the 3rd version, where random Python or file with some other extension
   will be shown as a text in the GUI window.
"""

import random
import string
import sys
from Tkinter import *
import time


def key(event):
    # Closes the app if any key is pressed.
    root.destroy()

root = Tk() # Run Tkinter
root.attributes('-fullscreen', True) # Run the window in full-screen mode
root.bind("<Key>", key) # Bind the press of any key

color = random.choice(['red', 'green', 'blue', 'violet', 'white', 'yellow']) # Set random color
text = Text(root, font="Courier 20", bg="Black", fg=color) # Create text and text parameters
text.pack(expand=True, fill="both")


def unicode_chars():
    # Random characters from Runic, Georgian, Tibetian, Thai and Khmer alphabets
    # are printed in the GUI window. The text is auto-scrolled.
    r1 = range(0x16a0, 0x16f0)  # Runic unicode
    r2 = range(0x10a0, 0x10c0)  # Georgian unicode
    r3 = range(0x0f00, 0x0f6c)  # Tibetian unicode
    r4 = range(0x0e00, 0x0e50)  # Thai unicode
    r5 = range(0x1780, 0x17dd)  # Khmer unicode

    random_integer = random.randint(1, 90)

    chars = map(unichr, r1 + r2 + r3 + r4 + r5)
    random_word = u''.join([random.choice(chars) for i in range(random_integer)])
    random_word = random_word + "\n"
    random_word = random_word.encode('utf-8')
    text.insert(END, random_word)
    text.see("end")
    text.after(500, unicode_chars)


def random_chars():
    # Random ASCII chars are chosen and printed in the GUI window. The window is auto-scrolling.
    rand_int = random.randint(1, 90)
    random_word_print = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits \
                                              + string.punctuation) for x in range(rand_int))

    random_word_print = random_word_print + "\n"

    text.insert(END, random_word_print)
    text.see("end")
    text.after(500, random_chars)


def random_version_choice():
    # Chooses random version to show
    version = random.choice(['v1', 'v2'])

    if version == 'v1':
        # If version 1 is chosen, then random chars from Thai, Georgian and some other alphabets
        # are shown in the window
        text.after(500, unicode_chars)
        root.mainloop()

    elif version == 'v2':
        # If version 2 is chosen, then random ASCII chars are printed in the window
        text.after(500, random_chars)
        root.mainloop()

    else:
        # version 3 is coming. It would show code from some python files and files from other extensions
        pass

if __name__ == "__main__":
    random_version_choice()
