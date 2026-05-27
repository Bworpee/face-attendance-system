# capture_dataset.py

"""
Improved Face Dataset Capture System

Features:
- Captures 100 quality face images
- Better face filtering
- Histogram equalization for lighting normalization
- Prevents low-quality face captures
- Captures more diverse frames
- Improved detection accuracy
"""

import os
import sys
import cv2

# ----------------------------------------
# Haar Cascade Path
# ----------------------------------------
CASCADE_PATH = "haarcascade_frontalface_default.xml"

# Load face detector
face_detector = cv2.CascadeClassifier(CASCADE_PATH)

# ----------------------------------------
# Get student label
# ----------------------------------------
if len(sys.argv) > 1:
    label = sys.argv[1]
else:
    label = input("Enter student label: ").strip()

if not label:
    print("Label cannot be empty.")
    exit()

# ----------------------------------------
# Create dataset folder
# ----------------------------------------
dataset_path = os.path.join("dataset", label)
os.makedirs(dataset_path, exist_ok=True)

# ----------------------------------------
# Open webcam
# ----------------------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Webcam opened successfully.")
print("Move your face slowly:")
print("- Look left")
print("- Look right")
print("- Look up/down slightly")
print("- Change expressions slightly")
print("Press Q to stop early.")

# ----------------------------------------
# Capture settings
# ----------------------------------------
count = 0
frame_skip = 0
target_samples = 100

# ----------------------------------------
# Start capture loop
# ----------------------------------------
while True:
    ret, frame = cap.read()

    if not ret:
        continue

    # Mirror effect (more natural)
    frame = cv2.flip(frame, 1)

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=7,
        minSize=(100, 100)
    )

    for (x, y, w, h) in faces:

        # Ignore very small faces
        if w < 100 or h < 100:
            continue

        # Draw rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Crop face
        face = gray[y:y+h, x:x+w]

        # Resize to standard size
        face = cv2.resize(face, (200, 200))

        # Normalize lighting
        face = cv2.equalizeHist(face)

        # Skip some frames for more diversity
        frame_skip += 1

        if frame_skip % 3 != 0:
            continue

        # Save image
        count += 1

        image_path = os.path.join(
            dataset_path,
            f"img_{count:03d}.jpg"
        )

        cv2.imwrite(image_path, face)

        # Display progress
        cv2.putText(
            frame,
            f"Captured: {count}/{target_samples}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # Save only one face per frame
        break

    # Show camera
    cv2.imshow("Face Dataset Capture", frame)

    # Stop after enough samples
    if count >= target_samples:
        print(f"Done! Captured {count} images.")
        break

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF in [ord('q'), ord('Q')]:
        print("Capture stopped by user.")
        break

# ----------------------------------------
# Cleanup
# ----------------------------------------
cap.release()
cv2.destroyAllWindows()

print(f"Images saved in: {dataset_path}")