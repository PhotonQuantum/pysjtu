from dataclasses import dataclass
from typing import List, Optional

from pysjtu.models.base import Result, Results


@dataclass
class ScheduleCourse(Result):
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
    :param credit: credits that the course provides.
    :type credit: int
    :param assessment: assessment method of this course. (exams, assesses, etc)
    :type assessment: str
    :param remark: remarks of this course.
    :type remark: str
    :param teacher_name: the teacher who offers this course.
    :type teacher_name: List[str]
    :param teacher_title: title of the course's teacher.
    :type teacher_title: List[str]
    :param course_id: course id.
    :type course_id: str
    :param class_name: class name (constant between years).
    :type class_name: str
    :param class_id: class id (variable between years).
    :type class_id: str
    :param hour_total: credit hours of the course.
    :type hour_total: int
    :param hour_remark: detailed explanation of the credit hours.
    :type hour_remark: dict
    :param hour_week: credit hours of the course every week.
    :type hour_week: int
    :param field: professional field of this course.
    :type field: str
    """
    name: str
    course_id: str
    class_name: str
    class_id: str
    day: Optional[int] = None
    week: Optional[list] = None
    time: Optional[range] = None
    location: Optional[str] = None
    credit: Optional[int] = None
    assessment: Optional[str] = None
    remark: Optional[str] = None
    teacher_name: Optional[List[str]] = None
    teacher_title: Optional[List[str]] = None
    hour_total: Optional[int] = None
    hour_remark: Optional[dict] = None
    hour_week: Optional[int] = None
    field: Optional[str] = None

    def __repr__(self):
        return f"<ScheduleCourse {self.name} week={self.week} day={self.day} time={self.time}>"


from pysjtu.schemas.schedule import ScheduleCourseSchema


class Schedule(Results[ScheduleCourse]):
    """
    A list-like interface to Schedule collections.
    An additional filter method has been added to make filter operations easier.
    """
    _schema = ScheduleCourseSchema
    _result_model = ScheduleCourse
