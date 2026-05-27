# trainer.py

"""
Improved LBPH Trainer

Features:
- Better image preprocessing
- Histogram equalization
- Noise reduction
- Consistent image resizing
- Optimized LBPH parameters
- Better training stability
"""

import os
import cv2
import numpy as np

# ----------------------------------------
# Dataset and trainer paths
# ----------------------------------------
DATASET_DIR = "dataset"
TRAINER_DIR = "trainer"

MODEL_PATH = os.path.join(TRAINER_DIR, "trainer.yml")


def preprocess_image(img):
    """
    Improves image quality before training.
    """

    # Resize consistently
    img = cv2.resize(img, (200, 200))

    # Normalize lighting
    img = cv2.equalizeHist(img)

    # Reduce noise
    img = cv2.GaussianBlur(img, (3, 3), 0)

    return img


def train_model():

    images = []
    labels = []

    # Ensure dataset exists
    if not os.path.isdir(DATASET_DIR):
        raise FileNotFoundError("Dataset folder not found.")

    # Loop through student folders
    for label_name in os.listdir(DATASET_DIR):

        label_path = os.path.join(DATASET_DIR, label_name)

        if not os.path.isdir(label_path):
            continue

        # Convert folder name to integer label
        try:
            label = int(label_name)
        except ValueError:
            continue

        # Read images inside folder
        for filename in os.listdir(label_path):

            if not filename.lower().endswith(".jpg"):
                continue

            img_path = os.path.join(label_path, filename)

            # Read grayscale image
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

            # Skip unreadable images
            if img is None:
                continue

            # Skip tiny/bad images
            if img.shape[0] < 100 or img.shape[1] < 100:
                continue

            # Preprocess image
            img = preprocess_image(img)

            images.append(img)
            labels.append(label)

    # Ensure images were loaded
    if len(images) == 0:
        raise ValueError("No valid images found in dataset folder.")

    # ----------------------------------------
    # Improved LBPH recognizer settings
    # ----------------------------------------
    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=2,
        neighbors=8,
        grid_x=8,
        grid_y=8
    )

    # Train recognizer
    recognizer.train(images, np.array(labels))

    # Create trainer folder
    os.makedirs(TRAINER_DIR, exist_ok=True)

    # Save trained model
    recognizer.write(MODEL_PATH)

    return len(images), len(set(labels))


# ----------------------------------------
# Run trainer
# ----------------------------------------
if __name__ == "__main__":

    total_images, total_people = train_model()

    print("\nTraining completed successfully!")
    print(f"Total images used: {total_images}")
    print(f"Total people trained: {total_people}")
    print(f"Model saved at: {MODEL_PATH}")