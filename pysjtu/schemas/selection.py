import re
import typing
from dataclasses import dataclass
from typing import List, Union

from marshmallow import EXCLUDE, Schema, fields, post_load  # type: ignore

from pysjtu.consts import CHINESE_WEEK
from pysjtu.schemas.base import BrSplitted, CommaSplitted
from pysjtu.utils import parse_course_week


@dataclass
class LessonTime:
    weekday: int
    week: List[Union[range, int]]
    time: List[range]


class TimeField(fields.Field):
    regex = re.compile("星期(?P<weekday>.)第(?P<time>.*?)节{(?P<week>.*?)}")

    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover

        def _parse_time(input_str: str) -> List[range]:
            return [range(int(time[0]), int(time[1])) for time in [times.split('-') for times in input_str.split(",")]]

        def _dict_to_time(input_dict: dict) -> LessonTime:
            return LessonTime(
                weekday=CHINESE_WEEK[input_dict["weekday"]],
                week=parse_course_week(input_dict["week"]),
                time=_parse_time(input_dict["time"])
            )

        return [_dict_to_time(match.groupdict()) for match in self.regex.finditer(value)]


class TeacherField(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return [tuple(teacher.split("/")[1:]) for teacher in value.split(";")]


class SelectionSharedInfoSchema(Schema):
    term = fields.Str(required=True, data_key="xqh_id")
    selection_year = fields.Int(required=True, data_key="xkxnm")
    selection_term = fields.Int(required=True, data_key="xkxqm")
    major_id = fields.Str(required=True, data_key="zyh_id")
    student_grade = fields.Int(required=True, data_key="njdm_id")
    natural_class_id = fields.Str(required=True, data_key="bh_id")
    self_selecting_status = fields.Int(required=True, data_key="xszxzt")

    # noinspection PyUnusedLocal
    @post_load
    def wrap(self, data, **kwargs):
        return SelectionSharedInfo(**data)


class SelectionSectorSchema(Schema):
    task_type = fields.Int(required=True, data_key="rwlx")
    xkly = fields.Int(required=True)
    pe_op_param = fields.Int(required=True, data_key="tykczgxdcs")
    sector_type_id = fields.Str(required=True, data_key="bklx_id")
    course_type_code = fields.Str(required=True, dump_only=True, data_key="kklxdm")
    txbsfrl = fields.Int(required=True)
    xkkz_id = fields.Str(dump_only=True)

    # noinspection PyUnusedLocal
    @post_load
    def wrap(self, data, **kwargs):
        return SelectionSector(**data)


class SelectionCourseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True, data_key="kcmc")
    credit = fields.Float(required=True, data_key="xf")
    course_id = fields.Str(required=True, data_key="kch")
    internal_course_id = fields.Str(required=True, data_key="kch_id")
    class_name = fields.Str(required=True, data_key="jxbmc")
    class_id = fields.Str(required=True, data_key="jxb_id")
    students_registered = fields.Int(required=True, data_key="yxzrs")


class SelectionClassSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    class_id = fields.Str(required=True, data_key="jxb_id")
    register_id = fields.Str(required=True, data_key="do_jxb_id")
    teachers = TeacherField(required=True, data_key="jsxx")
    locations = BrSplitted(required=True, data_key="jxdd")
    time = TimeField(required=True, data_key="sksj")
    course_type = CommaSplitted(required=True, data_key="kcxzmc")
    remark = fields.Str(data_key="xkbz", missing=None)
    students_planned = fields.Int(required=True, data_key="jxbrl")


from pysjtu.models.selection import SelectionSharedInfo, SelectionSector
