#"__author__" == "Vadim Toptunov"
# "__name__" = "RunThASCIIc-v1.0.2"

"""
88888888ba                     888888888888   db        ad88888ba    ,ad8888ba,  88 88   ,ad8888ba,
88      "8b                         88       d88b      d8"     "8b  d8"'    `"8b 88 88  d8"'    `"8b
88      ,8P                         88      d8'`8b     Y8,         d8'           88 88 d8'
88aaaaaa8P' 88       88 8b,dPPYba,  88     d8'  `8b    `Y8aaaaa,   88            88 88 88
88""""88'   88       88 88P'   `"8a 88    d8YaaaaY8b     `"""""8b, 88            88 88 88
88    `8b   88       88 88       88 88   d8""""""""8b          `8b Y8,           88 88 Y8,
88     `8b  "8a,   ,a88 88       88 88  d8'        `8b Y8a     a8P  Y8a.    .a8P 88 88  Y8a.    .a8P
88      `8b  `"YbbdP'Y8 88       88 88 d8'          `8b "Y88888P"    `"Y8888Y"'  88 88   `"Y8888Y"'


RunTASCIIc-v1.0.2
This screensaver was constructed by me not only just for fun, but also as an excercise for
 GUI programming on Python.
 The screensaver opens a full-screen GUI window (black), randomly chooses a colour for text,
 randomly chooses version, shows you some random characters printed and locks screen. It can be closed with any key pressed.
 
 TO USE THE SCRIPT:
 
 1. Create a directory with differrent files with code (.py, .pl, .sh, .c, .h extensions), with readonly permission;
 2. Set the directory to the variable dir2walk;
 3. Run the script on your computer;
 4. PROFIT!!!
"""
import os
import random
import string
import Tkinter as tk

dir2walk = "/your/directory/with/files/"

def key(event):
    # Closes the app if any key is pressed.
    lock_screen()
    rt.destroy()
    
    
def lock_screen():
    # Locks the screen
    os_name = os.name

    if os_name == 'posix':
        try:
            os.popen("gnome-screensaver-command -l")
        except Exception as exc:
            print exc

    elif os_name == 'windows' or os_name == 'nt':
        try:
            winpath = os.environ["windir"]
            os.system(winpath + r'\system32\rundll32 user32.dll, LockWorkStation')
        except Exception as exc:
            print exc
    else:
        pass

rt = tk.Tk() # Run Tkinter
rt.title("RunTASCIIc-v.1.0.3")
rt.attributes('-fullscreen', True) # Run the window in full-screen mode
rt.bind("<Key>", key) # Bind the press of any key

color = random.choice(('red', 'green', 'blue', 'violet', 'white', 'yellow')) # Set random color
text = tk.Text(rt, font="Courier 20", bg="Black", fg=color) # Create text and text parameters
text.pack(expand=True, fill="both")

mask = random.choice(('.py', '.sh', '.h', '.c', '.pl'))

for rt, dirs, files in os.walk(dir2walk, topdown=False):
    for fil in files:
        path = os.path.join(rt, fil)
        if path.endswith(mask):
            filename = open(path, 'r')
            r = filename.readlines()
            filename.close()

def read_files():
 # The function shows a file line by line in GUI window.
    global r
    text.insert(tk.END, r[0])
    r = r[1:]
    text.after(500, read_files)
    text.see(tk.END)

def unicode_chars():
    # Random characters from Runic, Georgian, Tibetian, Thai and Khmer alphabets
    # are printed in the GUI window. The text is auto-scrolled.
    r1 = range(0x16a0, 0x16f0)  # Runic unicode
    r2 = range(0x10a0, 0x10c0)  # Georgian unicode
    r3 = range(0x0f00, 0x0f6c)  # Tibetian unicode
    r4 = range(0x0e00, 0x0e50)  # Thai unicode
    r5 = range(0x1780, 0x17dd)  # Khmer unicode

    random_integer = random.randint(1, 140)

    chars = map(unichr, r1 + r2 + r3 + r4 + r5)
    random_word = u''.join([random.choice(chars) for i in range(random_integer)])
    random_word = random_word + "\n"
    random_word = random_word.encode('utf-8')
    text.insert(tk.END, random_word)
    text.see("end")
    text.after(500, unicode_chars)


def char101():
    ch101 = random.choice(('0', '1', ' '))
    text.insert(tk.END, ch101)
    text.see("end")
    text.after(1, char101)


def slash():
    slashh = random.choice(('/', "\/", '?', 'X', 'O', '|', ' ', '~', '<', '>', '[', ']'))
    text.insert(tk.END, slashh)
    text.see("end")
    text.after(1, slash)


def random_chars():
    # Random ASCII chars are chosen and printed in the GUI window. The window is auto-scrolling.
    rand_int = random.randint(1, 140)
    random_word_print = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits \
                                              + string.punctuation) for x in range(rand_int))

    random_word_print = random_word_print + "\n"

    text.insert(tk.END, random_word_print)
    text.see("end")
    text.after(500, random_chars)


def random_version_choice():
    # Chooses random version to show
    version = random.choice(('v1', 'v2', 'v3', 'v4', 'v5'))

    if version == 'v1':
        # If version 1 is chosen, then random chars from Thai, Georgian and some other alphabets
        # are shown in the window
        text.after(500, unicode_chars)
        rt.mainloop()
    elif version == 'v2':
        # If version 2 is chosen, then random ASCII chars are printed in the window
        text.after(500, random_chars)
        rt.mainloop()
    elif version == 'v3':
        text.after(1, char101)
        rt.mainloop()
    elif version == 'v4':
        text.after(1, slash)
        rt.mainloop()

    elif version  == 'v5':
        text.after(500, read_files)
        rt.mainloop()
    else: pass
     
if __name__ == "__main__":
    random_version_choice()
