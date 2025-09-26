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

- `data/` — Some visuals needed for the GUI
- `db/` — SQLite repository  and db initialization script
- `docs/` — Full Sphinx documentation
- `src/gui/` — GUI application  (choosing, Tkinter, and PyQt)
- `src/models/` — Student, Instructor, Course, Person  
- `src/validation/` — Validators & normalizers  
- `src/persistence/` — JSON store (save/load)  
- `tests/` — Pytest unit tests  
- `requirements.txt` — Dependencies


---

## 🚀 Getting Started

### 1. ✅ Prerequisites

- Python **3.9+** must be installed on your system  
- `git` installed for cloning the repository

Check your Python version:

```bash
python --version
```

### 2. 📥 Clone the Repository
Use git to clone the project locally:
```
git clone https://github.com/LineIntegralx/Lab4_LynnAriss_TamaraFakih.git
```
Then navigate into the project directory:
```
cd Lab4_LynnAriss_TamaraFakih
```

### 3. 🧪 Create a Virtual Environment (Recommended)
It’s best practice to create a virtual environment to isolate project dependencies.

Windows (PowerShell):
```
python -m venv venv
.\venv\Scripts\Activate.ps1
```
macOS / Linux:

```
python3 -m venv venv
source venv/bin/activate
```

### 4. 📦 Install Dependencies
Install the required Python packages using pip:

```
pip install -r requirements.txt
```

If you encounter issues with PyQt5, you can install it manually:
```
pip install PyQt5
```
### 5. 🗃️ (Optional) Initialize the Database
The SQLite database is automatically created on first run.
If you want to start from scratch, simply delete the existing .db file (school.db), and rerun the database initialization script init_db.py again.

### 6. 🚀 Run the Application
Launch the application using the GUI chooser script:

```
python src/gui/choose_gui.py
```
You will be prompted to choose between:

- PyQt5 – Full-featured modern interface

- Tkinter – Lightweight fallback GUI

### 7. 🔍 Run Unit Tests (Optional)
You can verify that everything is working correctly by running the test suite:

```
pytest
```
### 📸 Example Features in Action
Once the application is running, you can:

➕ Add new students, instructors, and courses

🔄 Edit or delete existing records

📚 Register students into courses and manage enrollments

🔎 Search for records by name or ID

💾 Export and import data as JSON or CSV

📤 Backup and restore the entire database with one click

### 📜 Example CLI Commands
To run the app:

```
python src/gui/choose_gui.py
```

To run tests:
```
pytest
```
To export data as JSON:
```
python -m src.persistence.json_store
```
### 🛠️ Troubleshooting
❗ PyQt5 ImportError:
Make sure it’s installed:

```
pip install PyQt5
```
❗ tkinter not found:
tkinter is part of the Python standard library. If missing, install it using your OS package manager:

- Ubuntu/Debian: sudo apt install python3-tk

- macOS: Usually included with Python

- Windows: Included with official Python installer

### 📜 License
This project is created for educational and demonstration purposes.
You are free to modify, distribute, and adapt it for your own learning or projects.

### 🤝 Contributing
Contributions are welcome!
If you’d like to improve the project:

Fork the repository

Create a new feature branch

Commit your changes

Submit a pull request 🚀

### 👩‍💻 Author
Developed by Tamara Fakih and Lynn Ariss – a demonstration project for Python desktop app development with databases and GUI frameworks.

### ⭐ Acknowledgements
Built with Python

GUI powered by PyQt5 and Tkinter

Database layer with SQLite

Documentation generated with Sphinx

