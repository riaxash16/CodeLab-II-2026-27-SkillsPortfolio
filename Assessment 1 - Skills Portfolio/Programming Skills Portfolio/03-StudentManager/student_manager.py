"""Exercise 3 - Student Manager (Tkinter), including the extension options."""
# AI reference: this file was written with the understanding of this youtube video.

import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
 
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "studentMarks.txt")
MAX_TOTAL = 160  # 3 coursework marks out of 20 + exam out of 100
 
 
# ---------- Data layer (no GUI code) ----------
 
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
 
 
def averagePercentage(students):
    if not students:
        return 0.0
    return sum(s.percentage for s in students) / len(students)
 
 
# ---------- GUI ----------
 
class StudentForm(tk.Toplevel):
    """Pop-up form used for adding and updating a student."""
 
    def __init__(self, parent, title, student=None):
        super().__init__(parent)
        self.title(title)
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
            tk.Label(self, text=label).grid(row=row, column=0, padx=10,
                                            pady=4, sticky="w")
            entry = tk.Entry(self, width=25)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, padx=10, pady=4)
            self.entries.append(entry)
 
        tk.Button(self, text="Save", width=10,
                  command=self.save).grid(row=6, column=0, pady=10)
        tk.Button(self, text="Cancel", width=10,
                  command=self.destroy).grid(row=6, column=1, pady=10)
 
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
        self.root.geometry("900x480")
        self.students = loadStudents()
        self.buildLayout()
        self.viewAll()
 
    def buildLayout(self):
        """Create the menu buttons (left) and results table (right)."""
        menu = tk.Frame(self.root, padx=10, pady=10)
        menu.pack(side="left", fill="y")
 
        tk.Label(menu, text="MENU", font=("Arial", 14, "bold")).pack(pady=5)
        buttons = [
            ("1. View all records", self.viewAll),
            ("2. View individual record", self.viewIndividual),
            ("3. Highest total score", self.showHighest),
            ("4. Lowest total score", self.showLowest),
            ("6. Add a student", self.addStudent),
            ("7. Delete a student", self.deleteStudent),
            ("8. Update a student", self.updateStudent),
        ]
        for text, command in buttons:
            tk.Button(menu, text=text, width=24, command=command).pack(pady=3)
 
        # 5. Sort section
        tk.Label(menu, text="5. Sort records",
                 font=("Arial", 10, "bold")).pack(pady=(12, 2))
        self.sort_field = ttk.Combobox(menu, state="readonly", width=21,
                                       values=["Name", "Number", "Percentage"])
        self.sort_field.current(0)
        self.sort_field.pack(pady=2)
        self.sort_order = tk.StringVar(value="asc")
        tk.Radiobutton(menu, text="Ascending", variable=self.sort_order,
                       value="asc").pack(anchor="w", padx=20)
        tk.Radiobutton(menu, text="Descending", variable=self.sort_order,
                       value="desc").pack(anchor="w", padx=20)
        tk.Button(menu, text="Sort", width=24,
                  command=self.sortStudents).pack(pady=3)
 
        # Results area
        right = tk.Frame(self.root, padx=10, pady=10)
        right.pack(side="right", fill="both", expand=True)
 
        self.title_label = tk.Label(right, text="", font=("Arial", 13, "bold"))
        self.title_label.pack(anchor="w")
 
        self.table = ttk.Treeview(right, columns=self.COLUMNS,
                                  show="headings", height=15)
        for column in self.COLUMNS:
            self.table.heading(column, text=column)
            self.table.column(column, width=110 if column != "Name" else 170,
                              anchor="w" if column == "Name" else "center")
        self.table.pack(fill="both", expand=True, pady=5)
 
        self.summary_label = tk.Label(right, text="", font=("Arial", 11))
        self.summary_label.pack(anchor="w")
 
    def showStudents(self, students, title, summary=True):
        """Fill the table with the given students."""
        self.table.delete(*self.table.get_children())
        for s in students:
            self.table.insert("", "end", values=(
                s.name, s.code, f"{s.coursework}/60", f"{s.exam}/100",
                f"{s.percentage:.1f}%", s.grade))
        self.title_label.config(text=title)
        if summary:
            self.summary_label.config(
                text=f"Students in class: {len(students)}    "
                     f"Average percentage: {averagePercentage(students):.1f}%")
        else:
            self.summary_label.config(text="")
 
    def saveAndRefresh(self):
        saveStudents(self.students)
        self.viewAll()
 
    def askForStudent(self, prompt):
        """Ask for a name or code and return one matching student (or None)."""
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
 
    # --- Menu actions ---
 
    def viewAll(self):
        self.showStudents(self.students, "All student records")
 
    def viewIndividual(self):
        student = self.askForStudent("Enter student name or number:")
        if student:
            self.showStudents([student], "Individual record", summary=False)
 
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
        student = self.askForStudent("Enter name or number of student to delete:")
        if student and messagebox.askyesno(
                "Confirm delete", f"Delete {student.name} ({student.code})?"):
            self.students.remove(student)
            self.saveAndRefresh()
 
    def updateStudent(self):
        student = self.askForStudent("Enter name or number of student to update:")
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