
from enum import Enum


class Req(Enum):
    all = 0
    exist_field = 1
    field_value = 2
    field_collection = 3
    field_contain = 4
    '''
    name = 5
    birthday = 6
    id = 7
    department = 8
    group = 9
    student_id = 10
    course = 11
    groups = 12
    students = 13'''


class Person:
    @property
    def to_json(self) -> dict:
        result = dict()
        for key in self.__dict__:
            if key[0] != '_':
                result[key] = self.__dict__[key]
        return result

    def __init__(self, json_str: dict) -> None:  # гарантируем правильный json
        for key in json_str:
            setattr(self, key, json_str[key])

    def __eq__(self, __o: object) -> bool:
        return self.id == __o.id

    def __hash__(self) -> int:
        return hash(self.__dict__)


class Student(Person):

    def __str__(self) -> str:
        return f"Student {self.name} from group {self.group}, {self.department}"


class Teacher(Person):
    def __str__(self) -> str:
        return f"Teacher {self.name} on course {self.course}. Works with {len(self.groups)} groups and {len(self.students)} students."


class AssistantStudent(Student, Teacher):
    def __str__(self) -> str:
        return f"Student {self.name} from group {self.group}, {self.department}. Also teaches {self.course} in {len(self.groups)} groups and mentors {len(self.students)} students."
