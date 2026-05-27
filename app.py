# app.py

"""
This is the main Flask web application for the
Face Recognition Attendance Management System.

What this app does:
1. Shows a home page
2. Allows adding students into the database
3. Allows training the face recognition model
4. Allows starting attendance
5. Allows viewing attendance records
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_conn
from trainer import train_model
import subprocess

# Create the Flask app
app = Flask(__name__)
import os

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "temporary_dev_key"
)


@app.route("/")
def home():
    """
    Home page route.
    This shows the main dashboard.
    """
    return render_template("index.html")


@app.route("/add-student", methods=["GET", "POST"])
def add_student():
    """
    This route allows the admin to add a student into the database.

    Improvements:
    - checks if matric number already exists
    - checks if face label already exists
    - shows friendly messages instead of crashing
    """
    if request.method == "POST":
        matric_no = request.form["matric_no"].strip()
        first_name = request.form["first_name"].strip()
        last_name = request.form["last_name"].strip()
        department = request.form["department"].strip()
        level = request.form["level"].strip()
        model_label = int(request.form["model_label"])

        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        # -----------------------------------------
        # Check if matric number already exists
        # -----------------------------------------
        check_matric_query = "SELECT * FROM students WHERE matric_no = %s"
        cursor.execute(check_matric_query, (matric_no,))
        existing_matric = cursor.fetchone()

        if existing_matric:
            cursor.close()
            conn.close()
            flash(f"Matric number '{matric_no}' already exists. Please use another one.", "error")
            return redirect(url_for("add_student"))

        # -----------------------------------------
        # Check if face label already exists
        # -----------------------------------------
        check_label_query = "SELECT * FROM facedata WHERE model_label = %s"
        cursor.execute(check_label_query, (model_label,))
        existing_label = cursor.fetchone()

        if existing_label:
            cursor.close()
            conn.close()
            flash(f"Face label '{model_label}' is already in use. Please choose another label.", "error")
            return redirect(url_for("add_student"))

        # -----------------------------------------
        # Insert student into students table
        # -----------------------------------------
        student_query = """
            INSERT INTO students (matric_no, first_name, last_name, department, level)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(student_query, (matric_no, first_name, last_name, department, level))
        conn.commit()

        # Get newly inserted student_id
        student_id = cursor.lastrowid

        # -----------------------------------------
        # Insert face label mapping into facedata table
        # -----------------------------------------
        facedata_query = """
            INSERT INTO facedata (student_id, model_label, dataset_path)
            VALUES (%s, %s, %s)
        """
        dataset_path = f"dataset/{model_label}"
        cursor.execute(facedata_query, (student_id, model_label, dataset_path))
        conn.commit()

        cursor.close()
        conn.close()

        flash("Student added successfully!", "success")
        return redirect(url_for("home"))

    return render_template("add_student.html")


@app.route("/capture-dataset", methods=["GET", "POST"])
def capture_dataset_page():
    """
    This route starts the webcam face capture script
    for a given student label.

    GET:
        Shows a form where user enters the face label

    POST:
        Runs capture_dataset.py with that label
    """
    if request.method == "POST":
        model_label = request.form["model_label"]

        # Run the dataset capture script and pass the label
        subprocess.run(["python", "capture_dataset.py", model_label])

        return redirect(url_for("train_model_page"))

    return render_template("capture_dataset.html")


@app.route("/train-model", methods=["GET", "POST"])
def train_model_page():
    """
    This route allows the admin to train the LBPH model.

    GET:
        Shows the train model page.

    POST:
        Runs the train_model() function from trainer.py
    """
    if request.method == "POST":
        train_model()
        return redirect(url_for("home"))

    return render_template("train_model.html")


@app.route("/start-attendance", methods=["GET", "POST"])
def start_attendance():
    """
    This route starts the attendance recognition script.

    GET:
        Shows the form to enter course ID.

    POST:
        Runs the attendance recognition script.
    """
    if request.method == "POST":
        course_id = request.form["course_id"]

        # Run the attendance marking script from terminal
        # We pass the course_id to it
        subprocess.run(["python", "recognize_and_mark_attendance.py"], input=f"{course_id}\n", text=True)

        return redirect(url_for("home"))

    return render_template("start_attendance.html")


@app.route("/attendance-report")
def attendance_report():
    """
    This route fetches attendance records together with
    student details and course details.

    Instead of showing only student_id and course_id,
    it shows real names, matric numbers, and course codes.
    """
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            a.attendance_id,
            s.matric_no,
            s.first_name,
            s.last_name,
            c.course_code,
            c.course_title,
            a.attendance_date,
            a.attendance_time,
            a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        JOIN courses c ON a.course_id = c.course_id
        ORDER BY a.attendance_id DESC
    """

    cursor.execute(query)
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("attendance_report.html", records=records)


# Run the Flask app
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )