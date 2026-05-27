# test_db.py

"""
This file is only for testing whether Python can connect to MySQL successfully.
"""

from db import get_conn

try:
    # Try to connect to the database
    conn = get_conn()
    
    # If connection works, print success message
    print("Database connection successful!")
    
    # Always close the connection after use
    conn.close()

except Exception as e:
    # If something goes wrong, print the error
    print("Database connection failed!")
    print("Error:", e)