"""Exercise 2 - Alexa tell me a Joke (Tkinter)."""
# AI reference: this file was written with the understanding of this youtube video.
 
import os
import random
import tkinter as tk

HERE = os.path.dirname(os.path.abspath(__file__))
JOKES_FILE = os.path.join(HERE, "randomJokes.txt")
FAVOURITES_FILE = os.path.join(HERE, "favourites.txt")

#Colour palette
BG = "#14213d"
BUBBLE = "#00b4d8"
PUNCH = "#ffd166"
TEXT = "#f1f5ff"
DARK = "#0b132b"
MUTED = "#9db4d6"
GOOD = "#7ee08a"
BAD = "#ff7b8e"


# ---------- Logic functions (no GUI code in these) ----------

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


def pickJoke(jokes, previous=None):
    """Pick a random joke that is different from the previous one."""
    choices = [joke for joke in jokes if joke != previous]
    return random.choice(choices or jokes)


def loadFavourites(path=FAVOURITES_FILE):
    """Return saved favourites as a list of 'setup | punchline' strings."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def saveFavourites(favourites, path=FAVOURITES_FILE):
    with open(path, "w", encoding="utf-8") as file:
        for favourite in favourites:
            file.write(favourite + "\n")


def reaction(laughs, groans):
    """Alexa's comment on how the audience is reacting."""
    if laughs + groans == 0:
        return "Rate a joke and I'll learn your taste."
    if laughs > groans:
        return "Tough crowd? Not you - you're loving these!"
    if groans > laughs:
        return "Lots of groans. Dad jokes are my speciality."
    return "Perfectly balanced, as all things should be."


# ---------- GUI ----------

