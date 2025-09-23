import json
import re

class person:
    """
    Base class for a person in the School Management System.
    
    :param name: Person's name
    :type name: str
    :param age: Person's age
    :type age: int
    :param _email: Person's email
    :type _email: str
    :raises ValueError: If the email format is invalid or age is negative  
    
    """

    def __init__(self, name, age, _email):
        self.name = name
        if not self.validate_email(_email):
            raise ValueError("Invalid email format.")
        if not self.validate_age(age):
            raise ValueError("Age must be a non-negative integer.")
        self.age = int(age)
        self._email = _email

    def introduce(self):
        """ Introduce the person by printing their details. """
        print(f"Hi my name is {self.name}, I am {self.age} years old and my email is {self._email}.")

    def to_dict(self):
        """ Convert the person object to a dictionary. 
        
         :return: Dictionary representation of the person with the name, age and email.
         :rtype: dict"""
        return {
            "name": self.name,
            "age": self.age,
            "_email": self._email
        }

    @classmethod
    def from_dict(cls, data):
        """ Create a person object from a dictionary.
        :param data: Dictionary containing person details (name, age and email)
        :type data: dict
        :return: Person object
        :rtype: person

        """
        return cls(data["name"], data["age"], data["_email"])

    def save_to_file(self, filename):
        """ Save the person object to a JSON file.

        :param filename: Name of the file to save the person object
        :type filename: str
        """
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filename):
        """ Load a person object from a JSON file.
        
        :param filename: Name of the file to load the person object from
        :type filename: str
        :return: Person object
        :rtype: person"""

        with open(filename, "r") as f:
            data = json.load(f)
            return cls.from_dict(data)
        
    @staticmethod
    def validate_email(email):
        """ Validate the email format.

        :param email: Email address to validate
        :type email: str
        :return: True if the email format is valid, False otherwise
        :rtype: bool
        """
        
        return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

    @staticmethod
    def validate_age(age):
        """ Validate that the age is a non-negative integer.
        :param age: Age to validate
        :type age: int
        :return: True if the age is a non-negative integer, False otherwise
        :rtype: bool
    """
        try:
            return int(age) >= 0
        except (ValueError, TypeError):
            return False