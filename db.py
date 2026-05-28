import os
import mysql.connector

# Railway automatically provides these environment variables
DB_CONFIG = {
    "host": os.getenv("mysql.railway.internal"),
    "user": os.getenv("root"),
    "password": os.getenv("MYSQLPASSWORD"),
    "database": os.getenv("MYSQLDkbyVstDBUxLWQhitTfFcBKkfizmfgnARATABASE"),
    "port": int(os.getenv("3306"))
}


def get_conn():
    """
    Creates and returns a MySQL database connection.
    """
    return mysql.connector.connect(**DB_CONFIG)