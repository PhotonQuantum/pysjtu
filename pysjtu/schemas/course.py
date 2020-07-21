import typing

from marshmallow import EXCLUDE, Schema, fields, post_load  # type: ignore

from pysjtu.schemas.base import CourseTime, CourseWeek, SplitField


class LibCreditHourDetail(fields.Field):
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


class LibCourseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True, data_key="kcmc")
    day = fields.Int(data_key="xqj")
    week = CourseWeek(data_key="qsjsz")
    time = CourseTime(data_key="skjc")
    location = fields.Str(data_key="cdmc")
    locations = SplitField(data_key="jxdd", sep=";")
    faculty = fields.Str(data_key="kkxy")
    credit = fields.Float(data_key="xf")
    teacher = SplitField(data_key="zjs", sep=",")
    course_id = fields.Str(data_key="kch")
    class_name = fields.Str(data_key="jxbmc")
    class_id = fields.Str(data_key="jxb_id")
    class_composition = SplitField(data_key="jxbzc", sep=";")
    hour_total = fields.Int(data_key="rwzxs")
    hour_remark = LibCreditHourDetail(data_key="zhxs")
    seats = fields.Int(data_key="zws")
    students_elected = fields.Int(data_key="xkrs")
    students_planned = fields.Int(data_key="jxbrs")

    # noinspection PyUnusedLocal
    @post_load
    def wrap(self, data, **kwargs):
        return LibCourse(**data)


from pysjtu.models.course import LibCourse
