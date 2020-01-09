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
    name: str = None
    day: int = None
    week: list = None
    time: range = None
    location: str = None
    credit: int = None
    assessment: str = None
    remark: str = None
    teacher: list = None
    meta: list = None
    class_hour: list = None
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
    def load(self, data: dict):
        pass
    def all(self) -> List[ScheduleCourse]:
        pass
    def filter(self, **param) -> List[ScheduleCourse]:
        pass
