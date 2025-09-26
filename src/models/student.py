"""
:module: models.student
:synopsis: Student entity extending Person; manages course registrations.

This module defines the ``Student`` domain class used by the School Management
System. A student has a validated/normalized ID and keeps a list of courses
they are registered in. Helpers keep the student<->course relationship in sync.

Notes
-----
- Validation/normalization is delegated to ``src.validation.validators``.
- We keep "local" helpers (no recursion) to update each side intentionally.
- ``__slots__`` used to keep instances lightweight and catch typos.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from .person import Person
from src.validation.validators import is_valid_student_id, norm_id
if TYPE_CHECKING:
    from .course import Course


class Student(Person):
    """
    Student model; inherits name/age/email from ``Person`` and adds a student ID
    plus the list of registered courses.

    Parameters
    ----------
    name : str
        Student's name (validated in Person).
    age : int
        Student's age (validated in Person).
    email : str
        Student's email (validated in Person).
    student_id : str
        External identifier for the student (validated, normalized).

    Attributes
    ----------
    student_id : str
        Normalized student ID (via ``norm_id``).
    registered_courses : list[Course]
        Courses this student is currently registered in.

    Notes
    -----
    - Relationship maintenance tries to be simple and explicit.
    """
    __slots__ = ("student_id", "registered_courses")

    def __init__(self, name: str, age: int, email: str, student_id: str) -> None:
        """Constructor method

        Parameters
        ----------
        name : str
            Student's name.
        age : int
            Student's age.
        email : str
            Student's email.
        student_id : str
            Proposed ID (must pass ``is_valid_student_id``).

        Raises
        ------
        ValueError
            If ``student_id`` is invalid.

        Notes
        -----
        - Calls ``super().__init__`` first to reuse Person validation.
        - Then validates and normalizes the student ID.
        """
        # init base fields (name/age/email) first
        super().__init__(name, age, email)
        # validate the id then normalize it so it's consistent in the system
        if not is_valid_student_id(student_id): raise ValueError("Bad student_id.")
        self.student_id = norm_id(student_id)
        # start with an empty course list (we'll wire as we register)
        self.registered_courses: list["Course"] = []

    def _add_course_local(self, course: "Course") -> None:
        """Internal helper to append a course locally (no back-link).

        Parameters
        ----------
        course : Course
            Course to add to ``registered_courses``.

        Returns
        -------
        None

        Notes
        -----
        - Use ``register_course`` for the public API that syncs both sides.
        """
        # only touch our own list; caller handles the course side
        self.registered_courses.append(course)

    def register_course(self, course: "Course") -> None:
        """Register this student into a course and sync the inverse relation.

        Parameters
        ----------
        course : Course
            Course to register in (ignored if falsy).

        Returns
        -------
        None

        Notes
        -----
        - Prevents duplicates in ``registered_courses``.
        - Ensures ``course.enrolled_students`` includes this student.
        """
        # basic checks then wire both sides if needed
        if course and course not in self.registered_courses:
            self._add_course_local(course)
            if self not in course.enrolled_students:
                course._add_student_local(self)

    def unregister_course(self, course: "Course") -> None:
        """Unregister this student from a course and clean up the inverse link.

        Parameters
        ----------
        course : Course
            Course to remove.

        Returns
        -------
        None
        """
        # remove locally then remove from the course if present
        if course in self.registered_courses:
            self.registered_courses.remove(course)
            if self in course.enrolled_students:
                course.enrolled_students.remove(self)

    def list_registered_courses(self) -> str:
        """Return a human-readable string of registered course IDs (also prints it).

        Returns
        -------
        str
            Message of the form:
            ``"The student <name> of id <student_id> is registered in the following courses: <ids>"``

        Notes
        -----
        - Also prints the same message for quick manual checking.
        - If none, shows "no courses".
        """
        # quick summary for debugging/testing in REPL
        courses = ", ".join(c.course_id for c in self.registered_courses) or "no courses"
        msg = f"The student {self.name} of id {self.student_id} is registered in the following courses: {courses}"
        print(msg)
        return msg

    def to_dict(self) -> dict:
        """Serialize the student to a plain dictionary.

        Returns
        -------
        dict
            Dict with person fields + ``student_id`` and ``registered_course_ids``.

        Notes
        -----
        - Related objects are represented by their IDs only.
        """
        # reuse base dict then add student-specific fields
        d = self._person_dict()
        d.update({"student_id": self.student_id})
        d["registered_course_ids"] = [c.course_id for c in self.registered_courses]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Student":
        """Construct a Student from a dictionary.

        Parameters
        ----------
        d : dict
            Dictionary containing at least ``name``, ``age``, ``email``, and ``student_id``.

        Returns
        -------
        Student
            New ``Student`` instance (courses are not attached here).

        Notes
        -----
        - Courses are intentionally not wired here; attach them later if needed.
        """
        return cls(d["name"], d["age"], d["email"], d["student_id"])
