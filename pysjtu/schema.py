import typing
from copy import deepcopy
from datetime import datetime

from marshmallow import Schema, fields, EXCLUDE, pre_load, post_load, pre_dump, post_dump

from .utils import replace_keys


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
    teacher_name = CourseTeacher(data_key="xm")
    teacher_title = CourseTeacher(data_key="zcmc")
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

    # noinspection PyUnusedLocal
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

    # noinspection PyUnusedLocal
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
        raw_time = value[value.find("(") + 1:-1].split("-")
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

    # noinspection PyUnusedLocal
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

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        return ";".join([str(item) for item in value])


class CommaSplitted(fields.Field):
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

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        return ",".join([str(item) for item in value])


class HasRoll(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return
        if "1" in value.split(","):
            return True
        elif "2" in value.split(","):
            return False
        else:
            return

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        if value is True:
            return 1
        elif value is False:
            return 0
        else:
            return -1


class Registered(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None
        if "3" in value.split(","):
            return True
        elif "4" in value.split(","):
            return False
        else:
            return

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        if value is True:
            return 1
        elif value is False:
            return 0
        else:
            return -1


class Attending(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None
        if "5" in value.split(","):
            return True
        elif "6" in value.split(","):
            return False
        else:
            return

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        if value is True:
            return 1
        elif value is False:
            return 0
        else:
            return -1


class ConditionLogic(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None
        if value == 0:
            return LogicEnum.AND
        elif value == 1:
            return LogicEnum.OR

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        if not value:
            return 0
        if value == LogicEnum.AND:
            return 0
        elif value == LogicEnum.OR:
            return 1
        else:
            raise ValueError


class MakeupAsPass(fields.Field):
    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        return "bk" if value else ""


class RebuildAsPass(fields.Field):
    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        return "cx" if value else ""


class RankingField(fields.Field):
    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        if not isinstance(value, Ranking):
            raise TypeError
        return value.value


class CourseRangeField(fields.Field):
    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        if not isinstance(value, CourseRange):
            raise TypeError
        return value.value


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

    # noinspection PyUnusedLocal
    @post_load
    def wrap(self, data, **kwargs):
        return LibCourse(**data)


class GPAQueryParamsSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    start_term = fields.Int(dump_key="qsXnxq", dump_only=True)
    end_term = fields.Int(dump_key="zzXnxq", dump_only=True)
    condition_logic = ConditionLogic(dump_key="tjgx", dump_only=True)
    makeup_as_60 = MakeupAsPass(dump_only=True)
    rebuild_as_60 = RebuildAsPass(dump_only=True)
    gp_round = fields.Int(load_key="cjblws", dump_key="sspjfblws")
    gpa_round = fields.Int(load_key="jdblws", dump_key="pjjdblws")
    exclude_gp = fields.Str(data_key="bjjd")
    exclude_gpa = fields.Str(data_key="bjpjf")
    course_whole = CommaSplitted(load_key="tjqckc", dump_key="kch_ids")
    course_range = CourseRangeField(dump_key="kcfw", dump_only=True)
    ranking = RankingField(dump_key="tjfw", dump_only=True)
    has_roll = HasRoll(data_key="atjc", load_only=True)
    registered = Registered(data_key="atjc", load_only=True)
    attending = Attending(data_key="atjc", load_only=True)
    has_roll_dump = HasRoll(data_key="xjzt", dump_only=True)
    registered_dump = Registered(data_key="zczt", dump_only=True)
    attending_dump = Attending(data_key="sfzx", dump_only=True)

    # noinspection PyUnusedLocal
    @pre_load
    def wrap_pre_load(self, data, **kwargs):
        pairs = tuple(
            (field.metadata['load_key'], field.data_key or field_name)
            for field_name, field in self.fields.items() if 'load_key' in field.metadata
        )
        return replace_keys(data, pairs)

    # noinspection PyUnusedLocal
    @post_load
    def wrap_post_load(self, data, **kwargs):
        return GPAQueryParams(makeup_as_60=False, rebuild_as_60=False, ranking=Ranking.GRADE_AND_FIELD,
                              course_range=CourseRange.CORE, start_term=None, end_term=None,
                              condition_logic=LogicEnum.AND, **data)

    # noinspection PyUnusedLocal
    @pre_dump
    def wrap_pre_dump(self, data, **kwargs):
        pre_dict = deepcopy(data.__dict__)
        pre_dict["has_roll_dump"] = pre_dict.pop("has_roll")
        pre_dict["registered_dump"] = pre_dict.pop("registered")
        pre_dict["attending_dump"] = pre_dict.pop("attending")
        return pre_dict

    # noinspection PyUnusedLocal
    @post_dump
    def wrap_post_dump(self, data, **kwargs):
        pairs = tuple(
            (field.data_key or field_name, field.metadata['dump_key'])
            for field_name, field in self.fields.items() if 'dump_key' in field.metadata
        )
        data = replace_keys(data, pairs)

        parse_fields = ["xjzt", "zczt", "sfzx"]
        data["alsfj"] = data.pop("makeup_as_60") + data.pop("rebuild_as_60")
        for field in parse_fields:
            if data[field] == -1:
                data.pop(field)

        parse_fields = ["qsXnxq", "zzXnxq"]
        for field in parse_fields:
            if data[field] is None:
                data[field] = ''
        return data


class Percentage(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return
        return float(value.replace("%", "")) / 100


class RankingResultField(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return
        return value.split("/")[0]


class StudentCountFromRanking(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return
        return value.split("/")[1]


class GPASchema(Schema):
    class Meta:
        unknown = EXCLUDE

    total_score = fields.Int(data_key="zf")
    course_count = fields.Int(data_key="mc")
    fail_count = fields.Int(data_key="bjgms")
    total_credit = fields.Float(data_key="zxf")
    acquired_credit = fields.Float(data_key="hdxf")
    failed_credit = fields.Float(data_key="bjgxf")
    pass_rate = Percentage(data_key="tgl")
    gp = fields.Float(data_key="xjf")
    gp_ranking = RankingResultField(data_key="xjfpm")
    gpa = fields.Float(data_key="gpa")
    gpa_ranking = RankingResultField(data_key="gpapm", load_only=True)
    total_students = StudentCountFromRanking(data_key="gpapm", load_only=True)

    # noinspection PyUnusedLocal
    @post_load
    def wrap(self, data, **kwargs):
        return GPA(**data)


from .model import *
