from marshmallow import EXCLUDE, Schema, fields, post_load  # type: ignore

from pysjtu.schemas.base import CommaSplitted, CourseTime, CourseWeek, CreditHourDetail


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
    teacher_name = CommaSplitted(data_key="xm")
    teacher_title = CommaSplitted(data_key="zcmc")
    course_id = fields.Str(required=True, data_key="kch_id")
    class_name = fields.Str(required=True, data_key="jxbmc")
    class_id = fields.Str(required=True, data_key="jxb_id")
    hour_total = fields.Int(data_key="zxs")
    hour_remark = CreditHourDetail(data_key="kcxszc")
    hour_week = fields.Int(data_key="zhxs")
    field = fields.Str(data_key="zyfxmc")

    # noinspection PyUnusedLocal
    @post_load
    def wrap(self, data, **kwargs):
        return ScheduleCourse(**data)


from pysjtu.models.schedule import ScheduleCourse
