# db_connection.py

import psycopg2
from sqlalchemy import create_engine
from create_database import NEW_DB_URL

# ----------------- PSYCOPG2 CONNECTION ----------------- #
def get_psycopg_connection():
    try:
        conn = psycopg2.connect(NEW_DB_URL)
        print("psycopg2 connection established.")
        return conn
    except Exception as e:
        print("Failed to connect via psycopg2:", e)
        return None

# ----------------- SQLALCHEMY ENGINE ------------------- #
def get_sqlalchemy_engine():
    try:
        engine = create_engine(NEW_DB_URL)
        print("SQLAlchemy engine created.")
        return engine
    except Exception as e:
        print("Failed to create SQLAlchemy engine:", e)
        return None
