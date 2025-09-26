"""
:module: models.instructor
:synopsis: Instructor entity extending Person; manages assigned courses.

This module defines the ``Instructor`` domain class used by the School Management
System. An instructor has a validated/normalized ID and keeps a list of courses
they are assigned to. Basic helpers maintain bidirectional links with ``Course``.

Notes
-----
- Validation/normalization is delegated to ``src.validation.validators``.
- We use small "local" helpers (no recursion) to keep both sides in sync.
- ``__slots__`` is used to keep objects lightweight and catch attr typos.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from .person import Person
from src.validation.validators import is_valid_instructor_id, norm_id
if TYPE_CHECKING:
    from .course import Course


class Instructor(Person):
    """
    Instructor model; inherits name/age/email from ``Person`` and adds an ID
    plus the list of assigned courses.

    Parameters
    ----------
    name : str
        Instructor's name (validated in Person).
    age : int
        Instructor's age (validated in Person).
    email : str
        Instructor's email (validated in Person).
    instructor_id : str
        External identifier for the instructor (validated, normalized).

    Attributes
    ----------
    instructor_id : str
        Normalized instructor ID (e.g., trimmed/uppercased by ``norm_id``).
    assigned_courses : list[Course]
        Courses currently assigned to this instructor.

    Notes
    -----
    - Keep list maintenance simple; we call "local" helpers to avoid loops.
    """
    __slots__ = ("instructor_id", "assigned_courses")

    def __init__(self, name: str, age: int, email: str, instructor_id: str) -> None:
        """Constructor method

        Parameters
        ----------
        name : str
            Instructor's name.
        age : int
            Instructor's age.
        email : str
            Instructor's email.
        instructor_id : str
            Proposed ID (must pass ``is_valid_instructor_id``).

        Raises
        ------
        ValueError
            If ``instructor_id`` is invalid.

        Notes
        -----
        - We call ``super().__init__`` first to reuse Person validation.
        - Then validate + normalize the instructor ID.
        """
        # init base person fields first (name/age/email)
        super().__init__(name, age, email)
        # make sure the id is decent before storing it
        if not is_valid_instructor_id(instructor_id): raise ValueError("Bad instructor_id.")
        self.instructor_id = norm_id(instructor_id)
        # start with no courses assigned
        self.assigned_courses: list["Course"] = []

    def _add_course_local(self, course: "Course") -> None:
        """Internal helper to append a course locally (no back-link).

        Parameters
        ----------
        course : Course
            Course to add to ``assigned_courses``.

        Returns
        -------
        None

        Notes
        -----
        - Use ``assign_course`` for the public API that syncs both sides.
        """
        # local add only; the caller handles wiring on the course side
        self.assigned_courses.append(course)

    def assign_course(self, course: "Course") -> None:
        """Assign a course to this instructor and sync the inverse relation.

        Parameters
        ----------
        course : Course
            Course to assign (ignored if falsy).

        Returns
        -------
        None

        Notes
        -----
        - Prevents duplicates in ``assigned_courses``.
        - Ensures ``course.instructor`` points to ``self``.
        - Cleans up the old instructor if the course was previously assigned.
        """
        # sanity checks then add if missing; keep both sides consistent
        if not course:
            return
        if course not in self.assigned_courses:
            self._add_course_local(course)
        if getattr(course, "instructor", None) is not self:
            old = course.instructor
            course._set_instructor_local(self)
            if old is not None and old is not self and course in old.assigned_courses:
                old.assigned_courses.remove(course)

    def list_assigned_courses(self) -> str:
        """Return a human-readable string of assigned course IDs (also prints it).

        Returns
        -------
        str
            Message of the form:
            ``"The instructor <name> of id <instructor_id> is assigned to the following courses: <ids>"``

        Notes
        -----
        - Also prints the same message for convenience during manual testing.
        - If there are no courses, returns "no courses".
        """
        # build a small summary string; useful when debugging in the shell
        courses = ", ".join(c.course_id for c in self.assigned_courses) or "no courses"
        msg = f"The instructor {self.name} of id {self.instructor_id} is assigned to the following courses: {courses}"
        print(msg)
        return msg

    def to_dict(self) -> dict:
        """Serialize the instructor to a plain dictionary.

        Returns
        -------
        dict
            Dict with person fields + ``instructor_id`` and ``assigned_course_ids``.

        Notes
        -----
        - Related objects are represented by their IDs only.
        """
        # leverage Person's dict, then extend with instructor-specific bits
        d = self._person_dict()
        d.update({
            "instructor_id": self.instructor_id,
            "assigned_course_ids": [c.course_id for c in self.assigned_courses],
        })
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Instructor":
        """Construct an Instructor from a dictionary.

        Parameters
        ----------
        d : dict
            Dictionary containing at least ``name``, ``age``, ``email``, and ``instructor_id``.

        Returns
        -------
        Instructor
            New ``Instructor`` instance (courses are not attached here).

        Notes
        -----
        - Courses are intentionally not wired here; attach them later as needed.
        """
        return cls(d["name"], d["age"], d["email"], d["instructor_id"])
