"""
:module: src.validation.__init__
:synopsis: Convenience re-exports for validation helpers (checks + normalizers).

This package exposes the most commonly used validation/normalization functions
so other modules can import them straight from ``src.validation`` without
reaching into the ``validators`` module every time.

Notes
-----
- Keeping an explicit ``__all__`` so docs + linters know the public API.
- This is purely an aggregator (aka barrel); no logic lives here.
"""

# pull selected helpers up to the package level, so elsewhere we can:
#   from src.validation import is_valid_email, norm_name, ...
# feels cleaner in the app code
from .validators import (
    is_non_empty_string,
    is_valid_email,
    is_non_negative_int,
    is_valid_person_name,
    is_valid_student_id,
    is_valid_instructor_id,
    is_valid_course_id,
    is_valid_course_name,
    norm_email,
    norm_id,
    norm_name,
)

# define what the package publicly exports (helps Sphinx + autocomplete)
# I’m just listing what we actually want to expose; keeps things tidy.
__all__ = [
    "is_non_empty_string",
    "is_valid_email",
    "is_non_negative_int",
    "is_valid_person_name",
    "is_valid_student_id",
    "is_valid_instructor_id",
    "is_valid_course_id",
    "is_valid_course_name",
    "norm_email",
    "norm_id",
    "norm_name",
]
