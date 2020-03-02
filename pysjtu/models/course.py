from typing import List

from pysjtu.models.base import Result


class LibCourse(Result):
    """
    A model which describes a course in CourseLib. Some fields may be empty.

    :param name: literal name of the course.
    :type name: str
    :param day: in which day(s) of weeks classes are given.
    :type day: int
    :param week: in which week(s) classes are given.
    :type week: list
    :param time: at which time of days classes are given.
    :type time: range
    :param location: the place where classes are given.
    :type location: str
    :param locations: the places where classes are given.
    :type locations: List[str]
    :param faculty: the faculty which offers this course.
    :type faculty: str
    :param credit: credits that the course provides.
    :type credit: float
    :param teacher: the teacher who offers this course.
    :type teacher: List[str]
    :param course_id: course id.
    :type course_id: str
    :param class_name: class name (constant between years).
    :type class_name: str
    :param class_id: class id (variable between years).
    :type class_id: str
    :param class_composition: students from which faculties do the course consists of.
    :type class_composition: List[str]
    :param hour_total: credit hours of the course.
    :type hour_total: int
    :param hour_remark: detailed explanation of the credit hours.
    :type hour_remark: dict
    :param seats: number of seats available in this course.
    :type seats: int
    :param students_elected: number of students elected this course.
    :type students_elected: int
    :param students_planned: number of students planned when setting this course.
    :type students_planned: int
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
