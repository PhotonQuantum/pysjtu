# flake8: noqa
import typing
from typing import List, Optional

from marshmallow import fields, EXCLUDE
from marshmallow_dataclass import dataclass

from pysjtu.fields import CourseWeek, CourseTime, SplitField
from pysjtu.models.base import Result, Results
from pysjtu.schema import mfield, WithField, FinalizeHook, LoadDumpSchema


class _CreditHourDetail(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        class_hour_details = value.split(",")
        rtn = {}
        for item in class_hour_details:
            try:
                name, hour = item.split(":")
                rtn[name] = float(hour)
            except ValueError:
                rtn["N/A"] = 0
        return rtn


@dataclass(base_schema=FinalizeHook(LoadDumpSchema))
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
    name: str = mfield(required=True, data_key="kcmc")
    course_id: str = mfield(required=True, data_key="kch_id")
    class_name: str = mfield(required=True, data_key="jxbmc")
    class_id: str = mfield(required=True, data_key="jxb_id")
    day: Optional[int] = mfield(None, data_key="xqj")
    week: WithField(Optional[list], field=CourseWeek) = mfield(None, data_key="zcd")
    time: WithField(Optional[range], field=CourseTime) = mfield(None, data_key="jcs")
    location: Optional[str] = mfield(None, data_key="cdmc")
    credit: Optional[float] = mfield(None, data_key="xf")
    assessment: Optional[str] = mfield(None, data_key="khfsmc")
    remark: Optional[str] = mfield(None, data_key="xkbz")
    teacher_name: WithField(Optional[List[str]], field=SplitField, sep=",") = mfield(None, data_key="xm")
    teacher_title: WithField(Optional[List[str]], field=SplitField, sep=",") = mfield(None, data_key="zcmc")
    hour_total: Optional[int] = mfield(None, data_key="zxs")
    hour_remark: WithField(Optional[dict], field=_CreditHourDetail) = mfield(None, data_key="kcxszc")
    hour_week: Optional[float] = mfield(None, data_key="zhxs")
    field: Optional[str] = mfield(None, data_key="zyfxmc")

    class Meta:
        unknown = EXCLUDE

    def __repr__(self):
        return f"<ScheduleCourse {self.name} week={self.week} day={self.day} time={self.time}>"


class Schedule(Results[ScheduleCourse]):
    """
    A list-like interface to Schedule collections.
    """
    _item = ScheduleCourse
