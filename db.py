import os
import mysql.connector

# Railway MySQL connection settings
DB_CONFIG = {
    "host": os.getenv("MYSQLHOST"),
    "user": os.getenv("MYSQLUSER"),
    "password": os.getenv("MYSQLPASSWORD"),
    "database": os.getenv("MYSQLDATABASE"),
    "port": int(os.getenv("MYSQLPORT"))
}


def get_conn():
    """
    Creates and returns a MySQL database connection.
    """
    return mysql.connector.connect(**DB_CONFIG)