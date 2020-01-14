import typing
from datetime import datetime

from marshmallow import Schema, fields, EXCLUDE, post_load


class CourseTeacher(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return
        return value.split(",")


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
        value = value.replace("节", "")
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
        class_hour_details = value.split(",")
        rtn = dict()
        for item in class_hour_details:
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

    name = fields.Str(required=True, data_key="kcmc")
    day = fields.Int(data_key="xqj")
    week = CourseWeek(data_key="zcd")
    time = CourseTime(data_key="jcs")
    location = fields.Str(data_key="cdmc")
    credit = fields.Float(data_key="xf")
    assessment = fields.Str(data_key="khfsmc")
    remark = fields.Str(data_key="xkbz")
    teacher_name = CourseTeacher(data_key="xm")
    teacher_title = CourseTeacher(data_key="zcmc")
    course_id = fields.Str(required=True, data_key="kch_id")
    class_name = fields.Str(required=True, data_key="jxbmc")
    class_id = fields.Str(required=True, data_key="jxb_id")
    hour_total = fields.Int(data_key="zxs")
    hour_remark = CreditHourDetail(data_key="kcxszc")
    hour_week = fields.Int(data_key="zhxs")
    field = fields.Str(data_key="zyfxmc")

    @post_load
    def wrap(self, data, **kwargs):
        return ScheduleCourse(**data)


class ScoreFactorName(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return
        return value[:value.find("(")]


class ScoreFactorPercentage(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return
        return float(value[value.find("(") + 1:value.find("%")]) / 100


class ChineseBool(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return
        return value == "是"


class ScoreFactorSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = ScoreFactorName(required=True, data_key="xmblmc")
    percentage = ScoreFactorPercentage(required=True, data_key="xmblmc", load_only=True)
    score = fields.Float(required=True, data_key="xmcj")

    @post_load
    def wrap(self, data, **kwargs):
        return ScoreFactor(**data)


class ScoreSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True, data_key="kcmc")
    teacher = fields.Str(data_key="jsxm")
    score = fields.Str(required=True, data_key="cj")
    credit = fields.Float(required=True, data_key="xf")
    gp = fields.Float(required=True, data_key="jd")
    invalid = ChineseBool(data_key="cjsfzf")
    course_type = fields.Str(data_key="kcbj")
    category = fields.Str(data_key="kclbmc")
    score_type = fields.Str(data_key="kcxz")
    method = fields.Str(data_key="khfsmc")
    course_id = fields.Str(data_key="kch_id")
    class_name = fields.Str(data_key="jxbmc")
    class_id = fields.Str(data_key="jxb_id")

    @post_load
    def wrap(self, data, **kwargs):
        return Score(**data)


class ExamDate(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return
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
            return
        raw_time = value[value.find("(")+1:-1].split("-")
        return [datetime.strptime(time, "%H:%M").time() for time in raw_time]


class ExamSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True, data_key="ksmc")
    location = fields.Str(data_key="cdmc")
    course_id = fields.Str(data_key="kch")
    course_name = fields.Str(data_key="kcmc")
    class_name = fields.Str(data_key="jxbmc")
    rebuild = ChineseBool(data_key="cxbj")
    credit = fields.Float(data_Key="xf")
    self_study = ChineseBool(data_key="zxbj")
    date = ExamDate(data_key="kssj", load_only=True)
    time = ExamTime(data_key="kssj", load_only=True)

    @post_load
    def wrap(self, data, **kwargs):
        return Exam(**data)


class ColonSplitted(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return
        return value.split(";")


class LibCourseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True, data_key="kcmc")
    day = fields.Int(data_key="xqj")
    week = CourseWeek(data_key="qzjsz")
    time = CourseTime(data_key="skjc")
    location = fields.Str(data_key="cdmc")
    locations = ColonSplitted(data_key="jxdd")
    faculty = fields.Str(data_key="kkxy")
    credit = fields.Float(data_key="xf")
    teacher_name = CourseTeacher(data_key="zjs")
    teacher_title = CourseTeacher(data_key="jszc")
    course_id = fields.Str(data_key="kch_id")
    class_name = fields.Str(data_key="jxbmc")
    class_id = fields.Str(data_key="jxb_id")
    class_composition = ColonSplitted(data_key="jxbzc")
    hour_total = fields.Int(data_key="rwzxs")
    hour_remark = CreditHourDetail(data_key="kcxszc")
    seats = fields.Int(data_key="zws")
    students_elected = fields.Int(data_key="xkrs")
    students_planned = fields.Int(data_key="jxbrs")


    @post_load
    def wrap(self, data, **kwargs):
        return LibCourse(**data)

from .model import *
