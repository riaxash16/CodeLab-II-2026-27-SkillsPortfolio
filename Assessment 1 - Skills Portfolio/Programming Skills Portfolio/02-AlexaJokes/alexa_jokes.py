"""Exercise 2 - Alexa tell me a Joke (Tkinter)."""
# AI reference: this file was written with the help of Claude (Anthropic).
 
import os
import random
import tkinter as tk
 
# The jokes file is expected in the same folder as this script
JOKES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "randomJokes.txt")
 
 
def loadJokes(path=JOKES_FILE):
    """Read the jokes file and return a list of (setup, punchline) tuples.
    Each line is split at the FIRST question mark only."""
    jokes = []
    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if "?" in line:
                setup, punchline = line.split("?", 1)
                jokes.append((setup + "?", punchline.strip()))
    return jokes
 
 
class JokeApp:
    def __init__(self, root, jokes):
        self.root = root
        self.jokes = jokes
        self.current = None  # the (setup, punchline) being shown
 
        self.root.geometry("520x300")
 
        tk.Label(root, text="Joke Assistant",
                 font=("Arial", 18, "bold")).pack(pady=10)
 
        self.setup_label = tk.Label(root, text="", wraplength=480,
                                    font=("Arial", 13))
        self.setup_label.pack(pady=10)
 
        self.punchline_label = tk.Label(root, text="", wraplength=480,
                                        font=("Arial", 13, "italic"), fg="blue")
        self.punchline_label.pack(pady=5)
 
        self.alexa_button = tk.Button(root, text="Alexa tell me a Joke",
                                      width=22, command=self.tellJoke)
        self.alexa_button.pack(pady=4)
 
        self.punchline_button = tk.Button(root, text="Show Punchline",
                                          width=22, state="disabled",
                                          command=self.showPunchline)
        self.punchline_button.pack(pady=4)
 
        self.next_button = tk.Button(root, text="Next Joke", width=22,
                                     state="disabled", command=self.tellJoke)
        self.next_button.pack(pady=4)
 
        tk.Button(root, text="Quit", width=22,
                  command=root.destroy).pack(pady=4)
 
    def tellJoke(self):
        """Pick a random joke (different from the last one) and show the setup."""
        choices = [joke for joke in self.jokes if joke != self.current]
        self.current = random.choice(choices or self.jokes)
        self.setup_label.config(text=self.current[0])
        self.punchline_label.config(text="")
        self.punchline_button.config(state="normal")
        self.next_button.config(state="normal")
 
    def showPunchline(self):
        """Show the punchline below the setup."""
        if self.current:
            self.punchline_label.config(text=self.current[1])
            self.punchline_button.config(state="disabled")
 
 
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Alexa tell me a Joke")
    try:
        JokeApp(root, loadJokes())
        root.mainloop()
    except FileNotFoundError:
        print(f"Could not find {JOKES_FILE}. Put randomJokes.txt next to this script.")
        root.destroy()