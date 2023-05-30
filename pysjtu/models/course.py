# flake8: noqa
import typing
from typing import List, Optional

from marshmallow import fields, EXCLUDE
from marshmallow_dataclass import dataclass

from pysjtu.fields import CourseWeek, CourseTime, SplitField
from pysjtu.models.base import Result
from pysjtu.schema import mfield, WithField, FinalizeHook, LoadDumpSchema


class _LibCreditHourDetail(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        class_hour_details = value.split("-")
        rtn = {}
        for item in class_hour_details:
            name, hour = item.split("(")
            rtn[name] = float(hour[:-1])
        return rtn


@dataclass(base_schema=FinalizeHook(LoadDumpSchema))
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
    name: str = mfield(required=True, data_key="kcmc")
    day: Optional[int] = mfield(None, data_key="xqj")
    week: WithField(Optional[list], CourseWeek) = mfield(None, data_key="qsjsz")
    time: WithField(Optional[range], CourseTime) = mfield(None, data_key="skjc")
    location: Optional[str] = mfield(None, data_key="cdmc")
    locations: WithField(Optional[List[str]], field=SplitField, sep=";") = mfield(None, data_key="jxdd")
    faculty: Optional[str] = mfield(None, data_key="kkxy")
    credit: Optional[float] = mfield(None, data_key="xf")
    teacher: WithField(Optional[List[str]], field=SplitField, sep=",") = mfield(None, data_key="zjs")
    course_id: Optional[str] = mfield(None, data_key="kch")
    class_name: Optional[str] = mfield(None, data_key="jxbmc")
    class_id: Optional[str] = mfield(None, data_key="jxb_id")
    class_composition: WithField(Optional[List[str]], field=SplitField, sep=";") = mfield(None, data_key="jxbzc")
    hour_total: Optional[int] = mfield(None, data_key="rwzxs")
    hour_remark: WithField(Optional[dict], _LibCreditHourDetail) = mfield(None, data_key="zhxs")
    seats: Optional[int] = mfield(None, data_key="zws")
    students_elected: Optional[int] = mfield(None, data_key="xkrs")
    students_planned: Optional[int] = mfield(None, data_key="jxbrs")

    class Meta:
        unknown = EXCLUDE

    def __repr__(self):
        return f"<LibCourse {self.name} class_name={self.class_name}>"
