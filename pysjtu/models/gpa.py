from dataclasses import dataclass
from enum import Enum
from typing import List

from pysjtu.models.base import Result


class LogicEnum(Enum):
    """ Used by :class:`GPAQueryParams` to specify condition logic. """
    AND = 0
    OR = 1


class CourseRange(Enum):
    """ Used by :class:`GPAQueryParams` to specify courses taken into account when ranking """
    ALL = "qbkc"
    CORE = "hxkc"


class Ranking(Enum):
    """ Used by :class:`GPAQueryParams` to specify student range upon which to rank """
    GRADE_AND_FIELD = "njzy"


@dataclass
class GPAQueryParams(Result):
    """
    A model which describes GPA query parameters. Used when performing gpa queries (pysjtu.Client().query_gpa(...)).
    You may leave fields empty if you don't want to filter by them.

    :param start_term: begin term of the query.
    :type start_term: int
    :param end_term: end term of the query.
    :type end_term: int
    :param condition_logic: logic applied between `has_roll`, `registered` and `attending`.
    :type condition_logic: :class:`LogicEnum`
    :param makeup_as_60: treat makeup scores (P) as 60.
    :type makeup_as_60: bool
    :param rebuild_as_60: treat rebuild scores (P) as 60.
    :type rebuild_as_60: bool
    :param gp_round: round gp to a given precision in decimal digits.
    :type gp_round: int
    :param gpa_round: round gpa to a given precision in decimal digits.
    :type gpa_round: int
    :param exclude_gp: exclude courses matching given criteria when calculating gp.
    :type exclude_gp: str
    :param exclude_gpa: exclude courses matching given criteria when calculating gpa.
    :type exclude_gpa: str
    :param course_whole: unknown parameter.
    :type course_whole: List[str]
    :param course_range: courses taken into account when ranking
    :type course_range: :class:`CourseRange`
    :param ranking: student range upon which to rank
    :type ranking: :class:`Ranking`
    :param has_roll: only include students who are enrolled in school.
    :type has_roll: bool
    :param registered: only include students who are registered.
    :type registered: bool
    :param attending: only include students who are attending school now.
    :type attending: bool
    """
    start_term: int
    end_term: int
    condition_logic: LogicEnum
    makeup_as_60: bool
    rebuild_as_60: bool
    gp_round: int
    gpa_round: int
    exclude_gp: str
    exclude_gpa: str
    course_whole: List[str]
    course_range: CourseRange
    ranking: Ranking
    has_roll: bool
    registered: bool
    attending: bool

    def __repr__(self):
        return f"<GPAQueryParams {self.__dict__}>"


@dataclass
class GPA(Result):
    """
    A model which describes GP & GPA and rankings.

    :param total_score: summed score of all matched courses.
    :type total_score: int
    :param course_count: number of all matched courses.
    :type course_count: int
    :param fail_count: number of failed courses.
    :type fail_count: int
    :param total_credit: summed credit of all matched courses.
    :type total_credit: float
    :param acquired_credit: summed credit of passed courses.
    :type acquired_credit: float
    :param failed_credit: summed credit of failed courses.
    :type failed_credit: float
    :param pass_rate: the pass rate of all matched courses.
    :type pass_rate: float
    :param gp: summed gp of all matched courses.
    :type gp: float
    :param gp_ranking: ranking of the gp.
    :type gp_ranking: int
    :param gpa: gpa of all matched courses.
    :type gpa: float
    :param gpa_ranking: ranking of the gpa.
    :type gpa_ranking: int
    :param total_students: number of students participates in the ranking.
    :type total_students: int
    """
    total_score: int
    course_count: int
    fail_count: int
    total_credit: float
    acquired_credit: float
    failed_credit: float
    pass_rate: float
    gp: float
    gp_ranking: int
    gpa: float
    gpa_ranking: int
    total_students: int

    def __repr__(self):
        return f"<GPA gp={self.gp} {self.gp_ranking}/{self.total_students} " \
               f"gpa={self.gpa} {self.gpa_ranking}/{self.total_students}>"
