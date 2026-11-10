
import os
import sqlite3
from pathlib import Path
import streamlit as st

# SQLite database file
DB_PATH = Path(
    os.environ.get(
        "SQLITE_DB_PATH",
        str(Path(__file__).resolve().parent / "organ_donation.db")
    )
)


def initialize_database():
    """Create project tables, view, trigger, and demo records."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    connection.executescript("""
        CREATE TABLE IF NOT EXISTS donor (
            Donor_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Age INTEGER,
            Gender TEXT,
            Blood_Group TEXT,
            Phone TEXT,
            Address TEXT,
            Registration_Date DATE
        );

        CREATE TABLE IF NOT EXISTS recipient (
            Recipient_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Age INTEGER,
            Gender TEXT,
            Blood_Group TEXT,
            Organ_Required TEXT,
            Priority TEXT,
            Registration_Date DATE
        );

        CREATE TABLE IF NOT EXISTS organ (
            Organ_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Donor_ID INTEGER,
            Organ_Type TEXT,
            Availability_Status TEXT DEFAULT 'Available',
            FOREIGN KEY (Donor_ID) REFERENCES donor(Donor_ID)
        );

        CREATE TABLE IF NOT EXISTS hospital (
            Hospital_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Hospital_Name TEXT,
            Location TEXT,
            Contact_Number TEXT
        );

        CREATE TABLE IF NOT EXISTS coordinator (
            Coordinator_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Phone TEXT,
            Hospital_ID INTEGER,
            FOREIGN KEY (Hospital_ID) REFERENCES hospital(Hospital_ID)
        );

        CREATE TABLE IF NOT EXISTS medical_compatibility (
            Compatibility_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Donor_ID INTEGER,
            Recipient_ID INTEGER,
            Compatibility_Status TEXT,
            Remarks TEXT,
            FOREIGN KEY (Donor_ID) REFERENCES donor(Donor_ID),
            FOREIGN KEY (Recipient_ID) REFERENCES recipient(Recipient_ID)
        );

        CREATE TABLE IF NOT EXISTS transplant (
            Transplant_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Donor_ID INTEGER,
            Recipient_ID INTEGER,
            Organ_ID INTEGER,
            Hospital_ID INTEGER,
            Transplant_Date DATE,
            Status TEXT,
            FOREIGN KEY (Donor_ID) REFERENCES donor(Donor_ID),
            FOREIGN KEY (Recipient_ID) REFERENCES recipient(Recipient_ID),
            FOREIGN KEY (Organ_ID) REFERENCES organ(Organ_ID),
            FOREIGN KEY (Hospital_ID) REFERENCES hospital(Hospital_ID)
        );

        CREATE VIEW IF NOT EXISTS available_organ_view AS
        SELECT Organ_ID, Donor_ID, Organ_Type, Availability_Status
        FROM organ
        WHERE Availability_Status = 'Available';

        CREATE TRIGGER IF NOT EXISTS trg_update_organ_status
        AFTER INSERT ON transplant
        BEGIN
            UPDATE organ
            SET Availability_Status = 'Unavailable'
            WHERE Organ_ID = NEW.Organ_ID;
        END;
    """)

    # Add fictional demonstration records only to empty tables.
    if connection.execute("SELECT COUNT(*) FROM donor").fetchone()[0] == 0:
        connection.executemany("""
            INSERT INTO donor
            (Donor_ID, Name, Age, Gender, Blood_Group,
             Phone, Address, Registration_Date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (1, "Rahul", 25, "Male", "O+", "9876543210",
             "Hyderabad", "2026-10-01"),
            (2, "Priya", 30, "Female", "A+", "9876543211",
             "Warangal", "2026-10-02")
        ])

    if connection.execute("SELECT COUNT(*) FROM recipient").fetchone()[0] == 0:
        connection.executemany("""
            INSERT INTO recipient
            (Recipient_ID, Name, Age, Gender, Blood_Group,
             Organ_Required, Priority, Registration_Date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (1, "Arjun", 40, "Male", "O+", "Kidney",
             "High", "2026-10-03"),
            (2, "Sneha", 35, "Female", "A+", "Liver",
             "Medium", "2026-10-04")
        ])

    if connection.execute("SELECT COUNT(*) FROM organ").fetchone()[0] == 0:
        connection.executemany("""
            INSERT INTO organ
            (Organ_ID, Donor_ID, Organ_Type, Availability_Status)
            VALUES (?, ?, ?, ?)
        """, [
            (1, 1, "Kidney", "Available"),
            (2, 2, "Liver", "Available")
        ])

    if connection.execute("SELECT COUNT(*) FROM hospital").fetchone()[0] == 0:
        connection.execute("""
            INSERT INTO hospital
            VALUES (1, 'City Hospital', 'Hyderabad', '9876500000')
        """)

    if connection.execute("SELECT COUNT(*) FROM coordinator").fetchone()[0] == 0:
        connection.execute("""
            INSERT INTO coordinator
            VALUES (1, 'Anil', '9876500001', 1)
        """)

    if connection.execute(
        "SELECT COUNT(*) FROM medical_compatibility"
    ).fetchone()[0] == 0:
        connection.executemany("""
            INSERT INTO medical_compatibility
            VALUES (?, ?, ?, ?, ?)
        """, [
            (1, 1, 1, "Compatible", "Sample compatibility record"),
            (2, 2, 2, "Compatible", "Sample compatibility record")
        ])

    connection.commit()
    connection.close()


class SQLiteCursor:
    """Small compatibility layer for the existing app.py queries."""

    def __init__(self, cursor):
        self.cursor_obj = cursor

    def execute(self, query, values=None):
        # Convert MySQL-style placeholders to SQLite placeholders.
        query = query.replace("%s", "?")

        if values is None:
            self.cursor_obj.execute(query)
        else:
            self.cursor_obj.execute(query, values)

        return self

    def fetchone(self):
        row = self.cursor_obj.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        return [dict(row) for row in self.cursor_obj.fetchall()]

    def close(self):
        self.cursor_obj.close()


class SQLiteConnection:
    """Preserves the cursor interface used by the original app.py."""

    def __init__(self, connection):
        self.connection = connection

    def cursor(self, dictionary=False):
        # SQLite rows are converted to dictionaries by SQLiteCursor.
        return SQLiteCursor(self.connection.cursor())

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


def get_connection():
    try:
        initialize_database()

        connection = sqlite3.connect(
            DB_PATH,
            timeout=30
        )

        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")

        return SQLiteConnection(connection)

    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None
