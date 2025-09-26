import sys
import json
import csv
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QHeaderView,QInputDialog, QDialog
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.models import Student
from src.models import Instructor
from src.models import Course
from db.sqlite_repo import SQLiteRepository

PRIMARY_COLOR = "#840132"
TEXT_COLOR = "#ffffff"
BG_COLOR = "#f0f4f7"
ROUNDED_STYLE = """
    QWidget, QLineEdit, QPushButton, QComboBox {
        border-radius: 12px;
        font-size: 14px;
    }
    QPushButton {
        background-color: #840132;
        color: #fff;
        padding: 8px 16px;
        border: none;
    }
    QPushButton:hover {
        background-color: #a03a5a;
    }
    QLineEdit, QComboBox {
        background: #fff;
        padding: 6px;
        border: 1px solid #840132;
    }
    QTabWidget::pane {
        border: 2px solid #840132;
        border-radius: 12px;
    }
    QTabBar::tab {
        background: #840132;
        color: #fff;
        border-radius: 12px;
        padding: 8px 20px;
        margin: 2px;
    }
    QTabBar::tab:selected {
        background: #fff;
        color: #840132;
        border: 2px solid #840132;
    }
"""

class EditDialog(QDialog):
    """A dialog for editing records whether for students or instructors.
    :param title: The title of the dialog window
    :type title: str
    :param fields: List of fields to be edited
    :type fields: list[str]
    :param values: List of current values of the fields
    :type values: list[str]
    :param parent: The parent widget of the dialog by default it is set to None
    :type parent: QWidget, optional"""

    def __init__(self, title, fields, values, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.edits = {}
        layout = QVBoxLayout()
        for label, value in zip(fields, values):
            row = QHBoxLayout()
            lbl = QLabel(label)
            edit = QLineEdit()
            edit.setText(str(value))
            row.addWidget(lbl)
            row.addWidget(edit)
            layout.addLayout(row)
            self.edits[label] = edit
        btns = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)
        self.setLayout(layout)

    def get_values(self):
        """Get the edited valuues entered in the dialog.
        :returns: List of edited values in the same order as fields
        :rtype: list[str]"""
        return [self.edits[label].text().strip() for label in self.edits]

