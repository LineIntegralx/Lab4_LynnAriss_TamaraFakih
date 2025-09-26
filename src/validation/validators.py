"""
:module: src.validation.validators
:synopsis: Regex-based validators and simple normalization helpers.

This module centralizes basic input validation (email, IDs, names, etc.) and
provides tiny normalization functions used across the School Management System.

Notes
-----
- Regexes are intentionally conservative to keep the lab predictable.
- Normalizers aim for "reasonable" cleanup (case/spacing), not perfect i18n.
"""

import re
from typing import Any, Iterable  # Iterable kept in case we add list validators later

# --- Compiled patterns (tweak here if the course wants different formats) ---
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
COURSE_ID_RE = re.compile(r"^[A-Z]{2,4}\d{3}[A-Z]?$")          # e.g., EECE435 or EECE435L
STUDENT_ID_RE = re.compile(r"^[A-Z]?\d{3,10}$")                 # simple: optional letter + 3-10 digits
INSTRUCTOR_ID_RE = re.compile(r"^[A-Z]?\d{3,10}$")              # same format as student for the lab
COURSE_NAME_RE = re.compile(r"^[A-Za-z0-9 .,&()/_-]{3,60}$")    # allow common punctuation
PERSON_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .'-]{1,58}[A-Za-z]$")  # basic Western-ish names


def is_non_empty_string(v: Any) -> bool:
    """Check that ``v`` is a non-empty (non-whitespace-only) string.

    Parameters
    ----------
    v : Any
        Value to check.

    Returns
    -------
    bool
        ``True`` if ``v`` is a non-empty string, else ``False``.
    """
    # quick guard for user text inputs
    return isinstance(v, str) and v.strip() != ""


def is_valid_email(v: Any) -> bool:
    """Validate email using a simple regex (not RFC-perfect, but fine for lab).

    Parameters
    ----------
    v : Any
        Value to check.

    Returns
    -------
    bool
        ``True`` if ``v`` matches ``EMAIL_RE``, else ``False``.
    """
    return isinstance(v, str) and bool(EMAIL_RE.fullmatch(v.strip()))


def is_non_negative_int(v: Any) -> bool:
    """Return True if ``v`` can be cast to ``int`` and is ``>= 0``.

    Parameters
    ----------
    v : Any
        Value to check.

    Returns
    -------
    bool
        ``True`` for non-negative integers (after casting), else ``False``.
    """
    try:
        return int(v) >= 0
    except (TypeError, ValueError):
        return False


def is_valid_person_name(v: Any) -> bool:
    """Validate a person's name against ``PERSON_NAME_RE``.

    Parameters
    ----------
    v : Any
        Value to check.

    Returns
    -------
    bool
        ``True`` if name matches allowed pattern, else ``False``.

    Notes
    -----
    - This is pretty opinionated and not globally inclusive; okay for the lab.
    """
    return isinstance(v, str) and bool(PERSON_NAME_RE.fullmatch(v.strip()))


def is_valid_student_id(v: Any) -> bool:
    """Validate a student ID using ``STUDENT_ID_RE``.

    Parameters
    ----------
    v : Any
        Value to check.

    Returns
    -------
    bool
        ``True`` if matches the expected pattern, else ``False``.
    """
    return isinstance(v, str) and bool(STUDENT_ID_RE.fullmatch(v.strip()))


def is_valid_instructor_id(v: Any) -> bool:
    """Validate an instructor ID using ``INSTRUCTOR_ID_RE``.

    Parameters
    ----------
    v : Any
        Value to check.

    Returns
    -------
    bool
        ``True`` if matches the expected pattern, else ``False``.
    """
    return isinstance(v, str) and bool(INSTRUCTOR_ID_RE.fullmatch(v.strip()))


def is_valid_course_id(v: Any) -> bool:
    """Validate a course ID (e.g., ``EECE435`` or ``EECE435L``).

    Parameters
    ----------
    v : Any
        Value to check.

    Returns
    -------
    bool
        ``True`` if matches ``COURSE_ID_RE``, else ``False``.
    """
    return isinstance(v, str) and bool(COURSE_ID_RE.fullmatch(v.strip()))


def is_valid_course_name(v: Any) -> bool:
    """Validate a course name for basic characters/length.

    Parameters
    ----------
    v : Any
        Value to check.

    Returns
    -------
    bool
        ``True`` if matches ``COURSE_NAME_RE``, else ``False``.
    """
    return isinstance(v, str) and bool(COURSE_NAME_RE.fullmatch(v.strip()))


# --- normalization helpers (tiny but used everywhere) ---

def norm_email(s: str) -> str:
    """Normalize email by trimming and lowercasing.

    Parameters
    ----------
    s : str
        Email string.

    Returns
    -------
    str
        Normalized email (lowercase).
    """
    return s.strip().lower()


def norm_id(s: str) -> str:
    """Normalize an ID by trimming and uppercasing.

    Parameters
    ----------
    s : str
        Identifier string.

    Returns
    -------
    str
        Normalized ID (uppercase).
    """
    return s.strip().upper()


def norm_name(s: str) -> str:
    """Normalize a name with title-case and single spaces.

    Parameters
    ----------
    s : str
        Name string.

    Returns
    -------
    str
        Normalized name (title-cased, internal whitespace squashed).

    Notes
    -----
    - This will "pretty up" names like ``"  aLiCe   o'connor  "`` → ``"Alice O'Connor"``.
    """
    return " ".join(s.strip().title().split())
