from marshmallow import Schema, fields, EXCLUDE, post_load
from .util import overlap
import typing


class Schedule:
    _courses = []

    def load(self, data):
        schema = CourseSchema(many=True)
        self._courses = schema.load(data)

    def all(self):
        return self._courses

    def filter(self, **param):
        rtn = self._courses
        for (k, v) in param.items():
            if k not in self._courses[0]:
                raise KeyError("Invalid criteria!")
            if k in ("week", "time", "day"):
                rtn = list(filter(lambda x: overlap(x[k], v), rtn))
            else:
                rtn = list(filter(lambda x: x[k] == v, rtn))
        return rtn


class CourseTime(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return
        cs = list(map(int, value.split("-")))
        return list(cs) if len(cs) == 1 else range(cs[0], cs[1] + 1)


class CreditHourDetail(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return
        credit_hour_details = value.split(",")
        rtn = dict()
        for item in credit_hour_details:
            name, hour = item.split(":")
            rtn[name] = hour
        return rtn


class CourseWeek(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        rtn = list()
        for item in value.split(','):
            if item[-2] in ["单", "双"]:
                start, end = map(int, item[:-4].split('-'))
                start += (1 - start % 2) if item[-2] == "单" else (start % 2)
                rtn.append(range(start, end + 1, 2))
            else:
                x = list(map(int, item[:-1].split('-')))
                rtn.append(x[0] if len(x) == 1 else range(x[0], x[1] + 1))
        return rtn


class CourseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(data_key="kcmc")
    day = fields.Int(data_key="xqj")
    week = CourseWeek(data_key="zcd")
    time = CourseTime(data_key="jcs")
    location = fields.Str(data_key="cdmc")
    credit = fields.Float(data_key="xf")
    assessment = fields.Str(data_key="khfsmc")
    remark = fields.Str(data_key="xkbz")
    teacher_name = fields.Str(data_key="xm")
    teacher_title = fields.Str(data_key="zcmc")
    course_code = fields.Str(data_key="kch_id")
    course_code_detail = fields.Str(required=True, data_key="jxbmc")
    course_id = fields.Str(required=True, data_key="jxb_id")
    credit_hour_total = fields.Int(data_key="zxs")
    credit_hour_detail = CreditHourDetail(data_key="kcxszc")
    credit_hour_week = fields.Int(data_key="zhxs")

    @post_load
    def wrap(self, data, **kwargs):
        data["teacher"] = {"name": data.pop("teacher_name", None), "title": data.pop("teacher_title", None)}
        data["meta"] = {"code": data.pop("course_code", None), "long_code": data.pop("course_code_detail", None),
                        "jxb_ids": data.pop("course_id", None)}
        data["credit_hour"] = {"week": data.pop("credit_hour_week", None), "total": data.pop("credit_hour_total", None),
                               "detail": data.pop("credit_hour_detail", None)}
        return data
