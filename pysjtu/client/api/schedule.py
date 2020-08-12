from typing import Union

from pysjtu import consts
from pysjtu import models
from pysjtu.client.base import BaseClient


class ScheduleMixin(BaseClient):
    async def schedule(self, year: int, term: int) -> models.Results[models.ScheduleCourse]:
        """
        Fetch your course schedule of specific year & term.

        :param year: year for the new :class:`Schedule` object.
        :param term: term for the new :class:`Schedule` object.
        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A new :class:`Schedule` object.
        :rtype: :class:`Schedule`
        """
        raw = await self._session.post(consts.SCHEDULE_URL, data={"xnm": year, "xqm": consts.TERMS[term]})
        schedule = models.Schedule(year, term)
        schedule.load((await raw.json())["kbList"])  # type: ignore
        return schedule
