import time

from httpx.config import (
    UNSET,
    TimeoutTypes
)

from pysjtu import const
from pysjtu import model
from pysjtu.client.base import BaseClient


class ExamMixin(BaseClient):
    def exam(self, year: int, term: int, timeout: TimeoutTypes = UNSET) -> model.Results[model.Exam]:
        """
        Fetch your exams schedule of specific year & term.

        :param year: year for the new :class:`Exams` object.
        :param term: term for the new :class:`Exams` object.
        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A new :class:`Exams` object.
        """
        raw = self._session.post(const.EXAM_URL + str(self.student_id),
                                 data={"xnm": year, "xqm": const.TERMS[term], "_search": False, "ksmcdmb_id": '',
                                       "kch": '', "kc": '', "ksrq": '', "kkbm_id": '',
                                       "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                       "queryModel.currentPage": 1, "queryModel.sortName": "",
                                       "queryModel.sortOrder": "asc", "time": 1}, timeout=timeout)
        scores = model.Exams(year, term)
        scores.load(raw.json()["items"])
        return scores
