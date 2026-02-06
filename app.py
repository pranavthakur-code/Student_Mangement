from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date

app = Flask(__name__)

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("database.db")


def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        roll TEXT PRIMARY KEY,
        name TEXT,
        marks INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll TEXT,
        date TEXT,
        status TEXT
    )
    """)

    db.commit()
    db.close()


init_db()

# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect("/dashboard")
    return render_template("login.html")


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ---------- STUDENTS ----------
@app.route("/students", methods=["GET", "POST"])
def students():
    db = get_db()
    c = db.cursor()

    if request.method == "POST":
        roll = request.form["roll"]
        name = request.form["name"]
        marks = request.form["marks"]

        c.execute("""
        INSERT INTO students (roll, name, marks)
        VALUES (?, ?, ?)
        ON CONFLICT(roll) DO UPDATE SET
        name=excluded.name,
        marks=excluded.marks
        """, (roll, name, marks))

        db.commit()

    students = c.execute("SELECT * FROM students").fetchall()
    db.close()
    return render_template("students.html", students=students)


@app.route("/delete_student/<roll>")
def delete_student(roll):
    db = get_db()
    db.execute("DELETE FROM students WHERE roll=?", (roll,))
    db.commit()
    db.close()
    return redirect("/students")


@app.route("/update_student/<roll>", methods=["GET", "POST"])
def update_student(roll):
    db = get_db()
    c = db.cursor()

    if request.method == "POST":
        name = request.form["name"]
        marks = request.form["marks"]
        c.execute("UPDATE students SET name=?, marks=? WHERE roll=?",
                  (name, marks, roll))
        db.commit()
        db.close()
        return redirect("/students")

    student = c.execute("SELECT * FROM students WHERE roll=?", (roll,)).fetchone()
    db.close()
    return render_template("update_student.html", student=student)


# ---------- ATTENDANCE ----------
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    db = get_db()
    c = db.cursor()

    if request.method == "POST":
        roll = request.form["roll"]
        status = request.form["status"]
        today = str(date.today())

        c.execute("INSERT INTO attendance (roll, date, status) VALUES (?, ?, ?)",
                  (roll, today, status))
        db.commit()

    records = c.execute("""
        SELECT attendance.id, attendance.roll, students.name, attendance.date, attendance.status
        FROM attendance
        JOIN students ON attendance.roll = students.roll
        ORDER BY attendance.date DESC
    """).fetchall()

    db.close()
    return render_template("attendance.html", records=records)


@app.route("/delete_attendance/<int:id>")
def delete_attendance(id):
    db = get_db()
    db.execute("DELETE FROM attendance WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect("/attendance")


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
