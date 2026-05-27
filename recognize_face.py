# recognize_face.py

"""
This script performs live face recognition using:
1. Webcam input
2. Haar Cascade face detection
3. LBPH trained model recognition

What it does:
- Opens the webcam
- Detects faces
- Recognizes the face using trainer/trainer.yml
- Displays the predicted label and confidence on the screen

For now:
- It only recognizes labels like 1, 2, 3
- Later, we will connect those labels to real student names in the database
"""

import os
import cv2

# Path to Haar Cascade file
CASCADE_PATH = "haarcascade_frontalface_default.xml"

# Path to trained LBPH model
MODEL_PATH = os.path.join("trainer", "trainer.yml")

# Load face detector
face_detector = cv2.CascadeClassifier(CASCADE_PATH)

# Create LBPH recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Load trained model
recognizer.read(MODEL_PATH)

# Open webcam
cap = cv2.VideoCapture(0)

# Check if webcam opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Webcam opened successfully.")
print("Press Q to quit.")

# Confidence threshold
# Lower confidence usually means better match in LBPH
threshold = 70

while True:
    # Read current frame from webcam
    ret, frame = cap.read()

    if not ret:
        continue

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5
    )

    # Loop through each detected face
    for (x, y, w, h) in faces:
        # Draw rectangle around face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Crop the face region
        face = gray[y:y + h, x:x + w]

        # Resize to same size used during training
        face = cv2.resize(face, (200, 200))

        # Predict the label and confidence
        label, confidence = recognizer.predict(face)

        # Decide if recognized or unknown
        if confidence <= threshold:
            text = f"Recognized: Label {label} | Confidence: {confidence:.2f}"
        else:
            text = f"Unknown | Confidence: {confidence:.2f}"

        # Put the result text above the face
        cv2.putText(
            frame,
            text,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    # Show webcam window
    cv2.imshow("Live Face Recognition", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF in [ord('q'), ord('Q')]:
        break

# Release webcam and close windows
cap.release()
cv2.destroyAllWindows()