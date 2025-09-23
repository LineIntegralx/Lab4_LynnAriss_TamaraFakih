import json
from person import person

class Instructor(person):
    """Represents an instructor 
    
    :param name: Instructor's name
    :param age: Instructor's age
    :param _email: Instructor's email
    :param instructor_id: Unique 9 digit identifier for the instructor
    :type instructor_id: str
    :raises ValueError: If instructor_id is not 9 characters long or not alphanumeric
    """
    def __init__(self, name, age, _email, instructor_id):
        super().__init__(name, age, _email)
        if len(instructor_id) != 9 or not instructor_id.isalnum():
            raise ValueError("instructor ID should be fully numeric and of length 9.")
        self.instructor_id = instructor_id
        self.assigned_courses = []

    def assign_course(self, course):
        """Assigns a course to the instructor

         :param course: Course to be assigned
         :type course: Course
        """
        self.assigned_courses.append(course)
        print(f"Course {course.course_name} has been succesfully assigned to instructor {self.name}.")

    def to_dict(self):
        """Convert the Instructor object to a dictionary for serialization
        
        :return: Dictionary representation of the Instructor object
        :rtype: dict
        """
        data = super().to_dict()
        data.update({
            "instructor_id": self.instructor_id,
            "assigned_courses": [c.course_id for c in self.assigned_courses]
        })
        return data

    @classmethod
    def from_dict(cls, data):
        """Create an Instructor object from a dictionary
        
        :param data: Dictionary containing instructor data
        :type data: dict
        :return: Instructor object
        :rtype: Instructor
        """
        instructor = cls(data["name"], data["age"], data["_email"], data["instructor_id"])
        instructor.assigned_courses = data.get("assigned_courses", [])
        return instructor

    def save_to_file(self, filename):
        """Save the Instructor object to a JSON file

         :param filename: Name of the file to save the data
         :type filename: str
        """
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filename):
        """Load an Instructor object from a JSON file
        
         :param filename: Name of the file to load the data from
         :type filename: str
         :return: Instructor object
         :rtype: Instructor
        """
        with open(filename, "r") as f:
            data = json.load(f)

            return cls.from_dict(data)           