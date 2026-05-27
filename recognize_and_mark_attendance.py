# recognize_and_mark_attendance.py

"""
This script:
1. Opens the webcam
2. Detects and recognizes a face using the trained LBPH model
3. Looks up the recognized label in the MySQL database
4. Marks attendance automatically for a selected course

Improved version:
- Shows student name clearly
- Shows matric number clearly
- Shows attendance status in a separate line
- Uses different colors for recognized and unknown faces
"""

import os
import cv2
from datetime import datetime, date
from db import get_conn

# -----------------------------------------
# File paths
# -----------------------------------------
CASCADE_PATH = "haarcascade_frontalface_default.xml"
MODEL_PATH = os.path.join("trainer", "trainer.yml")

# -----------------------------------------
# Load face detector
# -----------------------------------------
face_detector = cv2.CascadeClassifier(CASCADE_PATH)

# -----------------------------------------
# Load trained LBPH model
# -----------------------------------------
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(MODEL_PATH)

# -----------------------------------------
# Recognition threshold
# Lower confidence means better match in LBPH
# -----------------------------------------
threshold = 70


def get_student_by_label(label):
    """
    Gets student details from the database using the face label.
    Returns:
        student record if found
        None if not found
    """
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT s.student_id, s.matric_no, s.first_name, s.last_name, f.model_label
        FROM students s
        JOIN facedata f ON s.student_id = f.student_id
        WHERE f.model_label = %s
    """
    cursor.execute(query, (label,))
    student = cursor.fetchone()

    cursor.close()
    conn.close()

    return student


def mark_attendance(student_id, course_id):
    """
    Marks attendance in the database.

    Returns:
        'marked' if attendance is newly inserted
        'already_marked' if attendance already exists for today
    """
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    today = date.today()
    now = datetime.now().time().replace(microsecond=0)

    # Check if attendance already exists
    check_query = """
        SELECT * FROM attendance
        WHERE student_id = %s AND course_id = %s AND attendance_date = %s
    """
    cursor.execute(check_query, (student_id, course_id, today))
    existing = cursor.fetchone()

    if existing:
        cursor.close()
        conn.close()
        return "already_marked"

    # Insert new attendance row
    insert_query = """
        INSERT INTO attendance (student_id, course_id, attendance_date, attendance_time, status)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (student_id, course_id, today, now, "Present"))
    conn.commit()

    cursor.close()
    conn.close()

    return "marked"


# -----------------------------------------
# Ask for course ID
# -----------------------------------------
print("Enter the course_id to mark attendance for.")
course_id = input("Course ID: ").strip()

if not course_id.isdigit():
    print("Invalid course_id. Please enter a number.")
    exit()

course_id = int(course_id)

# -----------------------------------------
# Open webcam
# -----------------------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Webcam opened successfully.")
print("Press Q to quit.")

# -----------------------------------------
# Start recognition loop
# -----------------------------------------
marked_students = set()

while True:
    ret, frame = cap.read()

    if not ret:
        continue

    # Convert frame to grayscale for detection/recognition
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=7,
        minSize=(100,100)
    )

    # Process each detected face
    for (x, y, w, h) in faces:
        if w < 100 or h < 100:
            continue
        # Default display values
        box_color = (0, 0, 255)   # red for unknown
        line1 = "Unknown Face"
        line2 = ""
        line3 = ""

        # Draw rectangle first
        cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)

        # Crop and resize face region
        face = gray[y:y + h, x:x + w]
        face = cv2.resize(face, (200, 200))

        # Predict face label and confidence
        label, confidence = recognizer.predict(face)

        # Predict face label and confidence
        label, confidence = recognizer.predict(face)

        # Default values
        student = None

        # 🔥 SINGLE confidence check (ONLY ONE)
        if confidence < threshold:
            student = get_student_by_label(label)

        # If not recognized, display unknown
        if student is None:
            line1 = "Unknown Face"
            line2 = f"Confidence: {confidence:.2f}"
            line3 = ""
        else:
            full_name = f"{student['first_name']} {student['last_name']}"
            matric_no = student["matric_no"]
            student_id = student["student_id"]

            # Prevent duplicate attendance
            if student_id not in marked_students:
                result = mark_attendance(student_id, course_id)
                marked_students.add(student_id)
            else:
                result = "already_marked"

            # Set display
            box_color = (0, 255, 0)
            line1 = full_name
            line2 = f"Matric No: {matric_no}"

            if result == "marked":
                line3 = "Attendance Marked"
            else:
                line3 = "Already Marked"     







        # Draw rectangle again using final chosen color
        cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)

        # Draw text lines above the face
        cv2.putText(
            frame,
            line1,
            (x, y - 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            box_color,
            2
        )

        cv2.putText(
            frame,
            line2,
            (x, y - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            box_color,
            2
        )

        cv2.putText(
            frame,
            line3,
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            box_color,
            2
        )

    # Show webcam feed
    cv2.imshow("Face Recognition Attendance", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF in [ord("q"), ord("Q")]:
        break

# -----------------------------------------
# Clean up resources
# -----------------------------------------
cap.release()
cv2.destroyAllWindows()