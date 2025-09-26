# 🎓 School Management System

## 🧭 Project Overview

The **School Management System** is a desktop application built with **Python** and **PyQt5/Tkinter** that provides an intuitive interface for managing academic data in a school or university setting. Our interface was specifically designed for the American University of Beirut (AUB).
It allows administrators, teachers, or staff to efficiently **create, manage, and organize** information about **students, instructors, and courses** — all in one place, with an easy-to-use graphical user interface.

The system demonstrates **full-stack desktop application development** in Python, combining:

- A **modern GUI** (PyQt5) or a lightweight alternative (Tkinter)
- A **SQLite database** backend for data persistence
- Structured, object-oriented domain models for **Students**, **Instructors**, and **Courses**

---

## ✨ Features

- 👤 **Student Management** – Add, update, delete, and search student records (name, age, email, ID).  
- 👨‍🏫 **Instructor Management** – Manage instructors with their personal data and assigned courses.  
- 📚 **Course Management** – Create and assign courses to instructors, and manage enrolled students.  
- 📝 **Registration System** – Register or unregister students from courses with bidirectional data consistency.  
- 🔎 **Search & Display** – View and search all records in a dynamic, sortable table.  
- 💾 **Data Persistence** – Store all information locally in a SQLite database.  
- 📤 **Import & Export** – Backup, restore, or export data to JSON and CSV formats.  
- 🧪 **Tested & Modular** – Fully unit-tested model layer and serialization logic.

---

## 🧱 Architecture Overview

The project follows a modular, layered structure:

├── gui/ # PyQt5 + Tkinter GUI entry points

├── src/
│ ├── models/ # Core domain models (Student, Instructor, Course, Person)
│ ├── validation/ # Validation and normalization helpers
│ └── persistence/ # JSON persistence logic
├── db/ # SQLite repository implementation
├── tests/ # Unit tests with pytest
├── examples/ # Example/demo scripts
├── docs/ # Documentation helpers (for Sphinx)
├── requirements.txt # Project dependencies
└── README.md # Project documentation

yaml
Copy code

---

## 🚀 Getting Started

### 1. ✅ Prerequisites

- Python **3.9+** must be installed on your system  
- `git` installed for cloning the repository

Check your Python version:

```bash
python --version
2. 📥 Clone the Repository
Use git to clone the project locally:

bash
Copy code
git clone https://github.com/<your-username>/<your-repo-name>.git
Then navigate into the project directory:

bash
Copy code
cd <your-repo-name>
3. 🧪 Create a Virtual Environment (Recommended)
It’s best practice to create a virtual environment to isolate project dependencies.

Windows (PowerShell):

bash
Copy code
python -m venv venv
venv\Scripts\activate
macOS / Linux:

bash
Copy code
python3 -m venv venv
source venv/bin/activate
4. 📦 Install Dependencies
Install the required Python packages using pip:

bash
Copy code
pip install -r requirements.txt
If you encounter issues with PyQt5, you can install it manually:

bash
Copy code
pip install PyQt5
5. 🗃️ (Optional) Initialize the Database
The SQLite database is automatically created on first run.
If you want to start from scratch, simply delete the existing .db file (e.g., school.db).

6. 🚀 Run the Application
Launch the application using the GUI chooser script:

bash
Copy code
python gui/choose_gui.py
You will be prompted to choose between:

PyQt5 – Full-featured modern interface

Tkinter – Lightweight fallback GUI

7. 🔍 Run Unit Tests (Optional)
You can verify that everything is working correctly by running the test suite:

bash
Copy code
pytest
📸 Example Features in Action
Once the application is running, you can:

➕ Add new students, instructors, and courses

🔄 Edit or delete existing records

📚 Register students into courses and manage enrollments

🔎 Search for records by name or ID

💾 Export and import data as JSON or CSV

📤 Backup and restore the entire database with one click

🧪 Project Structure Explanation
GUI Layer (gui/) – Contains the main graphical interface using PyQt5 and a launcher using Tkinter.

Models (src/models/) – Defines the core domain classes (Student, Instructor, Course, Person).

Validation (src/validation/) – Handles input validation and normalization using regex and utility functions.

Persistence (src/persistence/) – Handles JSON serialization and deserialization for saving/loading data.

Database (db/) – Contains the SQLiteRepository that performs CRUD operations on the database.

Tests (tests/) – Pytest-based tests verifying relationships, serialization, and object logic.

📜 Example CLI Commands
To run the app:

bash
Copy code
python gui/choose_gui.py
To run tests:

bash
Copy code
pytest
To export data as JSON:

bash
Copy code
python -m src.persistence.json_store
🛠️ Troubleshooting
❗ PyQt5 ImportError:
Make sure it’s installed:

bash
Copy code
pip install PyQt5
❗ tkinter not found:
tkinter is part of the Python standard library. If missing, install it using your OS package manager:

Ubuntu/Debian: sudo apt install python3-tk

macOS: Usually included with Python

Windows: Included with official Python installer

📜 License
This project is created for educational and demonstration purposes.
You are free to modify, distribute, and adapt it for your own learning or projects.

🤝 Contributing
Contributions are welcome!
If you’d like to improve the project:

Fork the repository

Create a new feature branch

Commit your changes

Submit a pull request 🚀

👩‍💻 Author
Developed by [Your Name] – a demonstration project for Python desktop app development with databases and GUI frameworks.

⭐ Acknowledgements
Built with Python

GUI powered by PyQt5 and Tkinter

Database layer with SQLite

Documentation generated with Sphinx

markdown
Copy code

✅ **Tips before committing:**
- Replace `<your-username>` and `<your-repo-name>` with your actual GitHub repo path.
- Add your name in the **Author** section.
- Optionally insert screenshots using:

```markdown
![App Screenshot](images/screenshot.png)
