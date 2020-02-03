from typing import List

from pysjtu.model.base import Result, Results


class ScheduleCourse(Result):
    """
    A model which describes a course in CourseLib. Some fields may be empty.

    :param name: literal name of the course.
    :param day: in which day(s) of weeks classes are given.
    :param week: in which week(s) classes are given.
    :param time: at which time of days classes are given.
    :param location: the place where classes are given.
    :param credit: credits that the course provides.
    :param assessment: assessment method of this course. (exams, assesses, etc)
    :param remark: remarks of this course.
    :param teacher_name: the teacher who offers this course.
    :param teacher_title: title of the course's teacher.
    :param course_id: course id.
    :param class_name: class name (constant between years).
    :param class_id: class id (variable between years).
    :param hour_total: credit hours of the course.
    :param hour_remark: detailed explanation of the credit hours.
    :param hour_week: credit hours of the course every week.
    :param field: professional field of this course.
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

    Usage::

        >>> sched = ... # something that returns a Exams, for example pysjtu.Client().schedule(...)
        >>> sched
        [<ScheduleCourse 军事理论 week=[range(9, 17)] day=1 time=range(1, 3)>, ...]
        >>> sched.filter(time=[1, range(5, 7)], day=[2, range(4, 5)]))
        [<ScheduleCourse 线性代数 week=[range(1, 7), range(8, 17)] day=2 time=range(1, 3)>,
        <ScheduleCourse 线性代数 week=[7] day=2 time=range(1, 3)>,
        <ScheduleCourse 思想道德修养与法律基础 week=[range(1, 17)] day=2 time=range(6, 9)>,
        <ScheduleCourse 程序设计思想与方法（C++） week=[range(1, 16, 2)] day=4 time=range(1, 3)>]
    """
    _schema = ScheduleCourseSchema
    _result_model = ScheduleCourse
