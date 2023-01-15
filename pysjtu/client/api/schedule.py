from pysjtu import consts
from pysjtu import models
from pysjtu.client.base import BaseClient


class ScheduleMixin(BaseClient):
    def __init__(self):
        super().__init__()

    def schedule(self, year: int, term: int, **kwargs) -> models.Results[models.ScheduleCourse]:
        """
        Fetch your course schedule of specific year & term.

        See :meth:`pysjtu.session.Session.post` for more information about the keyword arguments.

        :param year: query year
        :param term: query term
        """
        raw = self._session.post(consts.SCHEDULE_URL, data={"xnm": year, "xqm": consts.TERMS[term]}, **kwargs)
        schedule = models.Schedule(year, term)
        schedule.load(raw.json()["kbList"])  # type: ignore
        return schedule
