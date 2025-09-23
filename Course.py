import json

class Course:
    """Class representing a course in the school management system.
    :param course_id: Unique identifier for the course.
    :type course_id: int
    :param course_name: Name of the course.
    :type course_name: str
    :param instructor: Instructor teaching the course.
    :type instructor: Instructor
    :param enrolled_students: List of students enrolled in the course."""

    def __init__(self, course_id, course_name, instructor):
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor
        self.enrolled_students = []

    def add_student(self, student):
        """Add a student to the course.
        :param student: Student to be added.
        :type student: Student"""

        self.enrolled_students.append(student)
        print(f"Student {student.name} has been added to the course: {self.course_name}.")
    
    def to_dict(self):
        """Convert the course object to a dictionary for serialization.
         :return: Dictionary representation of the course.
         :rtype: dict"""
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "instructor": self.instructor.instructor_id if self.instructor else None,
            "enrolled_students": [s.student_id for s in self.enrolled_students]
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Course object from a dictionary.
        :param data: Dictionary containing course data.
        :type data: dict
        :return: Course object.
        :rtype: Course"""
        course = cls(data["course_id"], data["course_name"], None)
        course.enrolled_students = data.get("enrolled_students", [])
        return course

    def save_to_file(self, filename):
        """Save the course object to a JSON file.
        :param filename: Name of the file to save the course data.
        :type filename: str"""
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filename):
        """Load a course object from a JSON file.
        
        :param filename: Name of the file to load the course data from.
        :type filename: str
        :return: Course object.
        :rtype: Course"""
        with open(filename, "r") as f:
            data = json.load(f)
            return cls.from_dict(data)