"""Exercise 1 - Maths Quiz (Tkinter)."""
# AI reference: this file was written with the help of Claude (Anthropic).
# (10 questions, 3 difficulty levels, 2 attempts per question, ranked results).

import random
import tkinter as tk
from tkinter import messagebox

TOTAL_QUESTIONS = 10


# ---------- Logic functions (no GUI code in these) ----------

def randomInt(level):
    """Return a random number with the right number of digits for the level.
    level 1 = single digit, 2 = double digit, 3 = four digit."""
    ranges = {1: (0, 9), 2: (10, 99), 3: (1000, 9999)}
    low, high = ranges[level]
    return random.randint(low, high)


def decideOperation():
    """Randomly return '+' or '-'."""
    return random.choice(['+', '-'])


def isCorrect(user_answer, correct_answer, attempt):
    """Check the answer. Return (points earned, message to show)."""
    if user_answer == correct_answer:
        points = 10 if attempt == 1 else 5
        return points, f"Correct! You earned {points} points."
    if attempt == 1:
        return 0, "Wrong answer. Try once more!"
    return 0, f"Wrong again. The correct answer was {correct_answer}."


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


# ---------- GUI ----------

class MathsQuiz:
    def __init__(self, root):
        self.root = root
        self.root.geometry("420x320")
        self.level = 1
        self.score = 0
        self.question_number = 0
        self.attempt = 1
        self.answer = 0
        self.displayMenu()

    def clearScreen(self):
        """Remove every widget so the next screen starts clean."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def displayMenu(self):
        """Show the difficulty level buttons."""
        self.clearScreen()
        tk.Label(self.root, text="DIFFICULTY LEVEL",
                 font=("Arial", 18, "bold")).pack(pady=20)
        for level, name in ((1, "Easy"), (2, "Moderate"), (3, "Advanced")):
            tk.Button(self.root, text=f"{level}. {name}", width=20,
                      command=lambda lvl=level: self.startQuiz(lvl)).pack(pady=6)

    def startQuiz(self, level):
        """Reset the score and begin question 1 at the chosen level."""
        self.level = level
        self.score = 0
        self.question_number = 0
        self.nextQuestion()

    def nextQuestion(self):
        """Create a new random problem and show it."""
        self.question_number += 1
        self.attempt = 1
        self.num1 = randomInt(self.level)
        self.num2 = randomInt(self.level)
        self.operation = decideOperation()
        if self.operation == '+':
            self.answer = self.num1 + self.num2
        else:
            self.answer = self.num1 - self.num2
        self.displayProblem()

    def displayProblem(self):
        """Show the question and an Entry box for the answer."""
        self.clearScreen()
        tk.Label(self.root,
                 text=f"Question {self.question_number} of {TOTAL_QUESTIONS}"
                      f"     Score: {self.score}",
                 font=("Arial", 11)).pack(pady=10)
        tk.Label(self.root,
                 text=f"{self.num1} {self.operation} {self.num2} =",
                 font=("Arial", 24, "bold")).pack(pady=10)

        self.entry = tk.Entry(self.root, font=("Arial", 16), width=10,
                              justify="center")
        self.entry.pack(pady=5)
        self.entry.focus()
        self.entry.bind("<Return>", lambda event: self.checkAnswer())

        self.feedback = tk.Label(self.root, text="", fg="red",
                                 font=("Arial", 11))
        self.feedback.pack(pady=5)

        tk.Button(self.root, text="Submit", width=12,
                  command=self.checkAnswer).pack(pady=5)

    def checkAnswer(self):
        """Read the Entry, use isCorrect(), then retry or move on."""
        try:
            user_answer = int(self.entry.get())
        except ValueError:
            self.feedback.config(text="Please enter a whole number.")
            return

        points, message = isCorrect(user_answer, self.answer, self.attempt)
        self.score += points

        if points > 0 or self.attempt == 2:
            messagebox.showinfo("Result", message)
            self.moveOn()
        else:
            # First attempt wrong: give one more chance
            self.attempt = 2
            self.feedback.config(text=message)
            self.entry.delete(0, tk.END)

    def moveOn(self):
        """Go to the next question, or show results after the last one."""
        if self.question_number >= TOTAL_QUESTIONS:
            self.showResults()
        else:
            self.nextQuestion()

    def showResults(self):
        """Show the final score, rank, and play again / quit buttons."""
        self.clearScreen()
        rank = displayResults(self.score)
        tk.Label(self.root, text="QUIZ COMPLETE",
                 font=("Arial", 18, "bold")).pack(pady=15)
        tk.Label(self.root, text=f"Your score: {self.score} / 100",
                 font=("Arial", 14)).pack(pady=5)
        tk.Label(self.root, text=f"Your rank: {rank}",
                 font=("Arial", 14)).pack(pady=5)
        tk.Label(self.root, text="Would you like to play again?",
                 font=("Arial", 11)).pack(pady=15)
        tk.Button(self.root, text="Play Again", width=14,
                  command=self.displayMenu).pack(pady=3)
        tk.Button(self.root, text="Quit", width=14,
                  command=self.root.destroy).pack(pady=3)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Maths Quiz")
    MathsQuiz(root)
    root.mainloop()