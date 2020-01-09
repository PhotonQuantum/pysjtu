from marshmallow import Schema, fields, EXCLUDE, post_load
import typing


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


class ScoreInvalid(fields.Field):
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
    score = fields.Number(required=True, data_key="xmcj")

    @post_load
    def wrap(self, data, **kwargs):
        return ScoreFactor(**data)


class ScoreSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True, data_key="kcmc")
    teacher = fields.Str(data_key="jsxm")
    score = fields.Int(required=True, data_key="cj")
    credit = fields.Number(required=True, data_key="xf")
    gp = fields.Number(required=True, data_key="jd")
    invalid = ScoreInvalid(data_key="cjsfzf")
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


from .model import *
