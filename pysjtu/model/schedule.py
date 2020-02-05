from typing import List

from pysjtu.model.base import Result, Results


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
    day: int
    week: list
    time: range
    location: str
    credit: int
    assessment: str
    remark: str
    teacher_name: List[str]
    teacher_title: List[str]
    course_id: str
    class_name: str
    class_id: str
    hour_total: int
    hour_remark: dict
    hour_week: int
    field: str

    _members = ["name", "day", "week", "time", "location", "credit", "assessment", "remark", "teacher_name",
                "teacher_title", "course_id", "class_name", "class_id", "hour_total", "hour_remark", "hour_week",
                "field"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<ScheduleCourse {self.name} week={self.week} day={self.day} time={self.time}>"


from pysjtu.schema.schedule import ScheduleCourseSchema


class Schedule(Results[ScheduleCourse]):
    """
    A list-like interface to Schedule collections.
    An additional filter method has been added to make filter operations easier.
    """
    _schema = ScheduleCourseSchema
    _result_model = ScheduleCourse
