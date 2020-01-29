import datetime
from enum import Enum
from typing import List, Callable, Union, Tuple, Generator, Type
from marshmallow import Schema


class LogicEnum(Enum):
    AND = 0
    OR = 1


class CourseRange(Enum):
    ALL = 0
    CORE = 1


class Ranking(Enum):
    GRADE_AND_FIELD = 0


class QueryResult:
    _ref: Callable
    _post_ref: Callable
    _query_params: dict
    _length: int
    _cache: list
    _cached_items: set
    _page_size: int

    def __init__(self, method_ref: Callable, post_ref: Callable, query_params: dict, page_size: int = 15):
        pass

    def __getitem__(self, arg: Union[int, slice]) -> LibCourse:  # for now
        pass

    def _handle_result_by_index(self, idx: int) -> list:
        pass

    def _handle_result_by_idx_slice(self, idx: slice) -> list:
        pass

    @property
    def __len__(self) -> int:
        pass

    def flush_cache(self):
        pass

    def _update_cache(self, start: int, end: int):
        pass

    def _fetch_range(self, page: int, count: int) -> Tuple[int, int]:
        pass

    def _query(self, page: int, count: int) -> dict:
        pass

    def __iter__(self) -> Generator:
        pass


class Result:
    _members: list
    def __init__(self, **kwargs):
        pass
    def __repr__(self):
        pass


class Results:
    _schema: Type[Schema]
    _result_model: Type[Result]
    _results: list
    year: int
    term: int

    def __init__(self, year: int = 0, term: int = 0):
        pass

    def load(self, data: dict):
        pass

    def all(self):
        pass

    def filter(self, **param):
        pass


class GPAQueryParams(Result):
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


class GPA(Result):
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


class LibCourse(Result):
    name: str
    day: int
    week: list
    time: range
    location: str
    locations: List[str]
    faculty: str
    credit: float
    teacher: List[str]
    course_id: str
    class_name: str
    class_id: str
    class_composition: List[str]
    hour_total: int
    hour_remark: dict
    seats: int
    students_elected: int
    students_planned: int


class Exam(Result):
    name: str
    location: str
    course_id: str
    course_name: str
    class_name: str
    rebuild: bool
    credit: float
    self_study: bool
    date: datetime.date
    time: List[datetime.time]


class ScoreFactor(Result):
    name: str
    percentage: float
    score: float


class Score(Result):
    name: str
    teacher: str
    score: str
    credit: float
    gp: float
    invalid: bool
    course_type: str
    category: str
    score_type: str
    method: str
    course_id: str
    class_name: str
    class_id: str
    detail: List[ScoreFactor]
    year: int
    term: int


class ScheduleCourse(Result):
    name: str
    day: int
    week: list
    time: range
    location: str
    credit: int
    assessment: str
    remark: str
    teacher_name: List[str]
    teacher_title: List[str]
    course_id: str
    class_name: str
    class_id: str
    hour_total: int
    hour_remark: dict
    hour_week: int
    field: str


class Exams(Results):
    def all(self) -> List[Exam]:
        pass

    def filter(self, **param) -> List[Exam]:
        pass


# noinspection PyMissingConstructor
class Scores(Results):
    _func_detail: Callable

    def __init__(self, year: int = 0, term: int = 0, func_detail: Callable = None):
        pass

    def all(self) -> List[Score]:
        pass

    def filter(self, **param) -> List[Score]:
        pass


class Schedule(Results):
    def all(self) -> List[ScheduleCourse]:
        pass

    def filter(self, **param) -> List[ScheduleCourse]:
        pass
