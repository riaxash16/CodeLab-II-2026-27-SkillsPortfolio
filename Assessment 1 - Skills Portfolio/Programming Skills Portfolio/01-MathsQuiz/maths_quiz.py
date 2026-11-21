"""Exercise 1 - Maths Quiz (Tkinter)."""
#AI reference: this file was written with the understanding of a youtube video.
#(10 questions, 3 difficulty levels, 2 attempts per question, ranked results).

import os
import random
import tkinter as tk
from tkinter import ttk

TOTAL_QUESTIONS = 10
TIME_LIMIT = 20  #Seconds allowed per attempt
SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "highscores.txt")
LEVEL_NAMES = {1: "Easy", 2: "Moderate", 3: "Advanced"}

#Colour palette
#All the colours are here so the whole theme can be changed in one place
BG = "#1a1b2e"
CARD = "#262842"
TEXT = "#e6e8ff"
MUTED = "#8b8fb8"
ACCENT = "#7aa2f7"
GOOD = "#7ee08a"
BAD = "#ff7b8e"
WARN = "#f5c26b"


#Logic functions
def randomInt(level):
    """Return a random number with the right number of digits for the level.
    level 1 = single digit, 2 = double digit, 3 = four digit.""" 
    #A dictionary maps each level to its (smallest, largest) number that avoids writing three separate if-blocks
    ranges = {1: (0, 9), 2: (10, 99), 3: (1000, 9999)} 
    #Unpack the pair for this level then pick a whole number in that range (random.randint includes both ends)
    low, high = ranges[level]
    return random.randint(low, high)

def decideOperation():
    """Randomly return '+' or '-'."""
    #random.choice picks one item from the list at random
    return random.choice(['+', '-']) 

def isCorrect(user_answer, correct_answer, attempt):
    """Check the answer. Return (points earned, message to show)."""
    if user_answer == correct_answer:
        #Full marks for the first try and half marks for the second
        points = 10 if attempt == 1 else 5
        return points, f"Correct! +{points} points"
    #Wrong on the first try: no points yet but there is another chance
    if attempt == 1:
        return 0, "Not quite - you get one more try!"
    #Wrong on the second try as well: no points and the answer is revealed
    return 0, f"Out of tries. The answer was {correct_answer}"


def displayResults(score):
    """Return a rank for a score out of 100."""
    if score > 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def rankComment(rank):
    """A short comment to go with each rank."""
    comments = {
        "A+": "Maths wizard! Flawless work.",
        "A": "Excellent - nearly perfect.",
        "B": "Great job, solid scores.",
        "C": "Good effort - keep practising.",
        "D": "You're getting there. Try again!",
        "F": "Tough round. The next one will be better!",
    }
    return comments[rank]


def streakMessage(streak):
    """Encouragement that grows with the number of correct answers in a row."""
    if streak >= 5:
        return f"On fire! {streak} in a row"
    if streak >= 3:
        return f"Nice streak: {streak} in a row"
    return ""


def loadHighScores(path=SCORE_FILE):
    """Return {level: best score}. Each line of the file is 'level,score'."""
    scores = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    scores[int(parts[0])] = int(parts[1])
    return scores


def saveHighScores(scores, path=SCORE_FILE):
    with open(path, "w", encoding="utf-8") as file:
        for level, score in sorted(scores.items()):
            file.write(f"{level},{score}\n")


# ---------- GUI ----------

