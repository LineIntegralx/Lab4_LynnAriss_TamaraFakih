"""
:module: tests.test_models_relations
:synopsis: Basic unit tests for Student–Course and Instructor–Course relations.

This module contains small pytest-style tests that check the bidirectional
linking between domain models:
- adding a student to a course syncs both sides,
- assigning/reassigning instructors updates both sides and cleans up old links,
- unregistering a student removes links from both objects.

Notes
-----
- Kept intentionally short and readable (lab style).
- These tests don't hit the database; they just exercise in-memory models.
"""

from src.models import Student, Instructor, Course


def test_student_course_linking():
    """Verify that adding a student to a course wires both sides.

    Returns
    -------
    None
        Asserts that:
        - ``s in c.enrolled_students``
        - ``c in s.registered_courses``

    Notes
    -----
    - Using the public ``add_student`` API (not the local helper).
    """
    s = Student("A B", 20, "a@b.com", "S001")
    c = Course("EECE435", "Tools")
    c.add_student(s)
    assert s in c.enrolled_students
    assert c in s.registered_courses


def test_instructor_assignment():
    """Verify that assigning an instructor sets both sides properly.

    Returns
    -------
    None
        Asserts that:
        - ``c in i.assigned_courses``
        - ``c.instructor is i``

    Notes
    -----
    - Using ``Instructor.assign_course`` which also updates ``course.instructor``.
    """
    i = Instructor("Dr X", 50, "x@y.com", "I001")
    c = Course("EECE455", "Design")
    i.assign_course(c)
    assert c in i.assigned_courses
    assert c.instructor is i


def test_instructor_reassignment_cleans_old():
    """Reassign instructor and ensure the old one loses the course.

    Returns
    -------
    None
        Asserts that:
        - ``c.instructor is i2``
        - ``c not in i1.assigned_courses``
        - ``c in i2.assigned_courses``

    Notes
    -----
    - Using the course-side API ``set_instructor`` to swap instructors.
    """
    i1 = Instructor("Dr A", 40, "a@x.com", "I001")
    i2 = Instructor("Dr B", 41, "b@x.com", "I002")
    c = Course("EECE460", "Systems")
    c.set_instructor(i1)
    c.set_instructor(i2)
    assert c.instructor is i2
    assert c not in i1.assigned_courses
    assert c in i2.assigned_courses


def test_unregister_and_remove():
    """Unregister a student from a course and verify both sides are updated.

    Returns
    -------
    None
        Asserts that:
        - ``s not in c.enrolled_students``
        - ``c not in s.registered_courses``

    Notes
    -----
    - We first add via course, then remove via student to cover both APIs.
    """
    s = Student("A B", 20, "a@b.com", "S001")
    c = Course("EECE435", "Tools")
    c.add_student(s)
    s.unregister_course(c)
    assert s not in c.enrolled_students
    assert c not in s.registered_courses
