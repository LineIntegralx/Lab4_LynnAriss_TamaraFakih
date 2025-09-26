"""
:module: tests.test_json_store_roundtrip
:synopsis: Round-trip JSON persistence test for Students, Instructors, and Courses.

This test creates a small in-memory graph of objects (students, instructor,
courses), wires up relationships, saves to JSON, then loads it back and checks
that IDs and links are restored correctly.

Notes
-----
- Uses pytest's ``tmp_path`` fixture to write to a temporary file.
- The goal is to sanity-check both serialization and re-hydration of relations.
"""

import os
from pathlib import Path
from src.models import Student, Instructor, Course
from src.persistence.json_store import save_to_json, load_from_json


def test_json_roundtrip(tmp_path: Path):
    """Create objects, persist to JSON, reload, and verify relations.

    Parameters
    ----------
    tmp_path : Path
        Temporary directory provided by pytest for file I/O.

    Returns
    -------
    None

    Notes
    -----
    - We test both directions of relations (student<->course, instructor<->course).
    - The assertions focus on IDs and membership, not exact object identity.
    """
    # build a tiny "world": 2 students, 1 instructor, 2 courses
    s1 = Student("Tamara", 22, "tamara@example.com", "S001")
    s2 = Student("Ali", 21, "ali@example.com", "S002")
    i1 = Instructor("Dr. Smith", 45, "smith@example.com", "I100")
    c1 = Course("EECE435", "Tools Lab")
    c2 = Course("EECE455", "Design")

    # wire up relationships (try a few combinations so we hit the code paths)
    c1.add_student(s1)
    c1.add_student(s2)
    c1.set_instructor(i1)
    i1.assign_course(c2)
    c2.add_student(s1)

    # save to a temp JSON file (round-trip target)
    out = tmp_path / "school.json"
    save_to_json(out, [s1, s2], [i1], [c1, c2])

    # load it back (this should rebuild the dictionaries + links)
    students, instructors, courses = load_from_json(out)

    # check that all entities made it back with the right IDs
    assert set(students.keys()) == {"S001", "S002"}
    assert set(instructors.keys()) == {"I100"}
    assert set(courses.keys()) == {"EECE435", "EECE455"}

    # grab loaded objects for readable assertions
    s1_loaded = students["S001"]
    i1_loaded = instructors["I100"]
    c1_loaded = courses["EECE435"]
    c2_loaded = courses["EECE455"]

    # verify bidirectional links survived the round-trip
    assert c1_loaded in s1_loaded.registered_courses
    assert s1_loaded in c1_loaded.enrolled_students
    assert c1_loaded.instructor is i1_loaded
    assert c2_loaded in i1_loaded.assigned_courses
