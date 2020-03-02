import typing
from datetime import datetime

from marshmallow import EXCLUDE, Schema, fields, post_load  # type: ignore

from pysjtu.schemas.base import ChineseBool


class ExamDate(fields.Field):
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


class ExamTime(fields.Field):
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


class ExamSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True, data_key="ksmc")
    location = fields.Str(data_key="cdmc")
    seat = fields.Int(data_key="zwh")
    course_id = fields.Str(data_key="kch")
    course_name = fields.Str(data_key="kcmc")
    class_name = fields.Str(data_key="jxbmc")
    rebuild = ChineseBool(data_key="cxbj")
    credit = fields.Float(data_key="xf")
    self_study = ChineseBool(data_key="zxbj")
    date = ExamDate(data_key="kssj", load_only=True)
    time = ExamTime(data_key="kssj", load_only=True)

    # noinspection PyUnusedLocal
    @post_load
    def wrap(self, data, **kwargs):
        return Exam(**data)


from pysjtu.models.exam import Exam
