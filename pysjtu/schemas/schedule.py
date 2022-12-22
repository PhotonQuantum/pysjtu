import typing

from marshmallow import EXCLUDE, Schema, fields, post_load  # type: ignore

from pysjtu.schemas.base import CourseTime, CourseWeek, SplitField


class CreditHourDetail(fields.Field):
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


class ScheduleCourseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True, data_key="kcmc")
    day = fields.Int(data_key="xqj")
    week = CourseWeek(data_key="zcd")
    time = CourseTime(data_key="jcs")
    location = fields.Str(data_key="cdmc")
    credit = fields.Float(data_key="xf")
    assessment = fields.Str(data_key="khfsmc")
    remark = fields.Str(data_key="xkbz")
    teacher_name = SplitField(data_key="xm", sep=",")
    teacher_title = SplitField(data_key="zcmc", sep=",")
    course_id = fields.Str(required=True, data_key="kch_id")
    class_name = fields.Str(required=True, data_key="jxbmc")
    class_id = fields.Str(required=True, data_key="jxb_id")
    hour_total = fields.Int(data_key="zxs")
    hour_remark = CreditHourDetail(data_key="kcxszc")
    hour_week = fields.Float(data_key="zhxs")
    field = fields.Str(data_key="zyfxmc")

    # noinspection PyUnusedLocal
    @post_load
    def wrap(self, data, **kwargs):
        return ScheduleCourse(**data)


from pysjtu.models.schedule import ScheduleCourse
