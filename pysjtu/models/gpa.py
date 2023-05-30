# flake8: noqa
import typing
from enum import Enum, IntEnum
from typing import List, Optional

from marshmallow import EXCLUDE, fields
from marshmallow_dataclass import dataclass

from pysjtu.fields import SplitField
from pysjtu.models.base import Result
from pysjtu.schema import FinalizeHook, LoadDumpSchema, mfield, WithField


class _HasRoll(fields.Field):
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


class _Registered(fields.Field):
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


class _Attending(fields.Field):
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


class _MakeupAsPass(fields.Field):
    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        return "bk" if value else ""


class _RebuildAsPass(fields.Field):
    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        return "cx" if value else ""


class _Percentage(fields.Field):
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


class _RankingResult(fields.Field):
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


class _StudentCountFromRanking(fields.Field):
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


class LogicEnum(IntEnum):
    """ Used by :class:`GPAQueryParams` to specify condition logic."""

    AND = 0
    """All conditions must be satisfied."""
    OR = 1
    """At least one condition must be satisfied."""


class CourseRange(Enum):
    """ Used by :class:`GPAQueryParams` to specify courses taken into account when ranking."""
    ALL = "qbkc"
    """All courses taken."""
    CORE = "hxkc"
    """Only core courses taken."""


class Ranking(Enum):
    """ Used by :class:`GPAQueryParams` to specify student range upon which to rank."""
    GRADE_AND_FIELD = "njzy"
    """Rank students in the same grade and field."""


class DedupMethod(Enum):
    """ Used by :class:`GPAQueryParams` to specify which score to take if a student has taken a course multiple
    times."""
    LAST_SCORE = "zhyccj"
    """Take the last score."""


class _GPAQueryParamsExtSchema(LoadDumpSchema):
    def pre_load(self, data, **kwargs):
        data = {item["zdm"]: item["szz"] for item in filter(lambda x: "szz" in x.keys(), data)}
        return super().pre_load(data, **kwargs)

    def post_dump(self, data, **kwargs):
        data = super().post_dump(data, **kwargs)

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


@dataclass(base_schema=FinalizeHook(_GPAQueryParamsExtSchema))
class GPAQueryParams(Result):
    """
    A model which describes GPA query parameters. Used when performing gpa queries (pysjtu.Client().query_gpa(...)).
    You may leave fields empty if you don't want to filter by them.

    :param start_term: begin term of the query.
    :param end_term: end term of the query.
    :param condition_logic: logic applied between `has_roll`, `registered` and `attending`.
    :param makeup_as_60: treat makeup scores (P) as 60.
    :param rebuild_as_60: treat rebuild scores (P) as 60.
    :param gp_round: round gp to a given precision in decimal digits.
    :param gpa_round: round gpa to a given precision in decimal digits.
    :param exclude_gp: exclude courses matching given criteria when calculating gp.
    :param exclude_gpa: exclude courses matching given criteria when calculating gpa.
    :param course_whole: unknown parameter. (统计全程的课程)
    :param course_range: courses taken into account when ranking
    :param excluded_courses: ids of courses excluded from statistics.
    :param excluded_course_groups: ids of course groups excluded from statistics.
    :param included_course_groups: ids of course groups included in statistics.
    :param dedup_method: which score to take if a student has taken a course multiple times.
    :param ranking: student range upon which to rank
    :param has_roll: only include students who are enrolled in school.
    :param registered: only include students who are registered.
    :param attending: only include students who are attending school now.
    """
    start_term: Optional[int] = mfield(dump_key="qsXnxq", load_default=None)
    end_term: Optional[int] = mfield(dump_key="zzXnxq", load_default=None)
    condition_logic: LogicEnum = mfield(dump_key="tjgx", load_default=LogicEnum.AND, by_value=True)
    makeup_as_60: WithField(bool, field=_MakeupAsPass) = mfield(load_default=False)
    rebuild_as_60: WithField(bool, field=_RebuildAsPass) = mfield(load_default=False)
    gp_round: int = mfield(required=True, load_key="cjblws", dump_key="sspjfblws")
    gpa_round: int = mfield(required=True, load_key="jdblws", dump_key="pjjdblws")
    exclude_gp: WithField(List[str], field=SplitField, sep=",") = mfield(required=True, data_key="bjjd")
    exclude_gpa: WithField(List[str], field=SplitField, sep=",") = mfield(required=True, data_key="bjpjf")
    course_whole: WithField(List[str], field=SplitField, sep=",") \
        = mfield(required=True, load_key="tjqckc", dump_key="kch_ids")
    course_range: CourseRange = mfield(dump_key="kcfw", load_default=CourseRange.CORE, by_value=True)
    excluded_courses: str = mfield(load_key="bcjkc", dump_key="bcjkc_id", load_default="")
    excluded_course_groups: str = mfield(load_key="bcjkz", dump_key="bcjkz_id", load_default="")
    included_course_groups: str = mfield(load_key="cjkz", dump_key="cjkz_id", load_default="")
    dedup_method: DedupMethod = mfield(required=True, data_key="cjxzm", by_value=True)
    ranking: Ranking = mfield(dump_key="tjfw", load_default=Ranking.GRADE_AND_FIELD, by_value=True)
    has_roll: WithField(bool, field=_HasRoll) = mfield(required=True, load_key="atjc", dump_key="xjzt")
    registered: WithField(bool, field=_Registered) = mfield(required=True, load_key="atjc", dump_key="zczt")
    attending: WithField(bool, field=_Attending) = mfield(required=True, load_key="atjc", dump_key="sfzx")

    class Meta:
        unknown = EXCLUDE

    def __repr__(self):
        return f"<GPAQueryParams {self.__dict__}>"


@dataclass
class GPA(Result):
    """
    A model which describes GP & GPA and rankings.

    :param total_score: summed score of all matched courses.
    :param course_count: number of all matched courses.
    :param fail_count: number of failed courses.
    :param total_credit: summed credit of all matched courses.
    :param acquired_credit: summed credit of passed courses.
    :param failed_credit: summed credit of failed courses.
    :param pass_rate: the pass rate of all matched courses.
    :param gp: summed gp of all matched courses.
    :param gp_ranking: ranking of the gp.
    :param gpa: gpa of all matched courses.
    :param gpa_ranking: ranking of the gpa.
    :param total_students: number of students participates in the ranking.
    """
    total_score: float = mfield(required=True, data_key="zf")
    course_count: int = mfield(required=True, data_key="ms")
    fail_count: int = mfield(required=True, data_key="bjgms")
    total_credit: float = mfield(required=True, data_key="zxf")
    acquired_credit: float = mfield(required=True, data_key="hdxf")
    failed_credit: float = mfield(required=True, data_key="bjgxf")
    pass_rate: WithField(float, _Percentage) = mfield(required=True, data_key="tgl")
    gp: float = mfield(required=True, data_key="xjf")
    gp_ranking: WithField(int, _RankingResult) = mfield(required=True, data_key="xjfpm")
    gpa: float = mfield(required=True, data_key="gpa")
    gpa_ranking: WithField(int, _RankingResult) = mfield(required=True, data_key="gpapm", load_only=True)
    total_students: WithField(int, _StudentCountFromRanking) = mfield(required=True, data_key="gpapm", load_only=True)

    class Meta:
        unknown = EXCLUDE

    def __repr__(self):
        return f"<GPA gp={self.gp} {self.gp_ranking}/{self.total_students} " \
               f"gpa={self.gpa} {self.gpa_ranking}/{self.total_students}>"
