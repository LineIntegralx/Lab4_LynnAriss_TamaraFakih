import sqlite3
import json
import shutil
from datetime import datetime
import os

class DatabaseManager:
    """Manages the SQLite database for the school management system
    :param db_path: Path to the SQLite database file
    :type db_path: str"""
    def __init__(self, db_path="school_management.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with self._connect() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    student_id TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS instructors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    instructor_id TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id TEXT NOT NULL UNIQUE,
                    course_name TEXT NOT NULL,
                    instructor_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(instructor_id) REFERENCES instructors(instructor_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(student_id) REFERENCES students(student_id),
                    FOREIGN KEY(course_id) REFERENCES courses(course_id),
                    UNIQUE(student_id, course_id)
                )
            """)
            
            conn.commit()
    
    def _connect(self):
        """Create database connection with proper settings"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    
    def create_student(self, name, age, email, student_id):
        """Create a new student record
        :param name: Student's name
        :type name: str
        :param age: Student's age
        :type age: int
        :param email: Student's email
        :type email: str
        :param student_id: Unique student identifier
        :type student_id: str
        :return: ID of the newly created student
        :rtype: int
        :raises sqlite3.IntegrityError: If email or student_id already exists"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO students (name, age, email, student_id)
                VALUES (?, ?, ?, ?)
            """, (name, int(age), email, student_id))
            conn.commit()
            return cursor.lastrowid
    
    def get_student(self, student_id):
        """Get a student by student_id"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_students(self):
        """Get all students"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_student(self, old_student_id, name, age, email, new_student_id):
        """Update a student record"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE students 
                SET name = ?, age = ?, email = ?, student_id = ?
                WHERE student_id = ?
            """, (name, int(age), email, new_student_id, old_student_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_student(self, student_id):
        """Delete a student and all their registrations"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM registrations WHERE student_id = ?", (student_id,))
            cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            conn.commit()
            return cursor.rowcount > 0
    
   
    def create_instructor(self, name, age, email, instructor_id):
        """Create a new instructor record
        :param name: Instructor's name
        :type name: str
        :param age: Instructor's age
        :type age: int
        :param email: Instructor's email
        :type email: str
        :param instructor_id: Unique instructor identifier
        :type instructor_id: str
        :return: ID of the newly created instructor
        :rtype: int
        :raises sqlite3.IntegrityError: If email or instructor_id already exists"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO instructors (name, age, email, instructor_id)
                VALUES (?, ?, ?, ?)
            """, (name, int(age), email, instructor_id))
            conn.commit()
            return cursor.lastrowid
    
    def get_instructor(self, instructor_id):
        """Get an instructor by instructor_id"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM instructors WHERE instructor_id = ?", (instructor_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_instructors(self):
        """Get all instructors"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM instructors ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_instructor(self, old_instructor_id, name, age, email, new_instructor_id):
        """Update an instructor record"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE instructors 
                SET name = ?, age = ?, email = ?, instructor_id = ?
                WHERE instructor_id = ?
            """, (name, int(age), email, new_instructor_id, old_instructor_id))
            
            cursor.execute("""
                UPDATE courses 
                SET instructor_id = ? 
                WHERE instructor_id = ?
            """, (new_instructor_id, old_instructor_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_instructor(self, instructor_id):
        """Delete an instructor and optionally their courses"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM courses WHERE instructor_id = ?", (instructor_id,))
            course_count = cursor.fetchone()[0]
            
            if course_count > 0:
                cursor.execute("""
                    DELETE FROM registrations 
                    WHERE course_id IN (
                        SELECT course_id FROM courses WHERE instructor_id = ?
                    )
                """, (instructor_id,))
                
                cursor.execute("DELETE FROM courses WHERE instructor_id = ?", (instructor_id,))
            
            cursor.execute("DELETE FROM instructors WHERE instructor_id = ?", (instructor_id,))
            conn.commit()
            return cursor.rowcount > 0
     
    def create_course(self, course_id, course_name, instructor_id):
        """Create a new course record
        :param course_id: Unique course identifier
        :type course_id: str
        :param course_name: Name of the course
        :type course_name: str
        :param instructor_id: Instructor's unique identifier
        :type instructor_id: str
        :return: ID of the newly created course
        :rtype: int
        :raises sqlite3.IntegrityError: If course_id already exists or instructor_id does not exist"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO courses (course_id, course_name, instructor_id)
                VALUES (?, ?, ?)
            """, (course_id, course_name, instructor_id))
            conn.commit()
            return cursor.lastrowid
    
    def get_course(self, course_id):
        """Get a course by course_id"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_courses(self):
        """Get all courses with instructor names"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, i.name as instructor_name
                FROM courses c
                LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
                ORDER BY c.course_name
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_course(self, old_course_id, course_id, course_name, instructor_id):
        """Update a course record"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE courses 
                SET course_id = ?, course_name = ?, instructor_id = ?
                WHERE course_id = ?
            """, (course_id, course_name, instructor_id, old_course_id))
            
            cursor.execute("""
                UPDATE registrations 
                SET course_id = ? 
                WHERE course_id = ?
            """, (course_id, old_course_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_course(self, course_id):
        """Delete a course and all its registrations"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM registrations WHERE course_id = ?", (course_id,))
            cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def register_student(self, student_id, course_id):
        """Register a student for a course"""
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO registrations (student_id, course_id)
                    VALUES (?, ?)
                """, (student_id, course_id))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False 
    
    def unregister_student(self, student_id, course_id):
        """Unregister a student from a course"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM registrations 
                WHERE student_id = ? AND course_id = ?
            """, (student_id, course_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_student_courses(self, student_id):
        """Get all courses a student is registered for"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, i.name as instructor_name
                FROM courses c
                JOIN registrations r ON c.course_id = r.course_id
                LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
                WHERE r.student_id = ?
                ORDER BY c.course_name
            """, (student_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_course_students(self, course_id):
        """Get all students registered for a course"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*
                FROM students s
                JOIN registrations r ON s.student_id = r.student_id
                WHERE r.course_id = ?
                ORDER BY s.name
            """, (course_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def search_records(self, query):
        """Search across all records"""
        results = []
        search_term = f"%{query.lower()}%"
        
        with self._connect() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 'Student' as type, name, student_id as id_number, email, age
                FROM students
                WHERE LOWER(name) LIKE ? OR LOWER(student_id) LIKE ? OR LOWER(email) LIKE ?
            """, (search_term, search_term, search_term))
            results.extend([dict(row) for row in cursor.fetchall()])
            
            cursor.execute("""
                SELECT 'Instructor' as type, name, instructor_id as id_number, email, age
                FROM instructors
                WHERE LOWER(name) LIKE ? OR LOWER(instructor_id) LIKE ? OR LOWER(email) LIKE ?
            """, (search_term, search_term, search_term))
            results.extend([dict(row) for row in cursor.fetchall()])
            
            cursor.execute("""
                SELECT 'Course' as type, course_name as name, course_id as id_number, '' as email, '' as age
                FROM courses
                WHERE LOWER(course_name) LIKE ? OR LOWER(course_id) LIKE ?
            """, (search_term, search_term))
            results.extend([dict(row) for row in cursor.fetchall()])
        
        return results
    
    def export_to_json(self, filename="school_data.json"):
        """Export all data to JSON file"""
        data = {
            "students": self.get_all_students(),
            "instructors": self.get_all_instructors(),
            "courses": self.get_all_courses(),
            "registrations": self._get_all_registrations()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4, default=str)
        return filename
    
    def import_from_json(self, filename="school_data.json"):
        """Import data from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
        
            for student in data.get("students", []):
                try:
                    self.create_student(
                        student["name"], 
                        student["age"], 
                        student["email"], 
                        student["student_id"]
                    )
                except sqlite3.IntegrityError:
                    pass  
            
            for instructor in data.get("instructors", []):
                try:
                    self.create_instructor(
                        instructor["name"], 
                        instructor["age"], 
                        instructor["email"], 
                        instructor["instructor_id"]
                    )
                except sqlite3.IntegrityError:
                    pass 
            
            for course in data.get("courses", []):
                try:
                    self.create_course(
                        course["course_id"], 
                        course["course_name"], 
                        course.get("instructor_id")
                    )
                except sqlite3.IntegrityError:
                    pass 
            
            for registration in data.get("registrations", []):
                try:
                    self.register_student(
                        registration["student_id"], 
                        registration["course_id"]
                    )
                except sqlite3.IntegrityError:
                    pass  
            
            return True
        except Exception as e:
            print(f"Import error: {e}")
            return False
    
    def _get_all_registrations(self):
        """Get all registrations"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT student_id, course_id FROM registrations")
            return [dict(row) for row in cursor.fetchall()]
    
    def backup_database(self, backup_path=None):
        """Create a backup of the database"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"school_management_backup_{timestamp}.db"
        
        try:
            shutil.copy2(self.db_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Backup error: {e}")
            return None
    
    def restore_database(self, backup_path):
        """Restore database from backup"""
        try:
            shutil.copy2(backup_path, self.db_path)
            return True
        except Exception as e:
            print(f"Restore error: {e}")
            return False
    
    def get_statistics(self):
        """Get database statistics"""
        with self._connect() as conn:
            cursor = conn.cursor()
            
            stats = {}
        
            cursor.execute("SELECT COUNT(*) FROM students")
            stats['students'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM instructors")
            stats['instructors'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM courses")
            stats['courses'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM registrations")
            stats['registrations'] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT AVG(student_count) FROM (
                    SELECT COUNT(*) as student_count 
                    FROM registrations 
                    GROUP BY course_id
                )
            """)
            result = cursor.fetchone()[0]
            stats['avg_students_per_course'] = round(result, 2) if result else 0
            
            return stats
