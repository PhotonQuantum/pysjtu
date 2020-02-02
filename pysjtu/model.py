import time
from enum import Enum

from .utils import overlap, range_in_set, parse_slice


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


class QueryResult:
    """
    A key accessible, sliceable, and iterable interface to query result collections.
    A QueryResult object is constructed with a raw data callable reference.
    A QueryResult object is returned by a query operation, and isn't meant to be constructed by a user.
    A QueryResult object is lazy, which means network I/Os won't be performed until items are actually accessed.

    Usage::

        >>> query = ... # something that returns a QueryResult, for example pysjtu.Client().query_courses(...)
        >>> len(query)
        90
        >>> query[-1]
        <LibCourse 高等数学I class_name=(2019-2020-1)-MA248-20>
        >>> query[14:16]
        [<LibCourse 高等数学III class_name=(2019-2020-1)-MA172-1>, <LibCourse 高等数学IV class_name=(2019-2020-1)-MA173-1>]
        >>> list(query)
        [<LibCourse 高等数学A1 class_name=(2019-2020-1)-VV156-1>, <LibCourse 高等数学B1 class_name=(2019-2020-1)-VV186-1>, ...]
    """

    def __init__(self, method_ref, post_ref, query_params, page_size=15):
        self._ref = method_ref
        self._post_ref = post_ref
        self._query_params = query_params
        self._length = 0
        self._cache = [None] * len(self)
        self._cached_items = set()
        self._page_size = page_size

    def __getitem__(self, arg):
        data = None
        if isinstance(arg, int):
            data = self._handle_result_by_index(arg)
        elif isinstance(arg, slice):
            data = self._handle_result_by_idx_slice(arg)
        if data is None:
            raise TypeError("QueryResult indices must be integers or slices, not " + type(arg).__name__)
        data = self._post_ref(data)
        return data

    def _handle_result_by_index(self, idx):
        idx = len(self) + idx if idx < 0 else idx
        if idx >= len(self) or idx < 0:
            raise IndexError("index out of range")
        self._update_cache(idx, idx + 1)
        return self._cache[idx]

    def _handle_result_by_idx_slice(self, idx):
        idx_start = parse_slice(idx.start)
        idx_stop = parse_slice(idx.stop)

        if idx_start is None:
            start = 0
        elif idx_start < 0:
            start = len(self) + idx.start
        else:
            start = idx.start

        if idx_stop is None:
            end = len(self) - 1
        elif idx_stop < 0:
            end = len(self) + idx.stop - 1
        else:
            end = idx.stop

        if end > len(self):
            end = len(self)
        if start >= end:
            return []
        self._update_cache(start, end)
        return self._cache[idx]

    def __len__(self):
        if not self._length:
            rtn = self._query(1, 1)
            self._length = rtn["totalResult"]
        return self._length

    def flush_cache(self):
        """
        Flush caches. Local caches are dropped and data will be fetched from remote.
        """
        self._length = 0
        self._cache = [None] * len(self)
        self._cached_items = set()

    def _update_cache(self, start, end):
        fetch_set = set(set(range(start, end)) - self._cached_items)
        while len(fetch_set) != 0:
            fetch_range = next(range_in_set(fetch_set))
            page = int(fetch_range.start / self._page_size) + 1
            self._cached_items.update(range(*self._fetch_range(page, self._page_size)))
            fetch_set = set(set(range(start, end)) - self._cached_items)

    def _fetch_range(self, page, count):
        rtn = self._query(page, count)["items"]
        for item in zip(range(count * (page - 1), count * (page - 1) + len(rtn)), rtn):
            self._cache[item[0]] = item[1]
        return count * (page - 1), count * (page - 1) + len(rtn)

    def _query(self, page, count):
        new_params = self._query_params
        new_params["queryModel.showCount"] = count
        new_params["queryModel.currentPage"] = page
        new_params["queryModel.sortName"] = ""
        new_params["queryModel.sortOrder"] = "asc"
        new_params["nd"] = int(time.time() * 1000)
        new_params["_search"] = False
        return self._ref(data=new_params).json()

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]


class Result:
    """ Base class for Result """
    _members = []

    def __init__(self, **kwargs):
        for member in self._members:
            setattr(self, member, kwargs.pop(member, None))
        if len(kwargs) != 0:
            raise TypeError(f"__init__() got an unexpected keyword argument '{list(kwargs.keys())[0]}'")

    def __repr__(self):
        raise NotImplementedError  # pragma: no cover


