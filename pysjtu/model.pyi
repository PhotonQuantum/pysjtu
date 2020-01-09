from typing import List
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

class Schedule:
    def load(self, data: dict):
        pass
    def all(self) -> List[ScheduleCourse]:
        pass
    def filter(self, **param) -> List[ScheduleCourse]:
        pass
