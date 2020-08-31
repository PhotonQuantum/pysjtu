import time
from typing import Union

from httpx.config import (TimeoutTypes, UNSET, UnsetType)

from pysjtu import consts
from pysjtu import models
from pysjtu.client.base import BaseClient


class ExamMixin(BaseClient):
    def __init__(self):
        super().__init__()

    def exam(self, year: int, term: int, timeout: Union[TimeoutTypes, UnsetType] = UNSET) \
            -> models.Results[models.Exam]:
        """
        Fetch your exams schedule of specific year & term.

        :param year: year for the new :class:`Exams` object.
        :param term: term for the new :class:`Exams` object.
        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A new :class:`Exams` object.
        :rtype: :class:`Exams`
        """
        raw = self._session.post(consts.EXAM_URL + str(self.student_id),
                                 data={"xnm": year, "xqm": consts.TERMS[term], "_search": False, "ksmcdmb_id": '',
                                       "kch": '', "kc": '', "ksrq": '', "kkbm_id": '',
                                       "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                       "queryModel.currentPage": 1, "queryModel.sortName": "",
                                       "queryModel.sortOrder": "asc", "time": 1}, timeout=timeout)
        scores = models.Exams(year, term)
        scores.load(raw.json()["items"])  # type: ignore
        return scores
