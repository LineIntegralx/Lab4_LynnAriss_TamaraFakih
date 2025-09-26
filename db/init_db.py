#!/usr/bin/env python3
"""
:module: init_db
:synopsis: Initialize the SQLite database schema for the School Management System.

This module creates the core tables used by the School Management System and
enables SQLite foreign key constraints.

Tables Created
--------------
- **STUDENTS**: (student_id PK, name, age, email)
- **INSTRUCTORS**: (instructor_id PK, name, age, email)
- **COURSES**: (course_id PK, course_name, i_id -> INSTRUCTORS)
- **REGISTRATION**: (s_id + c_id composite PK, both FKs to STUDENTS and COURSES)

Notes
-----
- Uses `PRAGMA foreign_keys = ON;` because SQLite doesn't enforce FKs by default.
- The schema is intentionally minimal (fits the lab). No fancy indices beyond PKs.
"""

import sqlite3
from pathlib import Path

# Database file path -> db/school.db
DB_PATH = Path(__file__).resolve().parent / "school.db"


def init_db(db_path: Path = DB_PATH):
    """Initialize the SQLite database and create all tables if missing.

    Parameters
    ----------
    db_path : Path, optional
        Path to the SQLite database file (defaults to DB_PATH).

    Returns
    -------
    None
        Prints a confirmation when the database is initialized.

    Examples
    --------
    >>> from pathlib import Path
    >>> init_db(Path("school.db"))  # basic usage

    Notes
    -----
    - This function is idempotent: it uses `CREATE TABLE IF NOT EXISTS`.
    - Foreign key constraints are enabled for the connection (important!).
    """
    # make sure the parent folder exists (otherwise sqlite will fail when opening file)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # open connection + cursor (classic pattern)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # enforce FK constraints (SQLite needs this per-connection)
    cur.execute("PRAGMA foreign_keys = ON;")

    # Creating all the tables in one go; easier to read than executing many small strings
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS STUDENTS (
        student_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        email TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS INSTRUCTORS (
        instructor_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        email TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS COURSES (
        course_id TEXT PRIMARY KEY,
        course_name TEXT NOT NULL,
        i_id TEXT DEFAULT NULL,
        FOREIGN KEY (i_id) REFERENCES INSTRUCTORS(instructor_id) ON DELETE SET NULL ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS REGISTRATION (
        s_id TEXT NOT NULL,
        c_id TEXT NOT NULL,
        PRIMARY KEY (s_id, c_id),
        FOREIGN KEY (s_id) REFERENCES STUDENTS(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (c_id) REFERENCES COURSES(course_id) ON DELETE CASCADE ON UPDATE CASCADE
    );
    """)

    # commit + close like good citizens
    conn.commit()
    conn.close()

    # tiny confirmation so I know it actually ran (useful in lab runs)
    print(f"Database initialized at {db_path}")


if __name__ == "__main__":
    # running as a script goes here (kept simple)
    init_db()
