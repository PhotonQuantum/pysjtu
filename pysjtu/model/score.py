from typing import Callable, List

from pysjtu.model.base import Result, Results


class ScoreFactor(Result):
    """
    A model which describes detailed composition of a course's score.

    :param name: item name
    :param percentage: item factor
    :param score: item score
    """
    name: str
    percentage: float
    score: float

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
    year: int
    term: int

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
    def detail(self) -> List[ScoreFactor]:
        if not self._detail:
            self._detail = self._func_detail(self.year, self.term, self.class_id)
        return self._detail


from pysjtu.schema.score import ScoreSchema


class Scores(Results[Score]):
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

    def __init__(self, year: int = 0, term: int = 0, func_detail: Callable = None):
        super().__init__(year, term)
        self._func_detail = func_detail

    def load(self, data: dict):
        """
        Load a list of dicts into Scores, and deserialize dicts to Score objects.

        :param data: a list of dicts contains scores.
        """
        super().load(data)
        for item in self:
            item.year = self.year
            item.term = self.term
            item._func_detail = self._func_detail
