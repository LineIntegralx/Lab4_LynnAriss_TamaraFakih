"""
:module: src.persistence.json_store
:synopsis: JSON persistence for Students, Instructors, and Courses.

This module provides two helpers to save/load the in-memory model objects
(``Student``, ``Instructor``, ``Course``) to/from a JSON file. It also exposes a
tiny in-memory ``Repository`` wrapper that groups the three dictionaries and
offers simple add/save/load utilities.

Notes
-----
- Schema is versioned via ``_SCHEMA_VERSION`` for future changes (basic).
- Relationships are re-hydrated after object construction to avoid recursion.
- Intentionally lightweight for the lab (no fancy error handling here).
"""

from __future__ import annotations
from pathlib import Path
import json
from typing import Iterable, Tuple, Dict, Any
from ..models import Student, Instructor, Course

_SCHEMA_VERSION = 1


def save_to_json(path: str | Path,
                 students: Iterable[Student],
                 instructors: Iterable[Instructor],
                 courses: Iterable[Course]) -> None:
    """Serialize models to a JSON file (atomic via temp file + replace).

    Parameters
    ----------
    path : str or Path
        Destination JSON file path.
    students : Iterable[Student]
        Students to serialize (iterable is enough; values() from a dict works).
    instructors : Iterable[Instructor]
        Instructors to serialize.
    courses : Iterable[Course]
        Courses to serialize.

    Returns
    -------
    None

    Notes
    -----
    - Writes to ``<path>.tmp`` first then replaces the target (safer on crash).
    - Uses UTF-8 and ``ensure_ascii=False`` so names/emails look normal.
    """
    # build the payload dict (IDs for relations are already in to_dict())
    data = {
        "schema_version": _SCHEMA_VERSION,
        "students": [s.to_dict() for s in students],
        "instructors": [i.to_dict() for i in instructors],
        "courses": [c.to_dict() for c in courses],
    }
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)  # make sure folder exists
    tmp = p.with_suffix(p.suffix + ".tmp")       # temp path for atomic write
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)  # atomic-ish on most OSes (good enough for lab)


def load_from_json(path: str | Path) -> Tuple[Dict[str, Student], Dict[str, Instructor], Dict[str, Course]]:
    """Load models from a JSON file and re-wire their relationships.

    Parameters
    ----------
    path : str or Path
        Source JSON file path.

    Returns
    -------
    tuple(dict[str, Student], dict[str, Instructor], dict[str, Course])
        Three dictionaries keyed by their IDs.

    Notes
    -----
    - Objects are constructed first from their base fields (no relations),
      then relationships are attached in a second pass using IDs.
    - Order of re-wiring matters a bit, so we do students/courses/instructors
      carefully to avoid missing links.
    """
    p = Path(path)
    data: Dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))

    students_by_id: Dict[str, Student] = {}
    instructors_by_id: Dict[str, Instructor] = {}
    courses_by_id: Dict[str, Course] = {}

    # 1) build plain objects (no links yet)
    for sd in data.get("students", []):
        s = Student.from_dict(sd)
        students_by_id[s.student_id] = s

    for idd in data.get("instructors", []):
        i = Instructor.from_dict(idd)
        instructors_by_id[i.instructor_id] = i

    for cd in data.get("courses", []):
        c = Course.from_dict(cd)
        courses_by_id[c.course_id] = c

    # 2) re-hydrate student <-> course links
    for sd in data.get("students", []):
        s = students_by_id.get(sd["student_id"])
        for cid in sd.get("registered_course_ids", []):
            c = courses_by_id.get(cid)
            if s and c:
                c.add_student(s)  # add_student syncs both sides

    # 3) re-hydrate course -> instructor + make sure enrolled students are present
    for cd in data.get("courses", []):
        c = courses_by_id.get(cd["course_id"])
        iid = cd.get("instructor_id")
        if c and iid:
            ins = instructors_by_id.get(iid)
            if ins:
                c.set_instructor(ins)  # will sync inverse link
        for sid in cd.get("enrolled_student_ids", []):
            s = students_by_id.get(sid)
            if c and s:
                c.add_student(s)

    # 4) re-hydrate instructor -> courses (double-checks inverse is set)
    for idd in data.get("instructors", []):
        i = instructors_by_id.get(idd["instructor_id"])
        for cid in idd.get("assigned_course_ids", []):
            c = courses_by_id.get(cid)
            if i and c:
                i.assign_course(c)

    return students_by_id, instructors_by_id, courses_by_id


class Repository:
    """
    Minimal in-memory repository for the three entity types.

    Attributes
    ----------
    students : dict[str, Student]
        Students keyed by ``student_id``.
    instructors : dict[str, Instructor]
        Instructors keyed by ``instructor_id``.
    courses : dict[str, Course]
        Courses keyed by ``course_id``.

    Notes
    -----
    - This is intentionally small/naive (lab-friendly). No conflicts checks, etc.
    - Use ``save`` / ``load`` to persist/restore from JSON.
    """

    def __init__(self) -> None:
        """Constructor method

        Returns
        -------
        None
        """
        # just three dicts; easy to reason about in the lab
        self.students: Dict[str, Student] = {}
        self.instructors: Dict[str, Instructor] = {}
        self.courses: Dict[str, Course] = {}

    def add_student(self, s: Student) -> None:
        """Add/replace a student in the repository (keyed by ID).

        Parameters
        ----------
        s : Student
            Student instance to store.

        Returns
        -------
        None

        Notes
        -----
        - Overwrites silently if the same ID already exists (simple behavior).
        """
        self.students[s.student_id] = s

    def add_instructor(self, i: Instructor) -> None:
        """Add/replace an instructor in the repository.

        Parameters
        ----------
        i : Instructor
            Instructor instance to store.

        Returns
        -------
        None
        """
        self.instructors[i.instructor_id] = i

    def add_course(self, c: Course) -> None:
        """Add/replace a course in the repository.

        Parameters
        ----------
        c : Course
            Course instance to store.

        Returns
        -------
        None
        """
        self.courses[c.course_id] = c

    def save(self, path: str | Path) -> None:
        """Persist the current repository state to a JSON file.

        Parameters
        ----------
        path : str or Path
            Destination JSON file path.

        Returns
        -------
        None
        """
        # delegate to the module-level function (keeps logic in one place)
        save_to_json(path, self.students.values(), self.instructors.values(), self.courses.values())

    @classmethod
    def load(cls, path: str | Path) -> "Repository":
        """Load a repository from a JSON file.

        Parameters
        ----------
        path : str or Path
            Source JSON file path.

        Returns
        -------
        Repository
            New repository instance populated with loaded data.

        Notes
        -----
        - Uses the module-level ``load_from_json`` and stuffs the dicts back in.
        """
        repo = cls()
        s, i, c = load_from_json(path)
        repo.students, repo.instructors, repo.courses = s, i, c
        return repo
