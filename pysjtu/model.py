from enum import Enum

from .util import overlap, range_in_set


class LogicEnum(Enum):
    AND = 0
    OR = 1


class CourseRange(Enum):
    ALL = "qbkc"
    CORE = "hxkc"


class Ranking(Enum):
    GRADE_AND_FIELD = "njzy"


class QueryResult:
    def __init__(self, method_ref, post_ref, query_params, page_size=15):
        self._ref = method_ref
        self._post_ref = post_ref
        self._query_params = query_params
        self._length = None
        self._cache = [None] * len(self)
        self._cached_items = set()
        self._page_size = page_size

    def __getitem__(self, arg):
        data = None
        if isinstance(arg, int):
            data = self._handle_result_by_index(arg)
        elif isinstance(arg, slice):
            if arg.start is None and arg.stop is None:
                data = self._handle_result_by_idx_slice(slice(0, -1))
            else:
                data = self._handle_result_by_idx_slice(arg)
        if data is None:
            raise KeyError
        data = self._post_ref(data)
        return data

    def _handle_result_by_index(self, idx):
        idx = len(self) + idx if idx < 0 else idx
        self._update_cache(idx, idx)
        return self._cache[idx]

    def _handle_result_by_idx_slice(self, idx):
        if idx.start is None:
            start = 0
        elif idx.start < 0:
            start = len(self) + idx.start
        else:
            start = idx.start

        if idx.stop is None:
            end = 0
        elif idx.stop < 0:
            end = len(self) + idx.stop
        else:
            end = idx.stop

        self._update_cache(start, end)
        return self._cache[idx]

    def __len__(self):
        if not self._length:
            rtn = self._query(1, 1)
            self._length = rtn["totalResult"]
        return self._length

    def flush_cache(self):
        self._length = None
        self._cache = [None] * len(self)
        self._cached_items = set()

    def _update_cache(self, start, end):
        fetch_set = set(set(range(start, end + 1)) - self._cached_items)
        while len(fetch_set) != 0:
            fetch_range = next(range_in_set(fetch_set))
            page = int(fetch_range.start / self._page_size) + 1
            self._cached_items.update(range(*self._fetch_range(page, self._page_size)))
            fetch_set = set(set(range(start, end + 1)) - self._cached_items)

    def _fetch_range(self, page, count):
        rtn = self._query(page, count)["items"]
        for item in zip(range(count * (page - 1), count * (page - 1) + len(rtn)), rtn):
            self._cache[item[0]] = item[1]
        return count * (page - 1), count * (page - 1) + len(rtn)

    def _query(self, page, count):
        new_params = self._query_params
        new_params["queryModel.showCount"] = count
        new_params["queryModel.currentPage"] = page
        return self._ref(data=new_params).json()

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]


class GPAQueryParams:
    _members = ["start_term", "end_term", "condition_logic", "makeup_as_60", "rebuild_as_60", "gp_round", "gpa_round",
                "exclude_credit", "exclude_gp", "course_whole", "course_range", "ranking", "has_roll",
                "registered", "attending"]

    def __init__(self, **kwargs):
        for member in self._members:
            setattr(self, member, None)
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"<GPAQueryParams {self.__dict__}>"


class GPA:
    _members = ["total_score", "course_count", "fail_count", "total_credit", "acquired_credit", "failed_credit",
                "pass_rate", "gp", "gp_ranking", "gpa", "gpa_ranking", "total_students"]

    def __init__(self, **kwargs):
        for member in self._members:
            setattr(self, member, None)
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"<GPA gp={self.gp} {self.gp_ranking}/{self.total_students} gpa={self.gpa} {self.gpa_ranking}/{self.total_students}>"


class LibCourse:
    _members = ["name", "day", "week", "time", "location", "locations", "faculty", "credit", "teacher_name",
                "teacher_title", "course_id", "class_name", "class_id", "class_composition", "hour_total",
                "hour_remark", "seats", "students_elected", "students_planned"]

    def __init__(self, **kwargs):
        for member in self._members:
            setattr(self, member, None)
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"<LibCourse {self.name} class_name={self.class_name}>"


class Exam:
    _members = ["name", "location", "course_id", "course_name", "class_name", "rebuild", "credit", "self_study",
                "date", "time"]

    def __init__(self, **kwargs):
        for member in self._members:
            setattr(self, member, None)
        self.__dict__.update(kwargs)

    def __repr__(self):
        time_out = [time.strftime("%H:%M") for time in self.time]
        return f"<Exam \"{self.name}\" location={self.location} datetime={self.date}({time_out[0]}-{time_out[1]})>"


class Exams:
    def __init__(self, year=None, term=None):
        self._exams = []
        self.year = year
        self.term = term

    def load(self, data):
        schema = ExamSchema(many=True)
        self._exams = schema.load(data)

    def all(self):
        return self._exams

    def filter(self, **param):
        rtn = self._exams
        for (k, v) in param.items():
            if not hasattr(Exam(), k):
                raise KeyError("Invalid criteria!")
            rtn = list(filter(lambda x: getattr(x, k) == v, rtn))
        return rtn


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
    _members = ["name", "day", "week", "time", "location", "credit", "assessment", "remark", "teacher_name",
                "teacher_title", "course_id", "class_name", "class_id", "hour_total", "hour_remark", "hour_week",
                "field"]

    def __init__(self, **kwargs):
        for member in self._members:
            setattr(self, member, None)
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"<ScheduleCourse {self.name} week={self.week} day={self.day} time={self.time}>"


class Schedule:

    def __init__(self, year=None, term=None):
        self._courses = []
        self.year = year
        self.term = term

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
