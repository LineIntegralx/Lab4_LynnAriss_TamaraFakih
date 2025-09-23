import json
from person import person

class Student(person):
    '''A class to represent a student, inheriting from the person class.
    
    :param name: The name of the student.
    :type name: str
    :param age: The age of the student.
    :type age: int
    :param _email: The email of the student.
    :type _email: str
    :param student_id: The unique 9-digit identifier for the student.
    :type student_id: str
    :raises ValueError: If the student_id is not 9 characters long or not alphanumeric.'''
    def __init__(self, name, age, _email, student_id):
        super().__init__(name, age, _email)
        if len(student_id) != 9 or not student_id.isalnum():
            raise ValueError("Student ID should be fully numeric and of length 9.")
        self.student_id = student_id
        self.registered_courses = []

    def register_course(self, course):
        '''Register a student in a course.
         :param course: The course to register the student in.
         :type course: Course
         '''
        self.registered_courses.append(course)
        print(f"You succesfully registered '{course}'")

    def to_dict(self):
        '''Convert the Student object to a dictionary for serialization.
         :return: A dictionary representation of the Student object.
         :rtype: dict
         '''
        data = super().to_dict()
        data.update({
            "student_id": self.student_id,
            "registered_courses": [c.course_id for c in self.registered_courses]
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        '''Create a Student object from a dictionary.
        :param data: A dictionary containing student data.
        :type data: dict
        :return: A Student object.
        :rtype: Student
        '''
        student = cls(data["name"], data["age"], data["_email"], data["student_id"])
        student.registered_courses = data.get("registered_courses", [])
        return student

    def save_to_file(self, filename):
        '''Save the Student object to a JSON file.
         :param filename: The name of the file to save the student data to.
         :type filename: str
         '''
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filename):
        '''Load a Student object from a JSON file.
        :param filename: The name of the file to load the student data from.
        :type filename: str
        :return: A Student object.
        :rtype: Student
        '''
        with open(filename, "r") as f:
            data = json.load(f)
            return cls.from_dict(data)