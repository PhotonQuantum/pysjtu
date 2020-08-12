import time
from typing import Union

from pysjtu import consts
from pysjtu import models
from pysjtu.client.base import BaseClient


class ExamMixin(BaseClient):
    async def exam(self, year: int, term: int) -> models.Results[models.Exam]:
        """
        Fetch your exams schedule of specific year & term.

        :param year: year for the new :class:`Exams` object.
        :param term: term for the new :class:`Exams` object.
        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A new :class:`Exams` object.
        :rtype: :class:`Exams`
        """
        raw = await self._session.post(f"{consts.EXAM_URL}{await self.student_id}",
                                 data={"xnm": year, "xqm": consts.TERMS[term], "_search": False, "ksmcdmb_id": '',
                                       "kch": '', "kc": '', "ksrq": '', "kkbm_id": '',
                                       "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                       "queryModel.currentPage": 1, "queryModel.sortName": "",
                                       "queryModel.sortOrder": "asc", "time": 1})
        scores = models.Exams(year, term)
        scores.load((await raw.json())["items"])  # type: ignore
        return scores
