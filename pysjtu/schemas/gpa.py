import typing
from copy import deepcopy

from marshmallow import EXCLUDE, Schema, fields, post_dump, post_load, pre_dump, pre_load  # type: ignore

from pysjtu.schemas.base import SplitField
from pysjtu.utils import replace_keys


class HasRoll(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        if "1" in value.split(","):
            return True
        if "2" in value.split(","):  # pragma: no cover
            return False  # pragma: no cover
        return None  # pragma: no cover

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        if value is True:
            return 1
        if value is False:
            return 0
        return -1  # pragma: no cover


class Registered(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        if "3" in value.split(","):
            return True  # pragma: no cover
        if "4" in value.split(","):
            return False  # pragma: no cover
        return None

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        if value is True:
            return 1
        if value is False:  # pragma: no cover
            return 0  # pragma: no cover
        return -1  # pragma: no cover


class Attending(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        if "5" in value.split(","):
            return True
        if "6" in value.split(","):  # pragma: no cover
            return False  # pragma: no cover
        return None  # pragma: no cover

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        if value is True:
            return 1
        if value is False:
            return 0  # pragma: no cover
        return -1


class ConditionLogic(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if value == 0:  # pragma: no cover
            return LogicEnum.AND  # pragma: no cover
        if value == 1:  # pragma: no cover
            return LogicEnum.OR  # pragma: no cover
        return None  # pragma: no cover

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        if not isinstance(value, LogicEnum):
            raise TypeError
        if value == LogicEnum.AND:
            return 0
        if value == LogicEnum.OR:  # pragma: no cover
            return 1  # pragma: no cover


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


class Percentage(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
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
            return None  # pragma: no cover
        return int(value.split("/")[0])


class StudentCountFromRanking(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return int(value.split("/")[1])


class GPAQueryParamsSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    start_term = fields.Int(required=True, dump_key="qsXnxq", dump_only=True)
    end_term = fields.Int(required=True, dump_key="zzXnxq", dump_only=True)
    condition_logic = ConditionLogic(required=True, dump_key="tjgx", dump_only=True)
    makeup_as_60 = MakeupAsPass(required=True, dump_only=True)
    rebuild_as_60 = RebuildAsPass(required=True, dump_only=True)
    gp_round = fields.Int(required=True, load_key="cjblws", dump_key="sspjfblws")
    gpa_round = fields.Int(required=True, load_key="jdblws", dump_key="pjjdblws")
    exclude_gp = fields.Str(required=True, data_key="bjjd")
    exclude_gpa = fields.Str(required=True, data_key="bjpjf")
    course_whole = SplitField(required=True, load_key="tjqckc", dump_key="kch_ids", sep=",")
    course_range = CourseRangeField(required=True, dump_key="kcfw", dump_only=True)
    ranking = RankingField(required=True, dump_key="tjfw", dump_only=True)
    has_roll = HasRoll(required=True, data_key="atjc", load_only=True)
    registered = Registered(required=True, data_key="atjc", load_only=True)
    attending = Attending(required=True, data_key="atjc", load_only=True)
    has_roll_dump = HasRoll(required=True, data_key="xjzt", dump_only=True)
    registered_dump = Registered(required=True, data_key="zczt", dump_only=True)
    attending_dump = Attending(required=True, data_key="sfzx", dump_only=True)

    # noinspection PyUnusedLocal
    @pre_load
    def wrap_pre_load(self, data, **kwargs):
        data = {item["zdm"]: item["szz"] for item in filter(lambda x: "szz" in x.keys(), data)}
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


class GPASchema(Schema):
    class Meta:
        unknown = EXCLUDE

    total_score = fields.Int(required=True, data_key="zf")
    course_count = fields.Int(required=True, data_key="ms")
    fail_count = fields.Int(required=True, data_key="bjgms")
    total_credit = fields.Float(required=True, data_key="zxf")
    acquired_credit = fields.Float(required=True, data_key="hdxf")
    failed_credit = fields.Float(required=True, data_key="bjgxf")
    pass_rate = Percentage(required=True, data_key="tgl")
    gp = fields.Float(required=True, data_key="xjf")
    gp_ranking = RankingResultField(required=True, data_key="xjfpm")
    gpa = fields.Float(required=True, data_key="gpa")
    gpa_ranking = RankingResultField(required=True, data_key="gpapm", load_only=True)
    total_students = StudentCountFromRanking(required=True, data_key="gpapm", load_only=True)

    # noinspection PyUnusedLocal
    @post_load
    def wrap(self, data, **kwargs):
        return GPA(**data)


from pysjtu.models.gpa import LogicEnum, Ranking, CourseRange, GPAQueryParams, GPA
