from dataclasses import dataclass
from typing import Callable, List, Optional

from pysjtu.models.base import Result, Results


@dataclass
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

    def __repr__(self):
        return f"<ScoreFactor {self.name}({self.percentage * 100}%)={self.score}>"


@dataclass
class Score(Result):
    """
    A model which describes the score of a specific course. Some fields may be empty.

    :param name: literal name of the course.
    :type name: str
    :param teacher: the teacher who offers this course.
    :type teacher: str
    :param score: score of this course
    :type score: str
    :param credit: credits that the course provides.
    :type credit: float
    :param gp: gp earned in this course.
    :type gp: float
    :param invalid: whether this score is voided.
    :type invalid: bool
    :param detail: a ScoreFactor object representing detailed composition of the score.
    :type detail: List[:class:`ScoreFactor`]
    :param course_type: type of this course. (compulsory, elective, etc)
    :type course_type: str
    :param category: category of this course. (specialized, general, PE, etc)
    :type category: str
    :param score_type: type of your score. (acquired by normal examination, etc)
    :type score_type: str
    :param method: assessment method of this course. (exams, assesses, etc)
    :type method: str
    :param course_id: course id.
    :type course_id: str
    :param class_name: class name (constant between years).
    :type class_name: str
    :param class_id: class id (variable between years).
    :type class_id: str
    """
    name: str
    teacher: str
    score: str
    credit: float
    gp: float
    invalid: Optional[bool] = None
    course_type: Optional[str] = None
    category: Optional[str] = None
    score_type: Optional[str] = None
    method: Optional[str] = None
    course_id: Optional[str] = None
    class_name: Optional[str] = None
    class_id: Optional[str] = None
    year: int = 0
    term: int = 0
    _detail: List[ScoreFactor] = None
    _func_detail: Callable = None

    def __repr__(self):
        return f"<Score {self.name} score={self.score} credit={self.credit} gp={self.gp}>"

    @property
    def detail(self) -> List[ScoreFactor]:
        if not self._detail:
            self._detail = self._func_detail(self.year, self.term, self.class_id)
        return self._detail


from pysjtu.schemas.score import ScoreSchema


class Scores(Results[Score]):
    """
    A list-like interface to Score collections.
    An additional filter method has been added to make filter operations easier.
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
            # noinspection PyTypeHints
            item._func_detail = self._func_detail  # type: ignore
