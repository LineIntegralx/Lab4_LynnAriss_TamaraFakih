"""
:module: models.course
:synopsis: Course entity with instructor and enrollment relations.

This module defines the ``Course`` domain class used by the School Management
System. A course has an ID, a name, an optional instructor, and a list of
enrolled students. It also handles basic relationship wiring with the
``Student`` and ``Instructor`` objects (local updates only).

Notes
-----
- Validation is delegated to ``src.validation.validators``.
- The relationship helpers here keep both sides in sync (student <-> course,
  instructor <-> course) using simple local methods. Kinda manual but fine for lab.
"""

from __future__ import annotations
from typing import Optional
from src.validation.validators import (
    is_valid_course_id, is_valid_course_name, norm_id, norm_name
)
from .student import Student
from .instructor import Instructor


class Course:
    """
    Course model representing a single course offering.

    Parameters
    ----------
    course_id : str
        External identifier of the course (validated, normalized).
    course_name : str
        Human-readable course title (validated, normalized).
    instructor : Instructor, optional
        The instructor initially assigned to this course (can be None).

    Attributes
    ----------
    course_id : str
        Normalized course ID (e.g., uppercased or trimmed).
    course_name : str
        Normalized course name.
    instructor : Instructor or None
        Current instructor or ``None`` if unassigned.
    enrolled_students : list[Student]
        List of students registered in this course.

    Notes
    -----
    - ``__slots__`` is used to keep the objects lightweight (and catch typos).
    - Relationship updates call corresponding "local" helpers to avoid recursion.
    """
    __slots__ = ("course_id", "course_name", "instructor", "enrolled_students")

    def __init__(self, course_id: str, course_name: str,
                 instructor: Optional[Instructor] = None) -> None:
        """Constructor method

        Parameters
        ----------
        course_id : str
            Proposed course identifier (must pass ``is_valid_course_id``).
        course_name : str
            Proposed course name (must pass ``is_valid_course_name``).
        instructor : Instructor, optional
            Optional initial instructor to attach.

        Raises
        ------
        ValueError
            If either ``course_id`` or ``course_name`` fails validation.

        Notes
        -----
        - Normalization is applied via ``norm_id`` and ``norm_name``.
        - If an instructor is provided, the bidirectional link is established.
        """
        # validate inputs first (keep it strict so data stays clean)
        if not is_valid_course_id(course_id): raise ValueError("Bad course_id.")
        if not is_valid_course_name(course_name): raise ValueError("Bad course_name.")
        # normalize strings so we don't store messy variations
        self.course_id = norm_id(course_id)
        self.course_name = norm_name(course_name)
        self.instructor = None
        self.enrolled_students: list[Student] = []
        # if we got an instructor, wire both sides carefully
        if instructor is not None:
            self._set_instructor_local(instructor)
            if self not in instructor.assigned_courses:
                instructor._add_course_local(self)

    def _add_student_local(self, student: Student) -> None:
        """Internal helper to append a student locally (no back-link).

        Parameters
        ----------
        student : Student
            Student object to add to ``enrolled_students``.

        Returns
        -------
        None

        Notes
        -----
        - This does not touch ``student.registered_courses`` on purpose.
        - Use ``add_student`` for public API that syncs both sides.
        """
        # local add only (caller handles the inverse side if needed)
        self.enrolled_students.append(student)

    def add_student(self, student: Student) -> None:
        """Public API to enroll a student and sync the inverse relation.

        Parameters
        ----------
        student : Student
            Student to enroll in this course.

        Returns
        -------
        None

        Notes
        -----
        - Prevents duplicates.
        - Ensures the student's ``registered_courses`` includes this course.
        """
        # sanity: only Student objects, and avoid duplicates
        if isinstance(student, Student) and student not in self.enrolled_students:
            self._add_student_local(student)
            if self not in student.registered_courses:
                student._add_course_local(self)

    def remove_student(self, student: Student) -> None:
        """Remove a student and clean up the inverse link if present.

        Parameters
        ----------
        student : Student
            Student to remove from enrollment.

        Returns
        -------
        None
        """
        # drop locally then remove from student's view if needed
        if student in self.enrolled_students:
            self.enrolled_students.remove(student)
            if self in student.registered_courses:
                student.registered_courses.remove(self)

    def _set_instructor_local(self, instructor: Instructor) -> None:
        """Internal helper to set the instructor locally (no back-link).

        Parameters
        ----------
        instructor : Instructor
            Instructor to assign locally.

        Returns
        -------
        None

        Notes
        -----
        - Use ``set_instructor`` for the full bidirectional update.
        """
        # simple local assignment (no touching instructor.assigned_courses)
        self.instructor = instructor

    def set_instructor(self, instructor: Optional[Instructor]) -> None:
        """Assign or clear the instructor and keep both sides in sync.

        Parameters
        ----------
        instructor : Instructor or None
            New instructor to assign or ``None`` to unassign.

        Returns
        -------
        None

        Notes
        -----
        - If setting to None, the old instructor (if any) loses this course.
        - If assigning a new instructor, the previous one is updated accordingly.
        - Early-return if the instructor is unchanged.
        """
        # no-op if same object (saves a bit of churn)
        if instructor is self.instructor:
            return
        old = self.instructor
        if instructor is None:
            # unassign case: remove from old.assigned_courses if present
            if old is not None and self in old.assigned_courses:
                old.assigned_courses.remove(self)
            self.instructor = None
            return
        # assign new; wire local then ensure instructor has us listed
        self._set_instructor_local(instructor)
        if self not in instructor.assigned_courses:
            instructor._add_course_local(self)
        # clean up old instructor if different
        if old is not None and old is not instructor and self in old.assigned_courses:
            old.assigned_courses.remove(self)

    def to_dict(self) -> dict:
        """Serialize the course to a plain dictionary.

        Returns
        -------
        dict
            Dict with keys: ``course_id``, ``course_name``, ``instructor_id``,
            and ``enrolled_student_ids``.

        Notes
        -----
        - IDs only for related objects (keeps payload small).
        """
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "instructor_id": self.instructor.instructor_id if self.instructor else None,
            "enrolled_student_ids": [s.student_id for s in self.enrolled_students],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Course":
        """Construct a course from a dictionary (instructor is not attached here).

        Parameters
        ----------
        d : dict
            Dictionary with at least ``course_id`` and ``course_name``.

        Returns
        -------
        Course
            New ``Course`` instance with no instructor assigned yet.

        Notes
        -----
        - The instructor is intentionally set to ``None``; attach it later if needed.
        """
        return cls(d["course_id"], d["course_name"], instructor=None)
