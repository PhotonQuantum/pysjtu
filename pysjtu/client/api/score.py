import time
from functools import partial
from typing import List

from httpx.config import (
    UNSET,
    TimeoutTypes
)

from pysjtu import const
from pysjtu import model
from pysjtu import schema
from pysjtu.client.base import BaseClient


class ScoreMixin(BaseClient):
    def _get_score_detail(self, year: int, term: int, class_id: str, timeout: TimeoutTypes = UNSET) -> List[
        model.ScoreFactor]:
        raw = self._session.post(const.SCORE_DETAIL_URL + str(self.student_id),
                                 data={"xnm": year, "xqm": const.TERMS[term], "jxb_id": class_id, "_search": False,
                                       "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                       "queryModel.currentPage": 1, "queryModel.sortName": "",
                                       "queryModel.sortOrder": "asc", "time": 1}, timeout=timeout)
        factors = schema.ScoreFactorSchema(many=True).load(raw.json()["items"][:-1])
        return factors

    def score(self, year: int, term: int, timeout: TimeoutTypes = UNSET) -> model.Results[model.Score]:
        """
        Fetch your scores of specific year & term.

        :param year: year for the new :class:`Scores` object.
        :param term: term for the new :class:`Scores` object.
        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A new :class:`Scores` object.
        """
        raw = self._session.post(const.SCORE_URL, data={"xnm": year, "xqm": const.TERMS[term], "_search": False,
                                                        "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                                        "queryModel.currentPage": 1, "queryModel.sortName": "",
                                                        "queryModel.sortOrder": "asc", "time": 1}, timeout=timeout)
        scores = model.Scores(year, term, partial(self._get_score_detail, timeout=timeout))
        scores.load(raw.json()["items"])
        return scores
