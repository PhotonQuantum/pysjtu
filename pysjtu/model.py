from .util import overlap


class ScoreFactor:
    def __init__(self, **kwargs):
        self.name = None
        self.percentage = 0.0
        self.score = 0.0
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"<ScoreFactor {self.name}({self.percentage * 100}%)={self.score}>"


class Score:
    _members = ["name", "teacher", "score", "credit", "gp", "invalid", "course_type", "category", "score_type",
                "method", "course_id", "class_name", "class_id"]

    def __init__(self, **kwargs):
        for member in self._members:
            setattr(self, member, None)
        self.__dict__.update(kwargs)
        self._detail = None
        self.year = None
        self.term = None
        self._func_detail = None

    def __repr__(self):
        return f"<Score {self.name} score={self.score} credit={self.credit} gp={self.gp}>"

    @property
    def detail(self):
        if not self._detail:
            self._detail = self._func_detail(self.year, self.term, self.class_id)
        return self._detail


class Scores:
    def __init__(self, year=None, term=None, func_detail=None):
        self._scores = []
        self.year = year
        self.term = term
        self._func_detail = func_detail

    def load(self, data):
        schema = ScoreSchema(many=True)
        self._scores = schema.load(data)
        for item in self._scores:
            item.year = self.year
            item.term = self.term
            item._func_detail = self._func_detail

    def all(self):
        return self._scores

    def filter(self, **param):
        rtn = self._scores
        for (k, v) in param.items():
            if not hasattr(Score(), k):
                raise KeyError("Invalid criteria!")
            rtn = list(filter(lambda x: getattr(x, k) == v, rtn))
        return rtn


class ScheduleCourse:
    _members = ["name", "day", "week", "time", "location", "credit", "assessment", "remark", "teacher", "meta",
                "class_hour"]

    def __init__(self, **kwargs):
        for member in self._members:
            setattr(self, member, None)
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"<ScheduleCourse name={self.name} week={self.week} day={self.day} time={self.time}>"


class Schedule:
    _courses = []

    def load(self, data):
        schema = CourseSchema(many=True)
        self._courses = schema.load(data)

    def all(self):
        return self._courses

    def filter(self, **param):
        rtn = self._courses
        for (k, v) in param.items():
            if not hasattr(ScheduleCourse(), k):
                raise KeyError("Invalid criteria!")
            if k in ("week", "time", "day"):
                rtn = list(filter(lambda x: overlap(getattr(x, k), v), rtn))
            else:
                rtn = list(filter(lambda x: getattr(x, k) == v, rtn))
        return rtn


from .schema import *