class MathsQuiz:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg=BG)
        self.root.geometry("520x480")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Quiz.Horizontal.TProgressbar", troughcolor=CARD,
                        background=ACCENT, bordercolor=BG, lightcolor=ACCENT,
                        darkcolor=ACCENT)

        self.high_scores = loadHighScores()
        self.level = 1
        self.score = 0
        self.question_number = 0
        self.attempt = 1
        self.streak = 0
        self.best_streak = 0
        self.answer = 0
        self.time_left = TIME_LIMIT
        self.timer_id = None
        self.next_id = None
        self.displayMenu()

    # --- helpers ---

    def clearScreen(self):
        """Cancel pending timers and remove every widget."""
        for job in (self.timer_id, self.next_id):
            if job:
                self.root.after_cancel(job)
        self.timer_id = self.next_id = None
        for widget in self.root.winfo_children():
            widget.destroy()

    def makeButton(self, parent, text, command, colour=ACCENT, width=24):
        return tk.Button(parent, text=text, command=command, width=width,
                         bg=colour, fg=BG, activebackground=TEXT,
                         font=("Segoe UI", 12, "bold"), relief="flat",
                         cursor="hand2", pady=6)

    # --- screens ---

    def displayMenu(self):
        """Show the difficulty menu with each level's best score."""
        self.clearScreen()
        tk.Label(self.root, text="MATHS QUIZ", bg=BG, fg=TEXT,
                 font=("Segoe UI", 28, "bold")).pack(pady=(35, 0))
        tk.Label(self.root, text="10 questions. Two tries each. Beat the clock!",
                 bg=BG, fg=MUTED, font=("Segoe UI", 11)).pack(pady=(0, 20))
        tk.Label(self.root, text="DIFFICULTY LEVEL", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 12, "bold")).pack(pady=(0, 10))

        details = {1: "single digits", 2: "double digits", 3: "four digits"}
        colours = {1: GOOD, 2: WARN, 3: BAD}
        for level in (1, 2, 3):
            self.makeButton(self.root,
                            f"{level}. {LEVEL_NAMES[level]}  ({details[level]})",
                            lambda lvl=level: self.startQuiz(lvl),
                            colours[level], 28).pack(pady=5)
            best = self.high_scores.get(level)
            tk.Label(self.root, text=f"Best: {best}/100" if best is not None
                     else "Best: not played yet", bg=BG, fg=MUTED,
                     font=("Segoe UI", 9)).pack()

    def startQuiz(self, level):
        """Reset the round and start question 1."""
        self.level = level
        self.score = 0
        self.question_number = 0
        self.streak = 0
        self.best_streak = 0
        self.nextQuestion()

    def nextQuestion(self):
        """Create a new random problem."""
        self.question_number += 1
        self.attempt = 1
        self.num1 = randomInt(self.level)
        self.num2 = randomInt(self.level)
        self.operation = decideOperation()
        self.answer = (self.num1 + self.num2 if self.operation == '+'
                       else self.num1 - self.num2)
        self.displayProblem()

    def displayProblem(self):
        """Show the question, progress bar, timer and answer box."""
        self.clearScreen()
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=25, pady=(20, 5))
        tk.Label(top, text=f"Question {self.question_number}/{TOTAL_QUESTIONS}",
                 bg=BG, fg=MUTED, font=("Segoe UI", 11)).pack(side="left")
        tk.Label(top, text=f"Score: {self.score}", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 12, "bold")).pack(side="right")

        bar = ttk.Progressbar(self.root, style="Quiz.Horizontal.TProgressbar",
                              maximum=TOTAL_QUESTIONS, length=470)
        bar["value"] = self.question_number - 1
        bar.pack(padx=25, pady=5)

        self.streak_label = tk.Label(self.root, text=streakMessage(self.streak),
                                     bg=BG, fg=WARN, font=("Segoe UI", 11, "bold"))
        self.streak_label.pack(pady=(10, 0))

        card = tk.Frame(self.root, bg=CARD)
        card.pack(padx=25, pady=10, fill="x")
        tk.Label(card, text=f"{self.num1} {self.operation} {self.num2} =",
                 bg=CARD, fg=TEXT,
                 font=("Segoe UI", 34, "bold")).pack(pady=(20, 10))
        self.entry = tk.Entry(card, font=("Segoe UI", 22), width=8,
                              justify="center", bg=BG, fg=TEXT,
                              insertbackground=TEXT, relief="flat")
        self.entry.pack(pady=(0, 20), ipady=6)
        self.entry.focus()
        self.entry.bind("<Return>", lambda event: self.checkAnswer())

        self.timer_label = tk.Label(self.root, text="", bg=BG, fg=GOOD,
                                    font=("Segoe UI", 12, "bold"))
        self.timer_label.pack()
        self.feedback = tk.Label(self.root, text="", bg=BG, fg=BAD,
                                 font=("Segoe UI", 12, "bold"))
        self.feedback.pack(pady=4)
        self.submit_button = self.makeButton(self.root, "Submit",
                                             self.checkAnswer, width=14)
        self.submit_button.pack(pady=4)
        self.startTimer()

    # --- timer ---

    def startTimer(self):
        """(Re)start the countdown for the current attempt."""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.time_left = TIME_LIMIT
        self.tick()

    def tick(self):
        """Update the countdown once a second; time-out counts as a wrong answer."""
        colour = GOOD if self.time_left > 10 else WARN if self.time_left > 5 else BAD
        self.timer_label.config(text=f"Time left: {self.time_left}s", fg=colour)
        if self.time_left <= 0:
            self.timer_id = None
            self.handleAnswer(None)
            return
        self.time_left -= 1
        self.timer_id = self.root.after(1000, self.tick)

    # --- answering ---

    def checkAnswer(self):
        """Read the Entry box and mark the answer."""
        try:
            user_answer = int(self.entry.get())
        except ValueError:
            self.feedback.config(text="Please enter a whole number.", fg=BAD)
            return
        self.handleAnswer(user_answer)

    def handleAnswer(self, user_answer):
        """Mark an answer (None means the timer ran out)."""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        points, message = isCorrect(user_answer, self.answer, self.attempt)
        if user_answer is None:
            message = ("Time's up! One more try." if self.attempt == 1
                       else f"Time's up! The answer was {self.answer}")
        self.score += points

        if points > 0:  # correct
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
            self.finishQuestion(message, GOOD)
        elif self.attempt == 1:  # wrong, second chance
            self.streak = 0
            self.attempt = 2
            self.feedback.config(text=message, fg=WARN)
            self.entry.delete(0, tk.END)
            self.startTimer()
        else:  # wrong twice
            self.streak = 0
            self.finishQuestion(message, BAD)

    def finishQuestion(self, message, colour):
        """Show feedback, lock the input, then move on automatically."""
        self.feedback.config(text=message, fg=colour)
        self.entry.config(state="disabled")
        self.submit_button.config(state="disabled")
        self.timer_label.config(text="")
        self.next_id = self.root.after(1300, self.moveOn)

    def moveOn(self):
        self.next_id = None
        if self.question_number >= TOTAL_QUESTIONS:
            self.showResults()
        else:
            self.nextQuestion()

    # --- results ---

    def showResults(self):
        """Show score, rank, comment, high score and play-again options."""
        self.clearScreen()
        rank = displayResults(self.score)
        previous_best = self.high_scores.get(self.level)
        new_record = previous_best is None or self.score > previous_best
        if new_record:
            self.high_scores[self.level] = self.score
            saveHighScores(self.high_scores)

        tk.Label(self.root, text="QUIZ COMPLETE", bg=BG, fg=TEXT,
                 font=("Segoe UI", 24, "bold")).pack(pady=(30, 5))
        tk.Label(self.root, text=f"{self.score} / 100", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 40, "bold")).pack()
        tk.Label(self.root, text=f"Rank: {rank}", bg=BG, fg=GOOD,
                 font=("Segoe UI", 20, "bold")).pack(pady=5)
        tk.Label(self.root, text=rankComment(rank), bg=BG, fg=TEXT,
                 font=("Segoe UI", 12)).pack()
        tk.Label(self.root, text=f"Level: {LEVEL_NAMES[self.level]}   "
                                 f"Best streak: {self.best_streak}",
                 bg=BG, fg=MUTED, font=("Segoe UI", 11)).pack(pady=8)
        if new_record:
            tk.Label(self.root, text="NEW HIGH SCORE!", bg=BG, fg=WARN,
                     font=("Segoe UI", 14, "bold")).pack()
        tk.Label(self.root, text="Would you like to play again?", bg=BG,
                 fg=MUTED, font=("Segoe UI", 11)).pack(pady=(15, 8))
        self.makeButton(self.root, "Play Again", self.displayMenu,
                        GOOD, 16).pack(pady=3)
        self.makeButton(self.root, "Quit", self.root.destroy, BAD, 16).pack(pady=3)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Maths Quiz")
    MathsQuiz(root)
    root.mainloop()