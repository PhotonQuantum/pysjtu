import datetime
import typing
from datetime import datetime
from typing import List, Optional

from marshmallow import fields, EXCLUDE
from marshmallow_dataclass import dataclass

from pysjtu.fields import ChineseBool
from pysjtu.models.base import Result, Results
from pysjtu.schema import mfield, WithField, FinalizeHook, LoadDumpSchema


class _ExamDate(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return datetime.strptime(value[:value.index("(")], "%Y-%m-%d").date()


class _ExamTime(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        raw_time = value[value.find("(") + 1:-1].split("-")
        return [datetime.strptime(time, "%H:%M").time() for time in raw_time]


@dataclass(base_schema=FinalizeHook(LoadDumpSchema))
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
    name: str = mfield(required=True, data_key="ksmc")
    location: Optional[str] = mfield(None, data_key="cdmc")
    seat: Optional[int] = mfield(None, data_key="zwh")
    course_id: Optional[str] = mfield(None, data_key="kch")
    course_name: Optional[str] = mfield(None, data_key="kcmc")
    class_name: Optional[str] = mfield(None, data_key="jxbmc")
    rebuild: WithField(Optional[bool], field=ChineseBool) = mfield(None, data_key="cxbj")
    credit: Optional[float] = mfield(None, data_key="xf")
    self_study: WithField(Optional[bool], field=ChineseBool) = mfield(None, data_key="zxbj")
    date: WithField(Optional[datetime.date], field=_ExamDate) = mfield(None, data_key="kssj", load_only=True)
    time: WithField(Optional[List[datetime.time]], field=_ExamTime) = mfield(None, data_key="kssj", load_only=True)

    class Meta:
        unknown = EXCLUDE

    def __repr__(self):
        date_out = self.date.strftime("%Y-%m-%d")
        time_out = [time.strftime("%H:%M") for time in self.time]
        return f"<Exam \"{self.name}\" course_name={self.course_name} location={self.location} " \
               f"datetime={date_out}({time_out[0]}-{time_out[1]})>"


class Exams(Results[Exam]):
    """
    A list-like interface to Exam collections.
    """
    _item = Exam
