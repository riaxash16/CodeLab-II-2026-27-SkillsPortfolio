"""Exercise 3 - Student Manager (Tkinter), including the extension options."""
# AI reference: this file was written with the understanding of this youtube video.

import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "studentMarks.txt")
MAX_TOTAL = 160 #3 coursework marks out of 20+ exam out of 100 grade letters from best to worst (the chart uses this order)
GRADES = ["A", "B", "C", "D", "F"]

#Colour palette
#Colours are kept in one place so the theme is easy to change
BG = "#161a2b"
PANEL = "#20253d"
TEXT = "#e8ebff"
MUTED = "#8f96c2"
ACCENT = "#6c8cff"
GRADE_COLOURS = {"A": "#6fe39a", "B": "#5fd4c8", "C": "#f2d46b",
                 "D": "#f5a05f", "F": "#ff6b81"}


#Data layer
class Student:
    """One student's record."""

    def __init__(self, code, name, coursework_marks, exam):
        self.code = code
        self.name = name
        self.coursework_marks = coursework_marks  # list of 3 marks out of 20
        self.exam = exam

    @property
    def coursework(self):
        return sum(self.coursework_marks)

    @property
    def total(self):
        return self.coursework + self.exam

    @property
    def percentage(self):
        return self.total / MAX_TOTAL * 100

    @property
    def grade(self):
        pct = self.percentage
        if pct >= 70:
            return "A"
        if pct >= 60:
            return "B"
        if pct >= 50:
            return "C"
        if pct >= 40:
            return "D"
        return "F"

    def toLine(self):
        """Format this record as a line for the data file."""
        marks = ",".join(str(m) for m in self.coursework_marks)
        return f"{self.code},{self.name},{marks},{self.exam}"


def loadStudents(path=DATA_FILE):
    """Read the file. First line is the student count, then one student per line."""
    students = []
    with open(path, encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]
    for line in lines[1:]:  # skip the count line
        parts = line.split(",")
        code = int(parts[0])
        name = ",".join(parts[1:-4]).strip()
        marks = [int(p) for p in parts[-4:-1]]
        exam = int(parts[-1])
        students.append(Student(code, name, marks, exam))
    return students