class SchoolManagementSystem(QMainWindow):
    """This is the main appication window for the School Management System.
    :ivar db: Database managrement instance used for CURD operations
    :vartype db:DatabaseManager
    """
    def __init__(self):
        """Initialize the main window and its components."""
        super().__init__()
        self.setWindowTitle("School Management System")
        self.setGeometry(100, 100, 1100, 700)
        self.setStyleSheet(ROUNDED_STYLE)
        self.db = SQLiteRepository()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface components."""
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()  
        save_btn = QPushButton("Save Data")
        load_btn = QPushButton("Load Data")
        export_btn = QPushButton("Export to CSV")
        backup_btn = QPushButton("Backup Database")
        restore_btn = QPushButton("Restore Database")
        save_btn.clicked.connect(self.save_data)
        load_btn.clicked.connect(self.load_data)
        export_btn.clicked.connect(self.export_csv)
        backup_btn.clicked.connect(self.backup_database)
        restore_btn.clicked.connect(self.restore_database)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(backup_btn)
        btn_layout.addWidget(restore_btn)

    
        main_layout = QVBoxLayout()
        main_layout.addLayout(btn_layout)  
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.student_tab = QWidget()
        self.instructor_tab = QWidget()
        self.course_tab = QWidget()
        self.registration_tab = QWidget()
        self.display_tab = QWidget()
        self.search_tab = QWidget()

        self.tabs.addTab(self.student_tab, "Students")
        self.tabs.addTab(self.instructor_tab, "Instructors")
        self.tabs.addTab(self.course_tab, "Courses")
        self.tabs.addTab(self.registration_tab, "Registration")
        self.tabs.addTab(self.display_tab, "Display All")
        self.tabs.addTab(self.search_tab, "Search")

        self.setup_student_tab()
        self.setup_instructor_tab()
        self.setup_course_tab()
        self.setup_registration_tab()
        self.setup_display_tab()
        self.setup_search_tab()
        self.update_course_and_registration()
        self.refresh_table()

    def setup_student_tab(self):
        """Set up the 'Studetns'tab UI with input fields and an Add buttons"""
        layout = QVBoxLayout()
        form = QVBoxLayout()

       
        form_widget = QWidget()
        form_widget.setLayout(form)
        form_widget.setFixedWidth(350) 

        
        name_label = QLabel("Name:")
        name_label.setAlignment(Qt.AlignLeft)
        self.student_name = QLineEdit()
        form.addWidget(name_label)
        form.addWidget(self.student_name)

        age_label = QLabel("Age:")
        age_label.setAlignment(Qt.AlignLeft)
        self.student_age = QLineEdit()
        form.addWidget(age_label)
        form.addWidget(self.student_age)

        email_label = QLabel("Email:")
        email_label.setAlignment(Qt.AlignLeft)
        self.student_email = QLineEdit()
        form.addWidget(email_label)
        form.addWidget(self.student_email)

        id_label = QLabel("Student ID:")
        id_label.setAlignment(Qt.AlignLeft)
        self.student_id = QLineEdit()
        form.addWidget(id_label)
        form.addWidget(self.student_id)

        add_btn = QPushButton("Add Student")
        add_btn.clicked.connect(self.add_student)
        form.addWidget(add_btn)

        outer_layout = QVBoxLayout()
        outer_layout.addStretch()
        h_center = QHBoxLayout()
        h_center.addStretch()
        h_center.addWidget(form_widget)
        h_center.addStretch()
        outer_layout.addLayout(h_center)
        outer_layout.addStretch()

        self.student_tab.setLayout(outer_layout)

    def setup_instructor_tab(self):
        """Set up the 'Instructors' tab UI with input fields and an Add button"""
        layout = QVBoxLayout()
        form = QVBoxLayout()

        form_widget = QWidget()
        form_widget.setLayout(form)
        form_widget.setFixedWidth(350)

        name_label = QLabel("Name:")
        name_label.setAlignment(Qt.AlignLeft)
        self.instructor_name = QLineEdit()
        form.addWidget(name_label)
        form.addWidget(self.instructor_name)

        age_label = QLabel("Age:")
        age_label.setAlignment(Qt.AlignLeft)
        self.instructor_age = QLineEdit()
        form.addWidget(age_label)
        form.addWidget(self.instructor_age)

        email_label = QLabel("Email:")
        email_label.setAlignment(Qt.AlignLeft)
        self.instructor_email = QLineEdit()
        form.addWidget(email_label)
        form.addWidget(self.instructor_email)

        id_label = QLabel("Instructor ID:")
        id_label.setAlignment(Qt.AlignLeft)
        self.instructor_id = QLineEdit()
        form.addWidget(id_label)
        form.addWidget(self.instructor_id)

        add_btn = QPushButton("Add Instructor")
        add_btn.clicked.connect(self.add_instructor)
        form.addWidget(add_btn)

        outer_layout = QVBoxLayout()
        outer_layout.addStretch()
        h_center = QHBoxLayout()
        h_center.addStretch()
        h_center.addWidget(form_widget)
        h_center.addStretch()
        outer_layout.addLayout(h_center)
        outer_layout.addStretch()

        self.instructor_tab.setLayout(outer_layout)

    def setup_course_tab(self):
        """Set up the 'Courses' tab UI with input fields and an Add button"""
        layout = QVBoxLayout()
        form = QVBoxLayout()

        form_widget = QWidget()
        form_widget.setLayout(form)
        form_widget.setFixedWidth(350)

        id_label = QLabel("Course ID:")
        id_label.setAlignment(Qt.AlignLeft)
        self.course_id = QLineEdit()
        form.addWidget(id_label)
        form.addWidget(self.course_id)

        name_label = QLabel("Course Name:")
        name_label.setAlignment(Qt.AlignLeft)
        self.course_name = QLineEdit()
        form.addWidget(name_label)
        form.addWidget(self.course_name)

        instructor_label = QLabel("Instructor:")
        instructor_label.setAlignment(Qt.AlignLeft)
        self.course_instructor = QComboBox()
        form.addWidget(instructor_label)
        form.addWidget(self.course_instructor)

        add_btn = QPushButton("Add Course")
        add_btn.clicked.connect(self.add_course)
        form.addWidget(add_btn)

        outer_layout = QVBoxLayout()
        outer_layout.addStretch()
        h_center = QHBoxLayout()
        h_center.addStretch()
        h_center.addWidget(form_widget)
        h_center.addStretch()
        outer_layout.addLayout(h_center)
        outer_layout.addStretch()

        self.course_tab.setLayout(outer_layout)

    def setup_registration_tab(self):
        """Set up the 'Registration' tab UI with the Student ID and Course selection fields."""
        layout = QVBoxLayout()
        form = QVBoxLayout()

        form_widget = QWidget()
        form_widget.setLayout(form)
        form_widget.setFixedWidth(350)

        student_id_label = QLabel("Student ID:")
        student_id_label.setAlignment(Qt.AlignLeft)
        self.reg_student_id = QLineEdit()
        form.addWidget(student_id_label)
        form.addWidget(self.reg_student_id)

        course_label = QLabel("Course:")
        course_label.setAlignment(Qt.AlignLeft)
        self.reg_course = QComboBox()
        form.addWidget(course_label)
        form.addWidget(self.reg_course)

        reg_btn = QPushButton("Register Student")
        reg_btn.clicked.connect(self.register_student)
        form.addWidget(reg_btn)

        outer_layout = QVBoxLayout()
        outer_layout.addStretch()
        h_center = QHBoxLayout()
        h_center.addStretch()
        h_center.addWidget(form_widget)
        h_center.addStretch()
        outer_layout.addLayout(h_center)
        outer_layout.addStretch()

        self.registration_tab.setLayout(outer_layout)

    def setup_display_tab(self):
        """Set up the 'Display All' tab UI with a table to show all records and Edit/Delete buttons."""
        layout = QVBoxLayout()
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Type", "Name", "ID Number", "Email", "Age"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        btns = QHBoxLayout()
        edit_btn = QPushButton("Edit Selected")
        delete_btn = QPushButton("Delete Selected")
        edit_btn.clicked.connect(self.edit_selected)
        delete_btn.clicked.connect(self.delete_selected)
        btns.addWidget(edit_btn)
        btns.addWidget(delete_btn)
        layout.addLayout(btns)
        self.display_tab.setLayout(layout)
        self.refresh_table()

    def setup_search_tab(self):
        """Set up the 'Search' tab UI with a search input and a table to show results."""
        layout = QVBoxLayout()
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_records)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        self.search_table = QTableWidget(0, 5)
        self.search_table.setHorizontalHeaderLabels(["Type", "Name", "ID Number", "Email", "Age"])
        self.search_input.setPlaceholderText("Type name or ID to search...")
        self.search_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.search_table)
        self.search_tab.setLayout(layout)

    
    def add_student(self):
        """Add a new student to the database
        :raises ValueError: If the input data is invalid
        :raises sqlite3.IntegrityError: If the student ID already exists in the database"""

        name = self.student_name.text().strip()
        age = self.student_age.text().strip()
        email = self.student_email.text().strip()
        student_id = self.student_id.text().strip()

        if not name or not age or not email or not student_id:
            QMessageBox.warning(self, "Invalid", "All fields are required.")
            return

        try:
            student = Student(name, int(age), email, student_id)
            self.db.add_student(student.student_id, student.name, student.age, student.email)
            QMessageBox.information(self, "Success", "Student added successfully!")
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
            return
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "Duplicate/Invalid", f"{e}")
            return

        self.refresh_table()
        self.update_course_and_registration()
        self.student_name.clear(); self.student_age.clear(); self.student_email.clear(); self.student_id.clear()


    def add_instructor(self):
        """Add a new instructor to the database
        :raises ValueError: If the input data is invalid
        :raises sqlite3.IntegrityError: If the instructor ID already exists in the database"""

        name = self.instructor_name.text().strip()
        age = self.instructor_age.text().strip()
        email = self.instructor_email.text().strip()
        instructor_id = self.instructor_id.text().strip()

        if not name or not age or not email or not instructor_id:
            QMessageBox.warning(self, "Invalid", "All fields are required.")
            return

        try:
            instructor = Instructor(name, int(age), email, instructor_id)
            self.db.add_instructor(instructor.instructor_id, instructor.name, instructor.age, instructor.email)
            QMessageBox.information(self, "Success", "Instructor added successfully!")
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
            return
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "Duplicate/Invalid", f"{e}")
            return

        self.refresh_table()
        self.update_course_and_registration()
        self.instructor_name.clear(); self.instructor_age.clear(); self.instructor_email.clear(); self.instructor_id.clear()


    def add_course(self):
        """Add a new course to the database
        :raises ValueError: If the input data is invalid
        :raises sqlite3.IntegrityError: If the course ID already exists in the database"""

        course_id = self.course_id.text().strip()
        course_name = self.course_name.text().strip()
        instructor_id = self.course_instructor.currentData() 

        if not course_id or not course_name or instructor_id is None:
            QMessageBox.warning(self, "Invalid", "Please enter valid course information.")
            return

        try:
            instructor_data = self.db.get_instructor(instructor_id)
            if not instructor_data:
                QMessageBox.warning(self, "Invalid", "Selected instructor not found.")
                return
                
            temp_instructor = Instructor(
                instructor_data['name'], 
                instructor_data['age'], 
                instructor_data['email'], 
                instructor_data['instructor_id']
            )
            course = Course(course_id, course_name, temp_instructor)
            self.db.add_course(course.course_id, course.course_name, instructor_id)
            QMessageBox.information(self, "Success", "Course added successfully!")
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
            return
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "Duplicate/Invalid", f"{e}")
            return

        self.refresh_table()
        self.update_course_and_registration()
        self.course_id.clear(); self.course_name.clear(); self.course_instructor.setCurrentIndex(-1)


    def register_student(self):
        """Register a student for a course
         :raises ValueError: If the input data is invalid"""
        
        student_id = self.reg_student_id.text().strip()
        course_id = self.reg_course.currentData()  

        if not student_id or not course_id:
            QMessageBox.warning(self, "Invalid", "Please select both student and course.")
            return

        student = self.db.get_student(student_id)
        course = self.db.get_course(course_id)
        
        if not student or not course:
            QMessageBox.warning(self, "Invalid", "Select a valid student and course.")
            return

        try:
            existing = self.db.get_registrations(s_id=student_id, c_id=course_id)
            if existing:
                QMessageBox.information(self, "Info", "Student is already registered in this course.")
                return
            self.db.register_student(student_id, course_id)
            QMessageBox.information(self, "Success", f"{student['name']} registered for {course['course_name']} successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration failed: {e}")

    def refresh_table(self):
        """Refresh the display table with the latest data from the database."""

        self.table.setRowCount(0)

   
        students = self.db.get_all_students()
        for s in students:
            self._add_table_row("Student", s["name"], s["student_id"], s["email"], s["age"])

        instructors = self.db.get_all_instructors()
        for i in instructors:
            self._add_table_row("Instructor", i["name"], i["instructor_id"], i["email"], i["age"])

        
        courses = self.db.get_all_courses()
        for c in courses:
            self._add_table_row("Course", c["course_name"], c["course_id"], "", "")


    def _add_table_row(self, typ, name, idnum, email, age):
        """Helper method to add a row to the display table.
        :param typ: The type of record (Student, Instructor, Course)
        :type typ: str
        :param name: The name of the person or course
        :type name: str
        :param idnum: The ID number of the person or course
        :type idnum: str
        :param email: The email of the person (empty for courses)
        :type email: str
        :param age: The age of the person (empty for courses)
        :type age: str or int"""

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(typ))
        self.table.setItem(row, 1, QTableWidgetItem(name))
        self.table.setItem(row, 2, QTableWidgetItem(idnum))
        self.table.setItem(row, 3, QTableWidgetItem(email))
        self.table.setItem(row, 4, QTableWidgetItem(str(age)))

    def update_course_and_registration(self):
        """Update the course and registration dropdowns with the latest data from the database."""
        self.course_instructor.clear()
        instructors = self.db.get_all_instructors()
        for instructor in instructors:
            self.course_instructor.addItem(f"{instructor['name']} ({instructor['instructor_id']})", instructor['instructor_id'])

    
        self.reg_course.clear()
        courses = self.db.get_all_courses()
        for course in courses:
            self.reg_course.addItem(f"{course['course_name']} ({course['course_id']})", course['course_id'])

    def edit_selected(self):
        """Edit the selected record in the display table."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select", "Select a record to edit.")
            return
        typ = self.table.item(row, 0).text()
        if typ == "Student":
            self._edit_student(row)
        elif typ == "Instructor":
            self._edit_instructor(row)
        else:
            QMessageBox.information(self, "Edit", "Editing courses is not supported.")

    def _edit_student(self, row):
        """Edit a student record given the table row index."""
        current_id = self.table.item(row, 2).text()
        student = self.db.get_student(current_id)
        if not student:
            QMessageBox.warning(self, "Not found", "Student not found in DB.")
            return

        dlg = EditDialog("Edit Student", ["Name", "Age", "Email", "Student ID"],
                        [student["name"], student["age"], student["email"], student["student_id"]], self)
        if dlg.exec_():
            name, age, email, new_id = dlg.get_values()
            if not name or not age or not email or not new_id:
                QMessageBox.warning(self, "Invalid", "All fields are required.")
                return
            try:
                if new_id != current_id:
                    QMessageBox.information(self, "Note", "Changing Student ID is not supported; updating other fields only.")
                test_student = Student(name, int(age), email, current_id)
                self.db.update_student(current_id, name=name, age=int(age), email=email)
                self.refresh_table()
            except ValueError as e:
                QMessageBox.warning(self, "Validation Error", str(e))
                return
            except sqlite3.IntegrityError as e:
                QMessageBox.warning(self, "Duplicate/Invalid", f"{e}")
                return


    def _edit_instructor(self, row):
        """Edit an instructor record given the table row index."""
        current_id = self.table.item(row, 2).text()
        instructor = self.db.get_instructor(current_id)
        if not instructor:
            QMessageBox.warning(self, "Not found", "Instructor not found in DB.")
            return

        dlg = EditDialog("Edit Instructor", ["Name", "Age", "Email", "Instructor ID"],
                        [instructor["name"], instructor["age"], instructor["email"], instructor["instructor_id"]], self)
        if dlg.exec_():
            name, age, email, new_id = dlg.get_values()
            if not name or not age or not email or not new_id:
                QMessageBox.warning(self, "Invalid", "All fields are required.")
                return

            try:
                if new_id != current_id:
                    QMessageBox.information(self, "Note", "Changing Instructor ID is not supported; updating other fields only.")
                test_instructor = Instructor(name, int(age), email, current_id)
                self.db.update_instructor(current_id, name=name, age=int(age), email=email)
                self.refresh_table()
                self.update_course_and_registration()
            except ValueError as e:
                QMessageBox.warning(self, "Validation Error", str(e))
                return
            except sqlite3.IntegrityError as e:
                QMessageBox.warning(self, "Duplicate/Invalid", f"{e}")
                return

    def delete_selected(self):
        """Delete the selected record from the display table and database."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select", "Select a record to delete.")
            return

        typ = self.table.item(row, 0).text()
        idnum = self.table.item(row, 2).text()

        try:
            if typ == "Student":
                self.db.delete_student(idnum)
            elif typ == "Course":
                self.db.delete_course(idnum)
            elif typ == "Instructor":
                courses = self.db.get_all_courses()
                instructor_courses = [c for c in courses if c.get('i_id') == idnum]
                if instructor_courses:
                    resp = QMessageBox.question(
                        self, "Also delete courses?",
                        f"Instructor teaches {len(instructor_courses)} course(s). Delete them (and their registrations) too?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if resp == QMessageBox.Yes:
                        self.db.delete_instructor(idnum)
                    else:
                        return
                else:
                    self.db.delete_instructor(idnum)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Delete failed: {e}")
            return

        self.refresh_table()
        self.update_course_and_registration()


    def search_records(self):
        """Search records by name or ID and display results in the search table."""
        query = self.search_input.text().strip()
        if not query:
            return
            
        self.search_table.setRowCount(0)
        # Aggregate simple fuzzy searches across tables
        results = []
        for row in self.db.search('STUDENTS', name=query) + self.db.search('STUDENTS', student_id=query):
            results.append({'type': 'Student', 'name': row['name'], 'id_number': row['student_id'], 'email': row['email'], 'age': row['age']})
        for row in self.db.search('INSTRUCTORS', name=query) + self.db.search('INSTRUCTORS', instructor_id=query):
            results.append({'type': 'Instructor', 'name': row['name'], 'id_number': row['instructor_id'], 'email': row['email'], 'age': row['age']})
        for row in self.db.search('COURSES', course_name=query) + self.db.search('COURSES', course_id=query):
            results.append({'type': 'Course', 'name': row['course_name'], 'id_number': row['course_id'], 'email': '', 'age': ''})

        for result in results:
            self._add_search_row(result['type'], result['name'], result['id_number'], result.get('email', ''), result.get('age', ''))

    def _add_search_row(self, typ, name, idnum, email, age):
        """Helper method to add a row to the search results table."""
        row = self.search_table.rowCount()
        self.search_table.insertRow(row)
        self.search_table.setItem(row, 0, QTableWidgetItem(typ))
        self.search_table.setItem(row, 1, QTableWidgetItem(name))
        self.search_table.setItem(row, 2, QTableWidgetItem(idnum))
        self.search_table.setItem(row, 3, QTableWidgetItem(email))
        self.search_table.setItem(row, 4, QTableWidgetItem(str(age)))

    def save_data(self):
        """Export all data to a JSON file."""
        try:
            filename = self.db.export_to_json()
            QMessageBox.information(self, "Save", f"Data exported to {filename}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {e}")

    def load_data(self):
        """Load data from a JSON file into the database."""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Select JSON file to load",
                "", "JSON files (*.json);;All files (*.*)"
            )
            if filename:
                success = self.db.import_from_json(filename)
                if success:
                    self.refresh_table()
                    self.update_course_and_registration()
                    QMessageBox.information(self, "Load", "Data loaded successfully.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to load data from file.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")

    def export_csv(self):
        """Export all data to a CSV file."""
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline='') as f:
                w = csv.writer(f)
                w.writerow(["Type", "Name", "ID Number", "Email", "Age"])
                
                students = self.db.get_all_students()
                for s in students:
                    w.writerow(["Student", s["name"], s["student_id"], s["email"], s["age"]])
                
                instructors = self.db.get_all_instructors()
                for i in instructors:
                    w.writerow(["Instructor", i["name"], i["instructor_id"], i["email"], i["age"]])
                
                courses = self.db.get_all_courses()
                for c in courses:
                    w.writerow(["Course", c["course_name"], c["course_id"], "", ""])
                    
            QMessageBox.information(self, "Export", "Data exported to CSV.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")

    def validate_email(self, email):
        """Validate email format using a simple regex.
        :param email: The email address to validate
        :type email: str
        :returns: True if email is valid, False otherwise
        :rtype: bool"""
        import re
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None
    
    def backup_database(self):
        """Create a backup of the current database."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Backup Database", "", "Database Files (*.sqlite *.db)"
            )
            if filename:
                backup_path = self.db.backup(filename)
                QMessageBox.information(self, "Backup", f"Database backed up to {backup_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Backup failed: {e}")
    
    def restore_database(self):
        """Restore the database from a backup file."""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Restore Database", "", "Database Files (*.sqlite *.db)"
            )
            if filename:
                reply = QMessageBox.question(
                    self, "Restore Database", 
                    "This will replace the current database. Are you sure?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    from pathlib import Path
                    import shutil
                    self.db.close()
                    dest = Path(self.db.db_path).resolve()
                    shutil.copy2(filename, dest)
                    self.db = SQLiteRepository(dest)
                    self.refresh_table()
                    self.update_course_and_registration()
                    QMessageBox.information(self, "Restore", "Database restored successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Restore failed: {e}")

    def _get_text(self, title, label, default):
        """Helper method to get text input from the user.
        :param title: The title of the input dialog
        :type title: str
        :param label: The label for the input field
        :type label: str
        :param default: The default text to display in the input field
        :type default: str
        :returns: The text entered by the user and a boolean indicating if OK was pressed
        :rtype: tuple[str, bool]"""
        text, ok = QInputDialog.getText(self, title, label, text=default)
        return text, ok


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SchoolManagementSystem()
    window.show()
    sys.exit(app.exec_())