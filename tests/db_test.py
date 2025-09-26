"""
:module: examples.sqlite_repo_demo
:synopsis: Tiny demo script showing basic usage of SQLiteRepository.

This script does a super quick end-to-end run:
- create a repo (connects to SQLite),
- add a student, instructor, course,
- register the student in the course,
- update the student,
- run a fuzzy search,
- then clean up (delete + close).

Notes
-----
- This is just for testing the repository API during the lab.
- No error handling here on purpose (keep it simple to see failures).
"""

from db.sqlite_repo import SQLiteRepository

# make a repo instance (opens the db; enables FK) — basic happy path demo
repo = SQLiteRepository()

# Add records (yeah, IDs are super simple here — good enough for the example)
repo.add_student("S001", "Alice", 20, "alice@example.com")
repo.add_instructor("I001", "Dr. Smith", 45, "smith@example.com")
repo.add_course("CSE101", "Intro to CS", "I001")

# Register student in course (should wire both sides internally)
repo.register_student("S001", "CSE101")

# Update student (pretend Alice had a birthday 🎂)
repo.update_student("S001", age=21)

# Search students (LIKE '%Alice%'); just to see something printed
print(repo.search("STUDENTS", name="Alice"))

# Delete (cleanup so the demo is idempotent-ish) and close the connection
repo.delete_student("S001")
repo.close()
