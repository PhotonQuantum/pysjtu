import time

from pysjtu import consts
from pysjtu import models
from pysjtu.client.base import BaseClient


class ExamMixin(BaseClient):
    def __init__(self):
        super().__init__()

    def exam(self, year: int, term: int, **kwargs) -> models.Results[models.Exam]:
        """
        Fetch your exams schedule of specific year & term.

        See :meth:`pysjtu.session.Session.post` for more information about the keyword arguments.

        :param year: query year
        :param term: query term
        """
        raw = self._session.post(consts.EXAM_URL + str(self.student_id),
                                 data={"xnm": year, "xqm": consts.TERMS[term], "_search": False, "ksmcdmb_id": '',
                                       "kch": '', "kc": '', "ksrq": '', "kkbm_id": '',
                                       "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                       "queryModel.currentPage": 1, "queryModel.sortName": "",
                                       "queryModel.sortOrder": "asc", "time": 1}, **kwargs)
        scores = models.Exams(year, term)
        scores.load(raw.json()["items"])  # type: ignore
        return scores
