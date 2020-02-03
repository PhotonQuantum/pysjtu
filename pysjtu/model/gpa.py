from enum import Enum
from typing import List

from pysjtu.model.base import Result


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
    :param exclude_credit: exclude courses matching given criteria when calculating gp.
    :param exclude_gp: exclude courses matching given criteria when calculating gpa.
    :param course_whole: unknown parameter.
    :param course_range: courses taken into account when ranking
    :param ranking: student range upon which to rank
    :param has_roll: only include students who are enrolled in school.
    :param registered: only include students who are registered.
    :param attending: only include students who are attending school now.
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

    _members = ["start_term", "end_term", "condition_logic", "makeup_as_60", "rebuild_as_60", "gp_round", "gpa_round",
                "exclude_gp", "exclude_gpa", "course_whole", "course_range", "ranking", "has_roll",
                "registered", "attending"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<GPAQueryParams {self.__dict__}>"


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

    _members = ["total_score", "course_count", "fail_count", "total_credit", "acquired_credit", "failed_credit",
                "pass_rate", "gp", "gp_ranking", "gpa", "gpa_ranking", "total_students"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<GPA gp={self.gp} {self.gp_ranking}/{self.total_students} " \
               f"gpa={self.gpa} {self.gpa_ranking}/{self.total_students}>"
