#!/usr/bin/env python3
"""
:module: sqlite_repo
:synopsis: SQLite Repository for School Management System

This module provides CRUD operations for Students, Instructors, Courses,
and Registration using a simple SQLite backend. It also exposes a small
search helper and a backup utility.

Notes
-----
- Designed to be small and straightforward for the lab. Not production-optimized.
- Foreign keys are enabled via PRAGMA to keep relational integrity (basic).
"""

import sqlite3
from pathlib import Path
from typing import Any, List, Dict, Optional, Tuple
import os


DB_PATH = Path(__file__).resolve().parent / "school.db"


class SQLiteRepository:
    """
    Repository class for handling School Management database operations.

    Parameters
    ----------
    db_path : Path, optional
        Path to the SQLite database file (defaults to 'school.db').

    Attributes
    ----------
    conn : sqlite3.Connection
        Active SQLite database connection. Exposed here for simplicity (lab style).
    """

    def __init__(self, db_path: Path = DB_PATH):
        """Constructor method

        Parameters
        ----------
        db_path : Path, optional
            Path to the SQLite database file (defaults to DB_PATH).
        """
        # connect to db and enforce foreign key constraints (otherwise cascades won't work)
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")  # yeah this is important for FK checks

    # ---------- STUDENTS ----------
    def add_student(self, student_id: str, name: str, age: int, email: str) -> None:
        """Insert a new student record.

        Parameters
        ----------
        student_id : str
            Unique student identifier.
        name : str
            Name of the student.
        age : int
            Age of the student.
        email : str
            Email address of the student.

        Returns
        -------
        None
            Nothing (side-effect: inserts row).
        """
        # just adding a student to the table (basic insert)
        self.conn.execute(
            "INSERT INTO STUDENTS (student_id, name, age, email) VALUES (?, ?, ?, ?)",
            (student_id, name, age, email),
        )
        self.conn.commit()

    def get_all_students(self) -> List[Dict[str, Any]]:
        """Return all students as a list of dictionaries sorted by name."""
        cur = self.conn.execute("SELECT * FROM STUDENTS ORDER BY name ASC")
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def update_student(self, student_id: str, name: Optional[str] = None,
                       age: Optional[int] = None, email: Optional[str] = None) -> None:
        """Update existing student details.

        Parameters
        ----------
        student_id : str
            Student identifier.
        name : str, optional
            Updated name (optional).
        age : int, optional
            Updated age (optional).
        email : str, optional
            Updated email (optional).

        Returns
        -------
        None
            Nothing (updates if fields provided).
        """
        # collect only the fields that are passed (otherwise no-op)
        fields, values = [], []
        if name: fields.append("name=?"); values.append(name)  # quick and simple
        if age is not None: fields.append("age=?"); values.append(age)
        if email: fields.append("email=?"); values.append(email)
        if not fields: return  # nothing to update -> silently return (simple pattern)
        values.append(student_id)
        self.conn.execute(f"UPDATE STUDENTS SET {', '.join(fields)} WHERE student_id=?", values)
        self.conn.commit()

    def get_all_instructors(self) -> List[Dict[str, Any]]:
        """Return all instructors as a list of dictionaries sorted by name."""
        cur = self.conn.execute("SELECT * FROM INSTRUCTORS ORDER BY name ASC")
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def delete_student(self, student_id: str) -> None:
        """Delete a student record.

        Parameters
        ----------
        student_id : str
            Student identifier.

        Returns
        -------
        None
        """
        # straight delete by id (no soft-delete here)
        self.conn.execute("DELETE FROM STUDENTS WHERE student_id=?", (student_id,))
        self.conn.commit()

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Fetch student record by ID.

        Parameters
        ----------
        student_id : str
            Student identifier.

        Returns
        -------
        dict or None
            Dictionary with student info or None if not found.
        """
        cur = self.conn.execute("SELECT * FROM STUDENTS WHERE student_id=?", (student_id,))
        row = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], row)) if row else None  # dictify because nicer

    # ---------- INSTRUCTORS ----------
    def add_instructor(self, instructor_id: str, name: str, age: int, email: str) -> None:
        """Insert a new instructor record.

        Parameters
        ----------
        instructor_id : str
            Unique instructor identifier.
        name : str
            Instructor name.
        age : int
            Instructor age.
        email : str
            Instructor email.

        Returns
        -------
        None
        """
        self.conn.execute(
            "INSERT INTO INSTRUCTORS (instructor_id, name, age, email) VALUES (?, ?, ?, ?)",
            (instructor_id, name, age, email),
        )
        self.conn.commit()

    def update_instructor(self, instructor_id: str, name: Optional[str] = None,
                          age: Optional[int] = None, email: Optional[str] = None) -> None:
        """Update existing instructor record.

        Parameters
        ----------
        instructor_id : str
            Instructor identifier.
        name : str, optional
            Updated name (optional).
        age : int, optional
            Updated age (optional).
        email : str, optional
            Updated email (optional).

        Returns
        -------
        None
        """
        # same update pattern as students (keep it consistent)
        fields, values = [], []
        if name: fields.append("name=?"); values.append(name)
        if age is not None: fields.append("age=?"); values.append(age)
        if email: fields.append("email=?"); values.append(email)
        if not fields: return
        values.append(instructor_id)
        self.conn.execute(f"UPDATE INSTRUCTORS SET {', '.join(fields)} WHERE instructor_id=?", values)
        self.conn.commit()

    def delete_instructor(self, instructor_id: str) -> None:
        """Delete an instructor by ID.

        Parameters
        ----------
        instructor_id : str
            Instructor identifier.

        Returns
        -------
        None
        """
        self.conn.execute("DELETE FROM INSTRUCTORS WHERE instructor_id=?", (instructor_id,))
        self.conn.commit()

    def get_instructor(self, instructor_id: str) -> Optional[Dict[str, Any]]:
        """Fetch instructor record.

        Parameters
        ----------
        instructor_id : str
            Instructor identifier.

        Returns
        -------
        dict or None
            Dictionary with instructor details or None.
        """
        cur = self.conn.execute("SELECT * FROM INSTRUCTORS WHERE instructor_id=?", (instructor_id,))
        row = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], row)) if row else None  # same dictify trick

    # ---------- COURSES ----------
    def add_course(self, course_id: str, course_name: str, i_id: Optional[str] = None) -> None:
        """Insert a new course.

        Parameters
        ----------
        course_id : str
            Course identifier.
        course_name : str
            Name of the course.
        i_id : str, optional
            Assigned instructor ID (optional).

        Returns
        -------
        None
        """
        self.conn.execute(
            "INSERT INTO COURSES (course_id, course_name, i_id) VALUES (?, ?, ?)",
            (course_id, course_name, i_id),
        )
        self.conn.commit()

    def update_course(self, course_id: str, course_name: Optional[str] = None,
                      i_id: Optional[str] = None) -> None:
        """Update existing course record.

        Parameters
        ----------
        course_id : str
            Course identifier.
        course_name : str, optional
            New course name (optional).
        i_id : str, optional
            New instructor ID (optional).

        Returns
        -------
        None
        """
        # update only provided fields (same pattern again)
        fields, values = [], []
        if course_name: fields.append("course_name=?"); values.append(course_name)
        if i_id is not None: fields.append("i_id=?"); values.append(i_id)
        if not fields: return
        values.append(course_id)
        self.conn.execute(f"UPDATE COURSES SET {', '.join(fields)} WHERE course_id=?", values)
        self.conn.commit()

    def delete_course(self, course_id: str) -> None:
        """Delete a course.

        Parameters
        ----------
        course_id : str
            Course identifier.

        Returns
        -------
        None
        """
        self.conn.execute("DELETE FROM COURSES WHERE course_id=?", (course_id,))
        self.conn.commit()

    def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a course record.

        Parameters
        ----------
        course_id : str
            Course identifier.

        Returns
        -------
        dict or None
            Dictionary with course data or None.
        """
        cur = self.conn.execute("SELECT * FROM COURSES WHERE course_id=?", (course_id,))
        row = cur.fetchone()
        return dict(zip([c[0] for c in cur.description], row)) if row else None  # keep consistent

    def get_all_courses(self) -> List[Dict[str, Any]]:
        """Return all courses as a list of dictionaries sorted by course_id."""
        cur = self.conn.execute("SELECT * FROM COURSES ORDER BY course_id ASC")
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    # ---------- REGISTRATION ----------
    def register_student(self, s_id: str, c_id: str) -> None:
        """Register a student in a course.

        Parameters
        ----------
        s_id : str
            Student ID.
        c_id : str
            Course ID.

        Raises
        ------
        ValueError
            If student or course does not exist.

        Returns
        -------
        None
        """
        # Ensure both exist first (otherwise FK error or logical error)
        if not self.get_student(s_id): raise ValueError("Student does not exist")
        if not self.get_course(c_id): raise ValueError("Course does not exist")
        self.conn.execute(
            "INSERT OR IGNORE INTO REGISTRATION (s_id, c_id) VALUES (?, ?)", (s_id, c_id)
        )
        self.conn.commit()

    def unregister_student(self, s_id: str, c_id: str) -> None:
        """Unregister a student from a course.

        Parameters
        ----------
        s_id : str
            Student ID.
        c_id : str
            Course ID.

        Returns
        -------
        None
        """
        self.conn.execute("DELETE FROM REGISTRATION WHERE s_id=? AND c_id=?", (s_id, c_id))
        self.conn.commit()

    def get_registrations(self, s_id: Optional[str] = None, c_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch registrations with optional filters.

        Parameters
        ----------
        s_id : str, optional
            Filter by student ID (optional).
        c_id : str, optional
            Filter by course ID (optional).

        Returns
        -------
        list
            List of registration records as dictionaries.
        """
        # build a small dynamic WHERE (not the fanciest way, but okay for the lab)
        q = "SELECT * FROM REGISTRATION WHERE 1=1"
        params: List[Any] = []
        if s_id:
            q += " AND s_id=?"; params.append(s_id)
        if c_id:
            q += " AND c_id=?"; params.append(c_id)
        cur = self.conn.execute(q, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    # ---------- SEARCH / FILTER ----------
    def search(self, table: str, **kwargs) -> List[Dict[str, Any]]:
        """Search any table by attribute filters.

        Parameters
        ----------
        table : str
            Table name (must be 'STUDENTS', 'INSTRUCTORS', 'COURSES', or 'REGISTRATION').
        **kwargs : dict
            Column filters (e.g., name='John'). Uses LIKE with wildcards.

        Returns
        -------
        list
            List of matching rows as dictionaries.

        Raises
        ------
        ValueError
            If table name is invalid.
        """
        # Example usage: repo.search('STUDENTS', name='John') -> fuzzy match on name
        if table not in ("STUDENTS", "INSTRUCTORS", "COURSES", "REGISTRATION"):
            raise ValueError("Invalid table name")
        q = f"SELECT * FROM {table} WHERE 1=1"
        params = []
        for k, v in kwargs.items():
            q += f" AND {k} LIKE ?"
            params.append(f"%{v}%")
        cur = self.conn.execute(q, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def backup(self, dest_path: str | os.PathLike) -> str:
        """Backup the database to a new file.

        Parameters
        ----------
        dest_path : str or Path
            Destination path (can be a directory or a file; if no extension, '.sqlite' is enforced).

        Returns
        -------
        str
            Absolute path of the backup file.
        """
        dest = Path(dest_path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Ensure the destination has a .sqlite or .db extension (optional nicety)
        if dest.suffix.lower() not in {".sqlite", ".db"}:
            dest = dest.with_suffix(".sqlite")  # I like .sqlite, but either works

        # Perform the backup (this uses SQLite's built-in backup API)
        with sqlite3.connect(dest) as backup_conn:
            # This copies the full database into `dest`
            self.conn.backup(backup_conn)

        return str(dest.resolve())

    # ---------- JSON IMPORT / EXPORT ----------
    def export_to_json(self, dest_path: Optional[str] = None) -> str:
        """Export full database (students, instructors, courses, registrations) to JSON.

        If ``dest_path`` is not provided, a timestamped file is created next to the DB.
        Returns the absolute path to the written JSON file.
        """
        import json
        from datetime import datetime

        data = {
            "students": self.get_all_students(),
            "instructors": self.get_all_instructors(),
            "courses": self.get_all_courses(),
            "registrations": self.get_registrations(),
        }

        if dest_path is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = (self.db_path.parent / f"export_{ts}.json").resolve()
        else:
            dest = Path(dest_path).resolve()
            dest.parent.mkdir(parents=True, exist_ok=True)

        with open(dest, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

        return str(dest)

    def import_from_json(self, src_path: str) -> bool:
        """Import database content from a JSON file produced by :meth:`export_to_json`.

        This replaces existing data. Returns True on success, False otherwise.
        """
        import json
        p = Path(src_path)
        if not p.exists():
            return False
        with open(p, "r", encoding="utf-8") as fp:
            payload = json.load(fp)

        try:
            cur = self.conn.cursor()
            cur.execute("PRAGMA foreign_keys = OFF;")
            # wipe existing data (order matters due to FKs)
            cur.execute("DELETE FROM REGISTRATION;")
            cur.execute("DELETE FROM COURSES;")
            cur.execute("DELETE FROM INSTRUCTORS;")
            cur.execute("DELETE FROM STUDENTS;")

            # re-insert in safe order: STUDENTS, INSTRUCTORS, COURSES, REGISTRATION
            for s in payload.get("students", []):
                cur.execute(
                    "INSERT INTO STUDENTS (student_id, name, age, email) VALUES (?, ?, ?, ?)",
                    (s["student_id"], s["name"], int(s["age"]), s["email"]),
                )
            for i in payload.get("instructors", []):
                cur.execute(
                    "INSERT INTO INSTRUCTORS (instructor_id, name, age, email) VALUES (?, ?, ?, ?)",
                    (i["instructor_id"], i["name"], int(i["age"]), i["email"]),
                )
            for c in payload.get("courses", []):
                cur.execute(
                    "INSERT INTO COURSES (course_id, course_name, i_id) VALUES (?, ?, ?)",
                    (c["course_id"], c["course_name"], c.get("i_id")),
                )
            for r in payload.get("registrations", []):
                cur.execute(
                    "INSERT OR IGNORE INTO REGISTRATION (s_id, c_id) VALUES (?, ?)",
                    (r["s_id"], r["c_id"]),
                )

            cur.execute("PRAGMA foreign_keys = ON;")
            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            return False

    def close(self):
        """Close the database connection.

        Returns
        -------
        None
        """
        # close politely (always a good idea)
        self.conn.close()