def saveStudents(students, path=DATA_FILE):
    """Write the records back to the file (count first, then each student)."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(f"{len(students)}\n")
        for student in students:
            file.write(student.toLine() + "\n")


def findStudents(students, query):
    """Return students whose code matches exactly, or whose name matches.
    Exact name matches win; otherwise partial matches are returned."""
    query = query.strip().lower()
    if not query:
        return []
    by_code = [s for s in students if str(s.code) == query]
    if by_code:
        return by_code
    exact = [s for s in students if s.name.lower() == query]
    if exact:
        return exact
    return [s for s in students if query in s.name.lower()]


def searchStudents(students, text):
    """Live-search filter: keep students whose name or code contains the text."""
    text = text.strip().lower()
    if not text:
        return list(students)
    return [s for s in students
            if text in s.name.lower() or text in str(s.code)]


def averagePercentage(students):
    if not students:
        return 0.0
    return sum(s.percentage for s in students) / len(students)


def passRate(students):
    """Percentage of students who scored 40% or more (grade D or better)."""
    if not students:
        return 0.0
    return sum(1 for s in students if s.percentage >= 40) / len(students) * 100


def gradeCounts(students):
    """Return {grade: number of students} for A to F."""
    counts = {grade: 0 for grade in GRADES}
    for student in students:
        counts[student.grade] += 1
    return counts


# ---------- GUI ----------

class StudentForm(tk.Toplevel):
    """Pop-up form used for adding and updating a student."""

    def __init__(self, parent, title, student=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=PANEL)
        self.result = None
        self.resizable(False, False)

        labels = ["Student code (1000-9999)", "Name", "Coursework 1 (/20)",
                  "Coursework 2 (/20)", "Coursework 3 (/20)", "Exam (/100)"]
        values = ["", "", "", "", "", ""]
        if student:
            values = [student.code, student.name, *student.coursework_marks,
                      student.exam]

        self.entries = []
        for row, (label, value) in enumerate(zip(labels, values)):
            tk.Label(self, text=label, bg=PANEL, fg=TEXT,
                     font=("Segoe UI", 10)).grid(row=row, column=0, padx=12,
                                                 pady=5, sticky="w")
            entry = tk.Entry(self, width=26, bg=BG, fg=TEXT,
                             insertbackground=TEXT, relief="flat")
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, padx=12, pady=5, ipady=3)
            self.entries.append(entry)

        tk.Button(self, text="Save", width=10, bg=ACCENT, fg=BG, relief="flat",
                  font=("Segoe UI", 10, "bold"),
                  command=self.save).grid(row=6, column=0, pady=12)
        tk.Button(self, text="Cancel", width=10, bg=MUTED, fg=BG, relief="flat",
                  font=("Segoe UI", 10, "bold"),
                  command=self.destroy).grid(row=6, column=1, pady=12)

        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def save(self):
        """Validate every field, then store a Student in self.result."""
        try:
            code = int(self.entries[0].get())
            name = self.entries[1].get().strip()
            marks = [int(self.entries[i].get()) for i in (2, 3, 4)]
            exam = int(self.entries[5].get())
        except ValueError:
            messagebox.showerror("Invalid input",
                                 "Codes and marks must be whole numbers.",
                                 parent=self)
            return
        if not 1000 <= code <= 9999:
            messagebox.showerror("Invalid input",
                                 "Student code must be 1000-9999.", parent=self)
            return
        if not name or "," in name:
            messagebox.showerror("Invalid input",
                                 "Enter a name (no commas).", parent=self)
            return
        if any(not 0 <= m <= 20 for m in marks) or not 0 <= exam <= 100:
            messagebox.showerror("Invalid input",
                                 "Coursework marks are 0-20, exam is 0-100.",
                                 parent=self)
            return
        self.result = Student(code, name, marks, exam)
        self.destroy()


class StudentManagerApp:
    COLUMNS = ("Name", "Number", "Coursework", "Exam", "Percentage", "Grade")

    def __init__(self, root):
        self.root = root
        self.root.title("Student Manager")
        self.root.geometry("1120x680")
        self.root.configure(bg=BG)
        self.students = loadStudents()
        self.shown = list(self.students)   # what the table currently displays
        self.title_text = "All student records"
        self.setupStyle()
        self.buildLayout()
        self.viewAll()

    def setupStyle(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                        foreground=TEXT, rowheight=28, borderwidth=0,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=BG, foreground=ACCENT,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#34406b")])

    def makeButton(self, parent, text, command, colour=ACCENT, width=24):
        return tk.Button(parent, text=text, command=command, width=width,
                         bg=colour, fg=BG, activebackground=TEXT,
                         font=("Segoe UI", 10, "bold"), relief="flat",
                         cursor="hand2", pady=4)

    def buildLayout(self):
        """Menu (left), search + table + stats (right)."""
        menu = tk.Frame(self.root, bg=PANEL, padx=12, pady=12)
        menu.pack(side="left", fill="y")
        tk.Label(menu, text="STUDENT MANAGER", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(0, 10))
        buttons = [
            ("1. View all records", self.viewAll, ACCENT),
            ("2. View individual record", self.viewIndividual, ACCENT),
            ("3. Highest total score", self.showHighest, GRADE_COLOURS["A"]),
            ("4. Lowest total score", self.showLowest, GRADE_COLOURS["F"]),
            ("6. Add a student", self.addStudent, GRADE_COLOURS["B"]),
            ("7. Delete a student", self.deleteStudent, GRADE_COLOURS["D"]),
            ("8. Update a student", self.updateStudent, GRADE_COLOURS["C"]),
        ]
        for text, command, colour in buttons:
            self.makeButton(menu, text, command, colour).pack(pady=3)

        # 5. Sort section
        tk.Label(menu, text="5. Sort records", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI", 10, "bold")).pack(pady=(14, 3))
        self.sort_field = ttk.Combobox(menu, state="readonly", width=22,
                                       values=["Name", "Number", "Percentage"])
        self.sort_field.current(0)
        self.sort_field.pack(pady=2)
        self.sort_order = tk.StringVar(value="asc")
        for text, value in (("Ascending", "asc"), ("Descending", "desc")):
            tk.Radiobutton(menu, text=text, variable=self.sort_order,
                           value=value, bg=PANEL, fg=TEXT, selectcolor=BG,
                           activebackground=PANEL, activeforeground=TEXT
                           ).pack(anchor="w", padx=22)
        self.makeButton(menu, "Sort", self.sortStudents, ACCENT).pack(pady=3)

        # Right side
        right = tk.Frame(self.root, bg=BG, padx=14, pady=12)
        right.pack(side="right", fill="both", expand=True)

        header = tk.Frame(right, bg=BG)
        header.pack(fill="x")
        self.title_label = tk.Label(header, text="", bg=BG, fg=TEXT,
                                    font=("Segoe UI", 15, "bold"))
        self.title_label.pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.applySearch())
        tk.Entry(header, textvariable=self.search_var, width=22, bg=PANEL,
                 fg=TEXT, insertbackground=TEXT, relief="flat",
                 font=("Segoe UI", 11)).pack(side="right", ipady=4)
        tk.Label(header, text="Search:", bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="right", padx=6)

        self.table = ttk.Treeview(right, columns=self.COLUMNS,
                                  show="headings", height=11)
        for column in self.COLUMNS:
            self.table.heading(column, text=column)
            self.table.column(column, width=180 if column == "Name" else 100,
                              anchor="w" if column == "Name" else "center")
        for grade, colour in GRADE_COLOURS.items():
            self.table.tag_configure(grade, foreground=colour)
        self.table.pack(fill="both", expand=True, pady=8)

        self.summary_label = tk.Label(right, text="", bg=BG, fg=TEXT,
                                      font=("Segoe UI", 11, "bold"))
        self.summary_label.pack(anchor="w")

        bottom = tk.Frame(right, bg=PANEL)
        bottom.pack(fill="x", pady=(8, 0))
        self.stats_label = tk.Label(bottom, text="", bg=PANEL, fg=TEXT,
                                    justify="left", font=("Segoe UI", 10),
                                    padx=14, pady=10)
        self.stats_label.pack(side="left")
        self.chart = tk.Canvas(bottom, width=380, height=130, bg=PANEL,
                               highlightthickness=0)
        self.chart.pack(side="right", padx=10, pady=5)

    # --- display ---

    def showStudents(self, students, title, summary=True):
        """Remember what is shown, then redraw the table."""
        self.shown = list(students)
        self.title_text = title
        self.search_var.set("")
        self.drawTable(self.shown, summary)

    def drawTable(self, students, summary=True):
        self.table.delete(*self.table.get_children())
        for s in students:
            self.table.insert("", "end", iid=str(s.code), tags=(s.grade,),
                              values=(s.name, s.code, f"{s.coursework}/60",
                                      f"{s.exam}/100", f"{s.percentage:.1f}%",
                                      s.grade))
        self.title_label.config(text=self.title_text)
        if summary:
            self.summary_label.config(
                text=f"Students in class: {len(students)}     "
                     f"Average percentage: {averagePercentage(students):.1f}%")
        else:
            self.summary_label.config(text="")
        self.drawStats()

    def applySearch(self):
        """Filter the table as the user types."""
        self.drawTable(searchStudents(self.shown, self.search_var.get()))

    def drawStats(self):
        """Class statistics text and the grade distribution bar chart."""
        everyone = self.students
        if everyone:
            top = max(everyone, key=lambda s: s.total)
            low = min(everyone, key=lambda s: s.total)
            self.stats_label.config(text=(
                f"CLASS STATS ({len(everyone)} students)\n"
                f"Average: {averagePercentage(everyone):.1f}%\n"
                f"Pass rate (40%+): {passRate(everyone):.0f}%\n"
                f"Top: {top.name} ({top.percentage:.0f}%)\n"
                f"Lowest: {low.name} ({low.percentage:.0f}%)"))
        else:
            self.stats_label.config(text="No students loaded.")

        self.chart.delete("all")
        counts = gradeCounts(everyone)
        biggest = max(counts.values()) or 1
        self.chart.create_text(10, 8, anchor="w", fill=MUTED,
                               text="Grade distribution",
                               font=("Segoe UI", 9, "bold"))
        for i, grade in enumerate(GRADES):
            x = 30 + i * 68
            height = counts[grade] / biggest * 70
            self.chart.create_rectangle(x, 100 - height, x + 40, 100,
                                        fill=GRADE_COLOURS[grade], width=0)
            self.chart.create_text(x + 20, 92 - height, fill=TEXT,
                                   text=str(counts[grade]),
                                   font=("Segoe UI", 9, "bold"))
            self.chart.create_text(x + 20, 115, fill=MUTED, text=grade,
                                   font=("Segoe UI", 10, "bold"))

    def saveAndRefresh(self):
        saveStudents(self.students)
        self.viewAll()

    def askForStudent(self, prompt):
        """Use the selected table row if there is one, otherwise ask for a
        name or number. Returns one matching student (or None)."""
        selected = self.table.selection()
        if selected:
            for student in self.students:
                if str(student.code) == selected[0]:
                    return student
        query = simpledialog.askstring("Find student", prompt, parent=self.root)
        if query is None:
            return None
        matches = findStudents(self.students, query)
        if not matches:
            messagebox.showinfo("Not found", "No matching student found.")
            return None
        if len(matches) > 1:
            names = ", ".join(f"{m.name} ({m.code})" for m in matches)
            messagebox.showinfo("Be more specific",
                                f"Several students match: {names}")
            return None
        return matches[0]

    # --- menu actions ---

    def viewAll(self):
        self.showStudents(self.students, "All student records")

    def viewIndividual(self):
        query = simpledialog.askstring("Find student",
                                       "Enter student name or number:",
                                       parent=self.root)
        if query is None:
            return
        matches = findStudents(self.students, query)
        if not matches:
            messagebox.showinfo("Not found", "No matching student found.")
            return
        self.showStudents(matches, "Individual record", summary=False)

    def showHighest(self):
        if self.students:
            best = max(self.students, key=lambda s: s.total)
            self.showStudents([best], "Highest total score", summary=False)

    def showLowest(self):
        if self.students:
            worst = min(self.students, key=lambda s: s.total)
            self.showStudents([worst], "Lowest total score", summary=False)

    def sortStudents(self):
        keys = {"Name": lambda s: s.name.lower(),
                "Number": lambda s: s.code,
                "Percentage": lambda s: s.percentage}
        reverse = self.sort_order.get() == "desc"
        ordered = sorted(self.students, key=keys[self.sort_field.get()],
                         reverse=reverse)
        direction = "descending" if reverse else "ascending"
        self.showStudents(ordered, f"Sorted by {self.sort_field.get()} "
                                   f"({direction})")

    def addStudent(self):
        form = StudentForm(self.root, "Add a student")
        if form.result is None:
            return
        if any(s.code == form.result.code for s in self.students):
            messagebox.showerror("Duplicate", "That student code already exists.")
            return
        self.students.append(form.result)
        self.saveAndRefresh()
        messagebox.showinfo("Added", f"{form.result.name} was added.")

    def deleteStudent(self):
        student = self.askForStudent(
            "Enter name or number of student to delete\n"
            "(or cancel and select a row first):")
        if student and messagebox.askyesno(
                "Confirm delete", f"Delete {student.name} ({student.code})?"):
            self.students.remove(student)
            self.saveAndRefresh()

    def updateStudent(self):
        student = self.askForStudent(
            "Enter name or number of student to update\n"
            "(or cancel and select a row first):")
        if not student:
            return
        form = StudentForm(self.root, "Update student", student)
        if form.result is None:
            return
        for other in self.students:
            if other is not student and other.code == form.result.code:
                messagebox.showerror("Duplicate",
                                     "That student code already exists.")
                return
        self.students[self.students.index(student)] = form.result
        self.saveAndRefresh()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        StudentManagerApp(root)
        root.mainloop()
    except FileNotFoundError:
        print(f"Could not find {DATA_FILE}. Put studentMarks.txt next to this script.")