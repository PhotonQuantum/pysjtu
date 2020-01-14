from typing import List, Callable, Union, Tuple, Generator
import datetime


class QueryResult:
    _ref: Callable
    _post_ref: Callable
    _query_params: dict
    _length: int
    _cache: dict
    _cached_items: set
    _page_size: int

    def __init__(self, method_ref: Callable, post_ref: Callable, query_params: dict, page_size: int=15):
        pass

    def __getitem__(self, arg: Union[int, slice]) -> LibCourse: # for now
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
class Exam:
    name: str
    location: str
    course_id: str
    course_name: str
    class_name: str
    rebuild: bool
    credit: float
    self_study: bool
    date: datetime.date
    time: datetime.time


class ScoreFactor:
    name: str
    percentage: float
    score: float


class Score:
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


class ScheduleCourse:
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
    hour_remark: str
    hour_week: int
    field: str


class Exams:
    year: int
    term: int

    def load(self, data: dict):
        pass

    def all(self) -> List[Exam]:
        pass

    def filter(self, **param) -> List[Exam]:
        pass


class Scores:
    year: int
    term: int

    def load(self, data: dict):
        pass

    def all(self) -> List[Score]:
        pass

    def filter(self, **param) -> List[Score]:
        pass


class Schedule:
    year: int
    term: int

    def load(self, data: dict):
        pass

    def all(self) -> List[ScheduleCourse]:
        pass

    def filter(self, **param) -> List[ScheduleCourse]:
        pass
