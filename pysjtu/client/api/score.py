import time
from functools import partial
from typing import List

from pysjtu import consts
from pysjtu import models
from pysjtu import schemas
from pysjtu.client.base import BaseClient


class ScoreMixin(BaseClient):
    def __init__(self):
        super().__init__()

    def _get_score_detail(self, year: int, term: int, class_id: str, **kwargs) -> List[models.ScoreFactor]:
        raw = self._session.post(consts.SCORE_DETAIL_URL + str(self.student_id),
                                 data={"xnm": year, "xqm": consts.TERMS[term], "jxb_id": class_id, "_search": False,
                                       "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                       "queryModel.currentPage": 1, "queryModel.sortName": "",
                                       "queryModel.sortOrder": "asc", "time": 1}, **kwargs)
        factors = schemas.ScoreFactorSchema(many=True).load(raw.json()["items"][:-1])  # type: ignore
        return factors

    def score(self, year: int, term: int, **kwargs) -> models.Results[models.Score]:
        """
        Fetch your scores of specific year & term.

        :param year: year for the new :class:`Scores` object.
        :param term: term for the new :class:`Scores` object.
        :return: A new :class:`Scores` object.
        :rtype: :class:`Scores`
        """
        raw = self._session.post(consts.SCORE_URL,
                                 data={"xnm": year, "xqm": consts.TERMS[term], "_search": False,
                                       "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                       "queryModel.currentPage": 1, "queryModel.sortName": "",
                                       "queryModel.sortOrder": "asc", "time": 1}, **kwargs)
        scores = models.Scores(year, term, partial(self._get_score_detail, **kwargs))
        scores.load(raw.json()["items"])  # type: ignore
        return scores
