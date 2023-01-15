import time
from functools import partial
from typing import List

from pysjtu import consts
from pysjtu import models
from pysjtu.client.base import BaseClient
from pysjtu.models import Scores


class ScoreMixin(BaseClient):
    def __init__(self):
        super().__init__()

    def _get_score_detail(self, year: int, term: int, class_id: str, **kwargs) -> List[models.ScoreFactor]:
        raw = self._session.post(consts.SCORE_DETAIL_URL + str(self.student_id),
                                 data={"xnm": year, "xqm": consts.TERMS[term], "jxb_id": class_id, "_search": False,
                                       "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                       "queryModel.currentPage": 1, "queryModel.sortName": "",
                                       "queryModel.sortOrder": "asc", "time": 1}, **kwargs)
        factors = models.ScoreFactor.Schema(many=True).load(raw.json()["items"][:-1])  # type: ignore
        return factors

    def score(self, year: int, term: int, **kwargs) -> Scores:
        """
        Fetch your scores of specific year & term.

        See :meth:`pysjtu.session.Session.post` for more information about the keyword arguments.

        :param year: query year
        :param term: query term
        """
        raw = self._session.post(consts.SCORE_URL,
                                 data={"xnm": year, "xqm": consts.TERMS[term], "_search": False,
                                       "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                       "queryModel.currentPage": 1, "queryModel.sortName": "",
                                       "queryModel.sortOrder": "asc", "time": 1}, **kwargs)
        scores = models.Scores(year, term, partial(self._get_score_detail, **kwargs))
        scores.load(raw.json()["items"])  # type: ignore
        return scores
