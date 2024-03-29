from typing import Callable, List, Optional, Any, Mapping

from marshmallow import fields, EXCLUDE
from marshmallow_dataclass import dataclass

from pysjtu.fields import ChineseBool
from pysjtu.models.base import Result, Results
from pysjtu.schema import FinalizeHook, LoadDumpSchema, WithField, mfield


class _ScoreFactorName(fields.Field):
    def _deserialize(
            self,
            value: Any,
            attr: Optional[str],
            data: Optional[Mapping[str, Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return value[:value.find("(")]


class _ScoreFactorPercentage(fields.Field):
    def _deserialize(
            self,
            value: Any,
            attr: Optional[str],
            data: Optional[Mapping[str, Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return float(value[value.find("(") + 1:value.find("%")]) / 100


@dataclass(base_schema=FinalizeHook(LoadDumpSchema))
class ScoreFactor(Result):
    """
    A model which describes detailed composition of a course's score.

    :param name: item name
    :param percentage: item factor
    :param score: item score
    """
    name: WithField(str, field=_ScoreFactorName) = mfield(required=True, data_key="xmblmc")
    percentage: WithField(float, field=_ScoreFactorPercentage) \
        = mfield(required=True, data_key="xmblmc", load_only=True)
    score: str = mfield(required=True, data_key="xmcj")

    class Meta:
        unknown = EXCLUDE

    def __repr__(self):
        return f"<ScoreFactor {self.name}({self.percentage * 100}%)={self.score}>"


@dataclass(base_schema=FinalizeHook(LoadDumpSchema))
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
    name: str = mfield(required=True, data_key="kcmc")
    teacher: str = mfield(data_key="jsxm")
    score: str = mfield(required=True, data_key="cj")
    credit: float = mfield(required=True, data_key="xf")
    gp: float = mfield(required=True, data_key="jd")
    invalid: WithField(Optional[bool], field=ChineseBool) = mfield(None, data_key="cjsfzf")
    course_type: Optional[str] = mfield(None, data_key="kcbj")
    category: Optional[str] = mfield(None, data_key="kclbmc")
    score_type: Optional[str] = mfield(None, data_key="ksxz")
    method: Optional[str] = mfield(None, data_key="khfsmc")
    course_id: Optional[str] = mfield(None, data_key="kch_id")
    class_name: Optional[str] = mfield(None, data_key="jxbmc")
    class_id: Optional[str] = mfield(None, data_key="jxb_id")
    year: int = mfield(0, raw=True)
    term: int = mfield(0, raw=True)
    _detail: List[ScoreFactor] = mfield(None, raw=True)
    _func_detail: Callable = mfield(None, raw=True)

    class Meta:
        unknown = EXCLUDE
        exclude = ["year", "term", "_detail", "_func_detail"]

    def __repr__(self):
        return f"<Score {self.name} score={self.score} credit={self.credit} gp={self.gp}>"

    @property
    def detail(self) -> List[ScoreFactor]:
        if not self._detail:
            self._detail = self._func_detail(self.year, self.term, self.class_id)
        return self._detail


class Scores(Results[Score]):
    """
    A list-like interface to Score collections.

    This class is a subclass of :class:`pysjtu.models.base.Results`.
    """
    _item = Score

    def __init__(self, year: int = 0, term: int = 0, func_detail: Callable[[int, int, str], List[ScoreFactor]] = None):
        super().__init__(year, term)
        self._func_detail = func_detail

    def load(self, data: dict):
        """
        Load a list of dicts into Scores, and deserialize dicts to Score objects.

        :param data: a list of dicts contains scores.
        :meta private:
        """
        super().load(data)
        for item in self:
            item.year = self.year
            item.term = self.term
            # noinspection PyTypeHints
            item._func_detail = self._func_detail  # type: ignore
