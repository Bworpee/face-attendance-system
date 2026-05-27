# db.py

"""
This file is responsible for connecting Python to the MySQL database.

Whenever we want to:
- save a student
- read courses
- store attendance
- get reports

we will use this connection.
"""

import mysql.connector

# This dictionary contains your database connection settings
DB_CONFIG = {
    "host": "localhost",              # MySQL is running on your computer
    "user": "root",                   # your MySQL username (usually root)
    "password": "engineering",        # replace this with your real MySQL password
    "database": "face_attendance_db"  # the database we created in Step 4
}

def get_conn():
    """
    This function creates and returns a connection to the MySQL database.
    
    We will call this function anytime we want to interact with the database.
    """
    return mysql.connector.connect(**DB_CONFIG)