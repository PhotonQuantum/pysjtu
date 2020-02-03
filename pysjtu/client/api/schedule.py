from httpx.config import (
    UNSET,
    TimeoutTypes
)

from pysjtu import const
from pysjtu import model
from pysjtu.client.base import BaseClient


class ScheduleMixin(BaseClient):
    def schedule(self, year: int, term: int, timeout: TimeoutTypes = UNSET) -> model.Results[model.ScheduleCourse]:
        """
        Fetch your course schedule of specific year & term.

        :param year: year for the new :class:`Schedule` object.
        :param term: term for the new :class:`Schedule` object.
        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A new :class:`Schedule` object.
        """
        raw = self._session.post(const.SCHEDULE_URL, data={"xnm": year, "xqm": const.TERMS[term]}, timeout=timeout)
        schedule = model.Schedule(year, term)
        schedule.load(raw.json()["kbList"])
        return schedule
