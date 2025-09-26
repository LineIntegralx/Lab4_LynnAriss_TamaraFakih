"""
School Management System

A Python-based School Management System that supports both SQLite database integration and JSON persistence, with two graphical user interface (GUI) options: PyQt5 and Tkinter.
The system enables managing students, instructors, and courses, with full CRUD operations, search, relationships (student-course registration, instructor-course assignment), and database backup.

✨ Features

Students

Add, update, delete students

Register students to courses

View/search student details with enrolled courses

Instructors

Add, update, delete instructors

Assign instructors to courses

View/search instructor details with assigned courses

Courses

Add, update, delete courses (optionally assign instructor)

Manage enrolled students

View/search course details with instructor and students

CRUD Support: Full create, read, update, delete operations with input validation.

Database: Uses SQLite (school.db) as the main persistent storage.

JSON Persistence: Import/export records to JSON files.

Search & Records Tab: Filter and display students, instructors, and courses simultaneously.

Database Backup: Export the SQLite database file to a user-specified location.

Validation: Robust checks for IDs, names, emails, and numeric inputs.

Two GUI Options:

qt_app_db.py: PyQt5-based GUI

tkinter_app_db.py: Tkinter-based GUI

📂 Folder Structure
SCHOOL_MANAGEMENT_SYSTEM/
│
├── db/                     # Database layer
│   ├── init_db.py          # Initializes the SQLite schema (tables, constraints)
│   ├── school.db           # SQLite database file
│   └── sqlite_repo.py      # Repository class for CRUD operations on SQLite
│
├── src/
│   ├── gui/                # User interfaces
│   │   ├── qt_app_db.py    # PyQt5 GUI (with SQLite + JSON support + DB backup)
│   │   ├── qt_app.py       # PyQt5 GUI (JSON-only, no DB integration)
│   │   ├── tkinter_app_db.py # Tkinter GUI with SQLite + JSON support
│   │   └── tkinter_app.py  # Tkinter GUI (JSON-only, no DB integration)
│   │
│   ├── models/             # Domain models
│   │   ├── person.py       # Base class (Person with validation & attributes)
│   │   ├── student.py      # Student model (inherits Person, adds student_id & courses)
│   │   ├── instructor.py   # Instructor model (inherits Person, adds instructor_id & courses)
│   │   └── course.py       # Course model (course_id, course_name, relationships)
│   │
│   ├── persistence/        # Persistence utilities
│   │   └── json_store.py   # Save/load data to/from JSON
│   │
│   └── validation/         # Validation logic
│       └── validators.py   # Input validators (IDs, names, email, etc.)
│
├── tests/                  # Unit tests
│   ├── db_test.py          # Tests for database operations
│   ├── test_models.py      # Tests for models (student, instructor, course)
│   ├── test_persistence.py # Tests for JSON persistence
│   └── conftest.py         # Pytest config
│
├── data/                   
│   ├── logo.png            # Image for the GUI
├── .venv/                  # Virtual environment (not included in final submission)
├── README.py               # Documentation (this file)
└── requirements.txt        # All required dependencies

⚙️ Installation & Setup

Clone or unzip the project:

unzip School_Management_System.zip
cd School_Management_System


Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows


Install dependencies:

pip install -r requirements.txt


Dependencies include:

PyQt5
pytest (for testing)

🚀 Running the Application
Option 1: PyQt5 GUI with SQLite
python -m src.gui.qt_app_db

Option 2: Tkinter GUI with SQLite
python -m src.gui.tkinter_app_db

Option 3: JSON-only PyQt5
python -m src.gui.qt_app

Option 4: JSON-only Tkinter
python -m src.gui.tkinter_app

🗄 Database

Schema is defined in db/init_db.py and initialized into school.db.

Tables include:

STUDENTS(student_id, name, age, email)

INSTRUCTORS(instructor_id, name, age, email)

COURSES(course_id, course_name, i_id)

REGISTRATION(s_id, c_id)

Supports constraints: foreign keys, uniqueness, referential integrity.

💾 Backup

Both GUIs include an option to backup the database:

User selects a location, and the current school.db is copied to that path.

🧪 Testing

Run the test suite using pytest:

pytest


Covers:

Model validation

Persistence (JSON save/load)

Database repository (CRUD correctness)

📌 Notes

school.db is included for demonstration.

Always re-run db/init_db.py if schema reset is needed.

JSON import/export is for quick data sharing; SQLite is the primary storage.
"""