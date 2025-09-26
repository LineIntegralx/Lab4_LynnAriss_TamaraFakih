"""
:module: models.__init__
:synopsis: Convenience re-exports for domain models (Student, Course, Instructor, Person).

This package `models` exposes the main domain classes so other modules can import
them directly from `models` instead of digging into individual files.

Notes
-----
- This is just an import aggregator (aka "barrel") for nicer imports in the app.
- Keeping `__all__` explicit so Sphinx + linters know what we intend to export.
- No logic here, literally just re-exports.
"""

# pull the classes from their files so we can write: from models import Student, ...
# (felt cleaner than repeating long relative paths everywhere)
from .student import Student
from .course import Course
from .instructor import Instructor
from .person import Person

# export list — this helps autocomplete and keeps the public API tidy
# (also Sphinx respects this when generating docs)
__all__ = ["Student", "Course", "Instructor", "Person"]
