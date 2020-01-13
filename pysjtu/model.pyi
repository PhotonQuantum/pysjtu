from typing import List
import datetime

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
