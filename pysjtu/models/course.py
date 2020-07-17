from dataclasses import dataclass
from typing import List, Optional

from pysjtu.models.base import Result


@dataclass
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
    day: Optional[int] = None
    week: Optional[list] = None
    time: Optional[range] = None
    location: Optional[str] = None
    locations: Optional[List[str]] = None
    faculty: Optional[str] = None
    credit: Optional[float] = None
    teacher: Optional[List[str]] = None
    course_id: Optional[str] = None
    class_name: Optional[str] = None
    class_id: Optional[str] = None
    class_composition: Optional[List[str]] = None
    hour_total: Optional[int] = None
    hour_remark: Optional[dict] = None
    seats: Optional[int] = None
    students_elected: Optional[int] = None
    students_planned: Optional[int] = None

    def __repr__(self):
        return f"<LibCourse {self.name} class_name={self.class_name}>"
