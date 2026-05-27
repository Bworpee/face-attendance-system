# reset_system.py

"""
This script resets the Face Recognition Attendance System.

It will:
1. Clear database records from:
   - attendance
   - facedata
   - students
   - courses

2. Reset AUTO_INCREMENT counters

3. Delete all face image folders inside dataset/

4. Delete the trained model file:
   trainer/trainer.yml

IMPORTANT:
- It does NOT delete your source code files
- It does NOT delete your templates or static files
- It is meant for starting the system fresh
"""

import os
import shutil
from db import get_conn


def clear_database():
    """
    Deletes all records from the database tables
    and resets their AUTO_INCREMENT counters.
    """
    conn = get_conn()
    cursor = conn.cursor()

    print("Clearing database tables...")

    # Use the correct order because of foreign key relationships
    cursor.execute("DELETE FROM attendance")
    cursor.execute("DELETE FROM facedata")
    cursor.execute("DELETE FROM students")
    cursor.execute("DELETE FROM courses")

    # Reset auto increment values
    cursor.execute("ALTER TABLE attendance AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE facedata AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE students AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE courses AUTO_INCREMENT = 1")

    conn.commit()
    cursor.close()
    conn.close()

    print("Database cleared successfully.")


def clear_dataset_folder():
    """
    Deletes all subfolders inside the dataset folder.
    Example:
    dataset/1
    dataset/2
    dataset/3
    """
    dataset_dir = "dataset"

    if not os.path.exists(dataset_dir):
        print("Dataset folder does not exist. Skipping dataset cleanup.")
        return

    print("Clearing dataset folder...")

    for item in os.listdir(dataset_dir):
        item_path = os.path.join(dataset_dir, item)

        # Delete folders recursively
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
            print(f"Deleted folder: {item_path}")

        # Delete files if any exist directly inside dataset/
        elif os.path.isfile(item_path):
            os.remove(item_path)
            print(f"Deleted file: {item_path}")

    print("Dataset folder cleared successfully.")


def clear_trained_model():
    """
    Deletes the trained model file if it exists.
    """
    model_path = os.path.join("trainer", "trainer.yml")

    if os.path.exists(model_path):
        os.remove(model_path)
        print(f"Deleted trained model: {model_path}")
    else:
        print("No trained model found. Skipping model cleanup.")


def main():
    """
    Main reset function.
    """
    print("=" * 50)
    print("FACE ATTENDANCE SYSTEM RESET")
    print("=" * 50)

    confirm = input(
        "This will delete all students, attendance, courses, datasets, and trained model.\n"
        "Type 'YES' to continue: "
    ).strip()

    if confirm != "YES":
        print("Reset cancelled.")
        return

    try:
        clear_database()
        clear_dataset_folder()
        clear_trained_model()

        print("\nSystem reset completed successfully.")
        print("You can now start fresh.")

    except Exception as e:
        print("\nAn error occurred during reset:")
        print(e)


if __name__ == "__main__":
    main()