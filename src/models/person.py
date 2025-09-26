"""
:module: models.person
:synopsis: Base Person entity with simple validation and a mutable email property.

This module defines the ``Person`` class used as a base for other domain models.
It validates/normalizes name, age, and email, exposes a property for email, and
provides a tiny helper to serialize common fields.

Notes
-----
- Validation/normalization helpers live in ``src.validation.validators``.
- Kept intentionally small for the lab. No fancy ORM stuff here.
"""

from __future__ import annotations
from src.validation.validators import (
    is_valid_person_name, is_non_negative_int, is_valid_email,
    norm_email, norm_name
)


class Person:
    """
    Simple person record with name, age, and email (normalized).

    Parameters
    ----------
    name : str
        Person's name (validated, then normalized).
    age : int
        Non-negative integer age.
    email : str
        Email address (validated, then normalized).

    Attributes
    ----------
    name : str
        Normalized person name.
    age : int
        Integer age (stored as int explicitly).
    _email : str
        Backing field for the public ``email`` property.

    Notes
    -----
    - ``__slots__`` used to save memory and avoid accidental attributes.
    - Email is exposed via a property so we can re-validate on update.
    """
    __slots__ = ("name", "age", "_email")

    def __init__(self, name: str, age: int, email: str) -> None:
        """Constructor method

        Parameters
        ----------
        name : str
            Proposed name; must pass ``is_valid_person_name``.
        age : int
            Proposed age; must pass ``is_non_negative_int``.
        email : str
            Proposed email; must pass ``is_valid_email``.

        Raises
        ------
        ValueError
            If any of the inputs fail validation.

        Notes
        -----
        - We normalize strings so we don't store messy variants (spacing/case).
        - Age is cast to int just in case a numeric-like value sneaks in.
        """
        # quick guard checks so objects are always valid upon construction
        if not is_valid_person_name(name): raise ValueError("Invalid name.")
        if not is_non_negative_int(age):   raise ValueError("Age must be ≥ 0.")
        if not is_valid_email(email):       raise ValueError("Invalid email.")
        # normalize and store
        self.name = norm_name(name)
        self.age = int(age)
        self._email = norm_email(email)

    @property
    def email(self) -> str:
        """Email getter.

        Returns
        -------
        str
            The (normalized) email string.
        """
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Email setter with validation + normalization.

        Parameters
        ----------
        value : str
            New email to set.

        Raises
        ------
        ValueError
            If the provided email is invalid.

        Notes
        -----
        - Keeping validation here ensures updates stay consistent with __init__.
        """
        if not is_valid_email(value): raise ValueError("Invalid email.")
        self._email = norm_email(value)

    def introduce(self) -> str:
        """Return and print a small intro string (lab-style helper).

        Returns
        -------
        str
            A message of the form:
            ``"Hi, I'm <name>. I am <age> years old. Please find attached my email address if you wish to contact me: <email>"``

        Notes
        -----
        - Also prints to stdout because it's handy for quick manual checks.
        """
        # tiny helper mostly for demo/debug output
        msg = f"Hi, I'm {self.name}. I am {self.age} years old. Please find attached my email address if you wish to contact me: {self._email}"
        print(msg)
        return msg

    def _person_dict(self) -> dict:
        """Serialize common person fields to a dict.

        Returns
        -------
        dict
            Dictionary with keys ``name``, ``age``, and ``email``.

        Notes
        -----
        - Private helper because higher-level models usually extend this.
        """
        # keep it minimal; higher-level classes extend this with their own fields
        return {"name": self.name, "age": self.age, "email": self.email}