class Results(list):
    """ Base class for Results """
    _schema = None
    _result_model = None

    def __init__(self, year=0, term=0):
        super().__init__()
        self.year = year
        self.term = term

    def load(self, data):
        """
        Load a list of dicts into Results, and deserialize dicts to Result objects.

        :param data: a list of dicts.
        """
        schema = self._schema(many=True)
        results = schema.load(data)
        for result in results:
            super().append(result)

    def filter(self, **param):
        """
        Get Result objects matching specific criteria.

        :param param: query criteria
        :return: Result objects matching given criteria.
        """
        rtn = self
        for (k, v) in param.items():
            if not hasattr(self._result_model(), k):
                raise KeyError("Invalid criteria!")
            if k in ("week", "time", "day"):
                rtn = list(filter(lambda x: overlap(getattr(x, k), v), rtn))
            else:
                rtn = list(filter(lambda x: getattr(x, k) == v, rtn))
        return rtn


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
    _members = ["total_score", "course_count", "fail_count", "total_credit", "acquired_credit", "failed_credit",
                "pass_rate", "gp", "gp_ranking", "gpa", "gpa_ranking", "total_students"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<GPA gp={self.gp} {self.gp_ranking}/{self.total_students} " \
               f"gpa={self.gpa} {self.gpa_ranking}/{self.total_students}>"


class LibCourse(Result):
    """
    A model which describes a course in CourseLib. Some fields may be empty.

    :param name: literal name of the course.
    :param day: in which day(s) of weeks classes are given.
    :param week: in which week(s) classes are given.
    :param time: at which time of days classes are given.
    :param location: the place where classes are given.
    :param locations: the places where classes are given.
    :param faculty: the faculty which offers this course.
    :param credit: credits that the course provides.
    :param teacher: the teacher who offers this course.
    :param course_id: course id.
    :param class_name: class name (constant between years).
    :param class_id: class id (variable between years).
    :param class_composition: students from which faculties do the course consists of.
    :param hour_total: credit hours of the course.
    :param hour_remark: detailed explanation of the credit hours.
    :param seats: number of seats available in this course.
    :param students_elected: number of students elected this course.
    :param students_planned: number of students planned when setting this course.
    """
    _members = ["name", "day", "week", "time", "location", "locations", "faculty", "credit", "teacher",
                "course_id", "class_name", "class_id", "class_composition", "hour_total",
                "hour_remark", "seats", "students_elected", "students_planned"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<LibCourse {self.name} class_name={self.class_name}>"


class Exam(Result):
    """
    A model which describes an exam. Some fields may be empty.

    :param name: name of the course on which you are being examined.
    :param location: the place where this exam is held.
    :param seat: seat number
    :param course_id: course id of the course on which you are being examined.
    :param course_name: course name of the course on which you are being examined.
    :param class_name: class name of the class you are attending on the course which are being examined.
    :param rebuild: whether this exam is a rebuild test.
    :param credit: credits that the course provides.
    :param self_study: whether this course is a self study course.
    :param date: date of the exam
    :param time: time range of the exam
    """
    _members = ["name", "location", "seat", "course_id", "course_name", "class_name", "rebuild", "credit", "self_study",
                "date", "time"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        date_out = self.date.strftime("%Y-%m-%d")
        time_out = [time.strftime("%H:%M") for time in self.time]
        return f"<Exam \"{self.name}\" location={self.location} datetime={date_out}({time_out[0]}-{time_out[1]})>"


class ScoreFactor(Result):
    """
    A model which describes detailed composition of a course's score.

    :param name: item name
    :param percentage: item factor
    :param score: item score
    """
    _members = ["name", "percentage", "score"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<ScoreFactor {self.name}({self.percentage * 100}%)={self.score}>"


class Score(Result):
    """
    A model which describes the score of a specific course. Some fields may be empty.

    :param name: literal name of the course.
    :param teacher: the teacher who offers this course.
    :param score: score of this course
    :param credit: credits that the course provides.
    :param gp: gp earned in this course.
    :param invalid: whether this score is voided.
    :param detail: a ScoreFactor object representing detailed composition of the score.
    :param course_type: type of this course. (compulsory, elective, etc)
    :param category: category of this course. (specialized, general, PE, etc)
    :param score_type: type of your score. (acquired by normal examination, etc)
    :param method: assessment method of this course. (exams, assesses, etc)
    :param course_id: course id.
    :param class_name: class name (constant between years).
    :param class_id: class id (variable between years).
    """
    _members = ["name", "teacher", "score", "credit", "gp", "invalid", "course_type", "category", "score_type",
                "method", "course_id", "class_name", "class_id"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._detail = None
        self.year = 0
        self.term = 0
        self._func_detail = None

    def __repr__(self):
        return f"<Score {self.name} score={self.score} credit={self.credit} gp={self.gp}>"

    @property
    def detail(self):
        if not self._detail:
            self._detail = self._func_detail(self.year, self.term, self.class_id)
        return self._detail


class ScheduleCourse(Result):
    """
    A model which describes a course in CourseLib. Some fields may be empty.

    :param name: literal name of the course.
    :param day: in which day(s) of weeks classes are given.
    :param week: in which week(s) classes are given.
    :param time: at which time of days classes are given.
    :param location: the place where classes are given.
    :param credit: credits that the course provides.
    :param assessment: assessment method of this course. (exams, assesses, etc)
    :param remark: remarks of this course.
    :param teacher_name: the teacher who offers this course.
    :param teacher_title: title of the course's teacher.
    :param course_id: course id.
    :param class_name: class name (constant between years).
    :param class_id: class id (variable between years).
    :param hour_total: credit hours of the course.
    :param hour_remark: detailed explanation of the credit hours.
    :param hour_week: credit hours of the course every week.
    :param field: professional field of this course.
    """

    _members = ["name", "day", "week", "time", "location", "credit", "assessment", "remark", "teacher_name",
                "teacher_title", "course_id", "class_name", "class_id", "hour_total", "hour_remark", "hour_week",
                "field"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<ScheduleCourse {self.name} week={self.week} day={self.day} time={self.time}>"


from .schema import *


class Exams(Results):
    """
    A list-like interface to Exam collections.
    An additional filter method has been added to make filter operations easier.

    Usage::

        >>> exams = ... # something that returns a Exams, for example pysjtu.Client().exam(...)
        >>> exams
        [<Exam "2019-2020-1数学期中考" location=东上院509 datetime=2019-11-06(13:10-15:10)>, ...]
        >>> from datetime import date
        >>> exams.filter(date=date(2019, 12, 31))
        [<Exam "2019-2020-1一专期末考（2019级）" location=东上院509 datetime=2019-12-31(08:00-10:00)>]
    """
    _schema = ExamSchema
    _result_model = Exam


class Scores(Results):
    """
    A list-like interface to Score collections.
    An additional filter method has been added to make filter operations easier.

    Usage::

        >>> scores = ... # something that returns a Exams, for example pysjtu.Client().score(...)
        >>> scores
        [<Score 大学化学 score=xx credit=x.x gp=x.x>, ...>
        >>> scores.filter(gp=4)
        [<Score xxxxx score=91 credit=2.0 gp=4.0>, ...]
    """
    _schema = ScoreSchema
    _result_model = Score

    def __init__(self, year=0, term=0, func_detail=None):
        super().__init__(year, term)
        self._func_detail = func_detail

    def load(self, data):
        """
        Load a list of dicts into Scores, and deserialize dicts to Score objects.

        :param data: a list of dicts contains scores.
        """
        super().load(data)
        for item in self:
            item.year = self.year
            item.term = self.term
            item._func_detail = self._func_detail


class Schedule(Results):
    """
    A list-like interface to Schedule collections.
    An additional filter method has been added to make filter operations easier.

    Usage::

        >>> sched = ... # something that returns a Exams, for example pysjtu.Client().schedule(...)
        >>> sched
        [<ScheduleCourse 军事理论 week=[range(9, 17)] day=1 time=range(1, 3)>, ...]
        >>> sched.filter(time=[1, range(5, 7)], day=[2, range(4, 5)]))
        [<ScheduleCourse 线性代数 week=[range(1, 7), range(8, 17)] day=2 time=range(1, 3)>,
        <ScheduleCourse 线性代数 week=[7] day=2 time=range(1, 3)>,
        <ScheduleCourse 思想道德修养与法律基础 week=[range(1, 17)] day=2 time=range(6, 9)>,
        <ScheduleCourse 程序设计思想与方法（C++） week=[range(1, 16, 2)] day=4 time=range(1, 3)>]
    """
    _schema = ScheduleCourseSchema
    _result_model = ScheduleCourse
