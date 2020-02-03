from typing import List

from pysjtu.model.base import Result


class LibCourse(Result):
    """
    A model which describes a course in CourseLib. Some fields may be empty.

    :param name: literal name of the course.
    :param day: in which day(s) of weeks classes are given.
    :param week: in which week(s) classes are given.
    :param time: at which time of days classes are given.
    :param location: the place where classes are given.
    :param locations: the places where classes are given.
    :param faculty: the faculty which offers this course.
    :param credit: credits that the course provides.
    :param teacher: the teacher who offers this course.
    :param course_id: course id.
    :param class_name: class name (constant between years).
    :param class_id: class id (variable between years).
    :param class_composition: students from which faculties do the course consists of.
    :param hour_total: credit hours of the course.
    :param hour_remark: detailed explanation of the credit hours.
    :param seats: number of seats available in this course.
    :param students_elected: number of students elected this course.
    :param students_planned: number of students planned when setting this course.
    """
    name: str
    day: int
    week: list
    time: range
    location: str
    locations: List[str]
    faculty: str
    credit: float
    teacher: List[str]
    course_id: str
    class_name: str
    class_id: str
    class_composition: List[str]
    hour_total: int
    hour_remark: dict
    seats: int
    students_elected: int
    students_planned: int

    _members = ["name", "day", "week", "time", "location", "locations", "faculty", "credit", "teacher",
                "course_id", "class_name", "class_id", "class_composition", "hour_total",
                "hour_remark", "seats", "students_elected", "students_planned"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<LibCourse {self.name} class_name={self.class_name}>"
