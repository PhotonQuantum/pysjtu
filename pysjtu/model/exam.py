import datetime
from typing import List

from pysjtu.model.base import Result, Results


class Exam(Result):
    """
    A model which describes an exam. Some fields may be empty.

    :param name: name of the course on which you are being examined.
    :param location: the place where this exam is held.
    :param seat: seat number
    :param course_id: course id of the course on which you are being examined.
    :param course_name: course name of the course on which you are being examined.
    :param class_name: class name of the class you are attending on the course which are being examined.
    :param rebuild: whether this exam is a rebuild test.
    :param credit: credits that the course provides.
    :param self_study: whether this course is a self study course.
    :param date: date of the exam
    :param time: time range of the exam
    """
    name: str
    location: str
    seat: int
    course_id: str
    course_name: str
    class_name: str
    rebuild: bool
    credit: float
    self_study: bool
    date: datetime.date
    time: List[datetime.time]

    _members = ["name", "location", "seat", "course_id", "course_name", "class_name", "rebuild", "credit", "self_study",
                "date", "time"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        date_out = self.date.strftime("%Y-%m-%d")
        time_out = [time.strftime("%H:%M") for time in self.time]
        return f"<Exam \"{self.name}\" location={self.location} datetime={date_out}({time_out[0]}-{time_out[1]})>"


from pysjtu.schema.exam import ExamSchema


class Exams(Results[Exam]):
    """
    A list-like interface to Exam collections.
    An additional filter method has been added to make filter operations easier.

    Usage::

        >>> exams = ... # something that returns a Exams, for example pysjtu.Client().exam(...)
        >>> exams
        [<Exam "2019-2020-1数学期中考" location=东上院509 datetime=2019-11-06(13:10-15:10)>, ...]
        >>> from datetime import date
        >>> exams.filter(date=date(2019, 12, 31))
        [<Exam "2019-2020-1一专期末考（2019级）" location=东上院509 datetime=2019-12-31(08:00-10:00)>]
    """
    _schema = ExamSchema
    _result_model = Exam
