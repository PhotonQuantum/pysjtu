import time
from functools import partial
from typing import List, Union

from pysjtu import consts
from pysjtu import models
from pysjtu import schemas
from pysjtu.client.base import BaseClient


class ScoreMixin(BaseClient):
    async def _get_score_detail(self, year: int, term: int, class_id: str) -> List[models.ScoreFactor]:
        raw = await self._session.post(f"{consts.SCORE_DETAIL_URL}{await self.student_id}",
                                 data={"xnm": year, "xqm": consts.TERMS[term], "jxb_id": class_id, "_search": False,
                                       "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                       "queryModel.currentPage": 1, "queryModel.sortName": "",
                                       "queryModel.sortOrder": "asc", "time": 1})
        factors = schemas.ScoreFactorSchema(many=True).load((await raw.json())["items"][:-1])  # type: ignore
        return factors

    async def score(self, year: int, term: int) -> models.Results[models.Score]:
        """
        Fetch your scores of specific year & term.

        :param year: year for the new :class:`Scores` object.
        :param term: term for the new :class:`Scores` object.
        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A new :class:`Scores` object.
        :rtype: :class:`Scores`
        """
        raw = await self._session.post(consts.SCORE_URL,
                                 data={"xnm": year, "xqm": consts.TERMS[term], "_search": False,
                                       "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                       "queryModel.currentPage": 1, "queryModel.sortName": "",
                                       "queryModel.sortOrder": "asc", "time": 1})
        scores = models.Scores(year, term, self._get_score_detail)
        scores.load((await raw.json())["items"])  # type: ignore
        return scores