class JokeApp:
    def __init__(self, root, jokes):
        self.root = root
        self.jokes = jokes
        self.current = None      # (setup, punchline) on screen
        self.told = 0
        self.laughs = 0
        self.groans = 0
        self.anim_id = None      # pending after() job
        self.favourites = loadFavourites()

        root.configure(bg=BG)
        root.geometry("620x560")
        root.resizable(False, False)

        tk.Label(root, text="Alexa, tell me a joke", bg=BG, fg=TEXT,
                 font=("Segoe UI", 22, "bold")).pack(pady=(18, 0))
        self.stats = tk.Label(root, text="", bg=BG, fg=MUTED,
                              font=("Segoe UI", 10))
        self.stats.pack(pady=(0, 8))

        # Chat area
        chat = tk.Frame(root, bg=DARK)
        chat.pack(fill="both", expand=True, padx=20, pady=5)

        self.setup_bubble = tk.Label(
            chat, text="Hi! Press the button and I'll tell you a joke.",
            bg=BUBBLE, fg=DARK, wraplength=380, justify="left",
            font=("Segoe UI", 13), padx=14, pady=10)
        self.setup_bubble.pack(anchor="w", padx=15, pady=(20, 10))

        self.punch_bubble = tk.Label(
            chat, text="", bg=DARK, fg=DARK, wraplength=380, justify="left",
            font=("Segoe UI", 13, "bold"), padx=14, pady=10)
        self.punch_bubble.pack(anchor="e", padx=15, pady=10)

        self.reaction_label = tk.Label(chat, text=reaction(0, 0), bg=DARK,
                                       fg=MUTED, font=("Segoe UI", 10, "italic"))
        self.reaction_label.pack(side="bottom", pady=8)

        # Rating buttons (shown once the punchline appears)
        self.rating_frame = tk.Frame(chat, bg=DARK)
        self.rating_frame.pack(side="bottom")
        self.laugh_button = self.makeButton(self.rating_frame, "Ha ha!",
                                            self.rateLaugh, GOOD, 10)
        self.groan_button = self.makeButton(self.rating_frame, "Groan...",
                                            self.rateGroan, BAD, 10)
        self.fav_button = self.makeButton(self.rating_frame, "Save",
                                          self.saveFavourite, PUNCH, 8)
        for button in (self.laugh_button, self.groan_button, self.fav_button):
            button.pack(side="left", padx=4)
            button.config(state="disabled")

        # Required buttons
        controls = tk.Frame(root, bg=BG)
        controls.pack(pady=12)
        self.alexa_button = self.makeButton(controls, "Alexa tell me a Joke",
                                            self.tellJoke, BUBBLE, 20)
        self.alexa_button.grid(row=0, column=0, padx=5, pady=4)
        self.punchline_button = self.makeButton(controls, "Show Punchline",
                                                self.showPunchline, PUNCH, 20)
        self.punchline_button.grid(row=0, column=1, padx=5, pady=4)
        self.punchline_button.config(state="disabled")
        self.next_button = self.makeButton(controls, "Next Joke",
                                           self.tellJoke, BUBBLE, 20)
        self.next_button.grid(row=1, column=0, padx=5, pady=4)
        self.next_button.config(state="disabled")
        self.makeButton(controls, "Quit", root.destroy, BAD,
                        20).grid(row=1, column=1, padx=5, pady=4)

        self.makeButton(root, "My favourites", self.showFavourites, DARK,
                        16).pack(pady=(0, 12))
        self.updateStats()

    def makeButton(self, parent, text, command, colour, width):
        return tk.Button(parent, text=text, command=command, width=width,
                         bg=colour, fg=DARK, activebackground=TEXT,
                         disabledforeground="#5c6b8a",
                         font=("Segoe UI", 11, "bold"), relief="flat",
                         cursor="hand2", pady=4)

    def updateStats(self):
        self.stats.config(text=f"Jokes told: {self.told}   Laughs: "
                               f"{self.laughs}   Groans: {self.groans}")
        self.reaction_label.config(text=reaction(self.laughs, self.groans))

    def cancelAnimation(self):
        if self.anim_id:
            self.root.after_cancel(self.anim_id)
            self.anim_id = None

    # --- telling a joke ---

    def tellJoke(self):
        """Pick a joke and type the setup out letter by letter."""
        self.cancelAnimation()
        self.current = pickJoke(self.jokes, self.current)
        self.told += 1
        self.updateStats()
        self.setup_bubble.config(text="")
        self.punch_bubble.config(text="", bg=DARK)
        for button in (self.punchline_button, self.next_button,
                       self.laugh_button, self.groan_button, self.fav_button):
            button.config(state="disabled")
        self.next_button.config(state="normal")
        self.typeText(self.current[0], 0)

    def typeText(self, text, index):
        """Typing animation for the setup bubble."""
        self.setup_bubble.config(text=text[:index])
        if index < len(text):
            self.anim_id = self.root.after(30, self.typeText, text, index + 1)
        else:
            self.anim_id = None
            self.punchline_button.config(state="normal")

    def showPunchline(self):
        """Drumroll, then reveal the punchline below the setup."""
        if not self.current:
            return
        self.punchline_button.config(state="disabled")
        self.punch_bubble.config(bg=DARK, fg=PUNCH)
        self.drumroll(0)

    def drumroll(self, step):
        if step < 6:
            self.punch_bubble.config(text="Drumroll" + "." * (step % 4))
            self.anim_id = self.root.after(300, self.drumroll, step + 1)
        else:
            self.anim_id = None
            self.punch_bubble.config(text=self.current[1], bg=PUNCH, fg=DARK)
            for button in (self.laugh_button, self.groan_button,
                           self.fav_button):
                button.config(state="normal")

    # --- reactions and favourites ---

    def rateLaugh(self):
        self.laughs += 1
        self.laugh_button.config(state="disabled")
        self.groan_button.config(state="disabled")
        self.updateStats()

    def rateGroan(self):
        self.groans += 1
        self.laugh_button.config(state="disabled")
        self.groan_button.config(state="disabled")
        self.updateStats()

    def saveFavourite(self):
        entry = f"{self.current[0]} | {self.current[1]}"
        if entry not in self.favourites:
            self.favourites.append(entry)
            saveFavourites(self.favourites)
        self.fav_button.config(state="disabled")

    def showFavourites(self):
        """Pop-up list of saved jokes."""
        window = tk.Toplevel(self.root)
        window.title("My favourite jokes")
        window.configure(bg=BG)
        window.geometry("560x320")
        if not self.favourites:
            tk.Label(window, text="No favourites yet. Press Save on a joke you like!",
                     bg=BG, fg=TEXT, font=("Segoe UI", 12)).pack(pady=40)
            return
        box = tk.Listbox(window, bg=DARK, fg=TEXT, font=("Segoe UI", 11),
                         selectbackground=BUBBLE, relief="flat")
        for favourite in self.favourites:
            box.insert(tk.END, favourite)
        box.pack(fill="both", expand=True, padx=10, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Alexa tell me a Joke")
    try:
        JokeApp(root, loadJokes())
        root.mainloop()
    except FileNotFoundError:
        print(f"Could not find {JOKES_FILE}. Put randomJokes.txt next to this script.")
        root.destroy()