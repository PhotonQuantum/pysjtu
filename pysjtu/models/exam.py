import datetime
from dataclasses import dataclass
from typing import List, Optional

from pysjtu.models.base import Result, Results


@dataclass
class Exam(Result):
    """
    A model which describes an exam. Some fields may be empty.

    :param name: name of the course on which you are being examined.
    :type name: str
    :param location: the place where this exam is held.
    :type location: str
    :param seat: seat number
    :type seat: int
    :param course_id: course id of the course on which you are being examined.
    :type course_id: str
    :param course_name: course name of the course on which you are being examined.
    :type course_name: str
    :param class_name: class name of the class you are attending on the course which are being examined.
    :type class_name: str
    :param rebuild: whether this exam is a rebuild test.
    :type rebuild: bool
    :param credit: credits that the course provides.
    :type credit: float
    :param self_study: whether this course is a self study course.
    :type self_study: bool
    :param date: date of the exam
    :type date: datetime.date
    :param time: time range of the exam
    :type time: List[datetime.time]
    """
    name: str
    location: Optional[str] = None
    seat: Optional[int] = None
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    class_name: Optional[str] = None
    rebuild: Optional[bool] = None
    credit: Optional[float] = None
    self_study: Optional[bool] = None
    date: Optional[datetime.date] = None
    time: Optional[List[datetime.time]] = None

    def __repr__(self):
        date_out = self.date.strftime("%Y-%m-%d")
        time_out = [time.strftime("%H:%M") for time in self.time]
        return f"<Exam \"{self.name}\" course_name={self.course_name} location={self.location} " \
               f"datetime={date_out}({time_out[0]}-{time_out[1]})>"


from pysjtu.schemas.exam import ExamSchema


class Exams(Results[Exam]):
    """
    A list-like interface to Exam collections.
    An additional filter method has been added to make filter operations easier.
    """
    _schema = ExamSchema
    _result_model = Exam
