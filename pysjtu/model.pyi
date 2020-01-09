from typing import List

class ScoreFactor:
    name: str
    percentage: float
    score: float

class Score:
    name: str
    teacher: str
    score: int
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
