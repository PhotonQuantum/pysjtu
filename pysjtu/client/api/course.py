from functools import partial

from pysjtu import consts
from pysjtu import models
from pysjtu.client.base import BaseClient
from pysjtu.utils import range_list_to_str, schema_post_loader


class CourseLibMixin(BaseClient):
    def __init__(self):
        super().__init__()

    def query_courses(self, year: int, term: int, page_size: int = 15, name: str = None, teacher: str = None,
                      day_of_week: list = None, week: list = None, time_of_day: list = None,
                      **kwargs) -> models.QueryResult[models.LibCourse]:
        """
        Query courses matching given criteria from the whole course lib of SJTU.

        See :meth:`pysjtu.session.Session.post` for more information about the keyword arguments.

        :param year: year in which target courses are given.
        :param term: term in which target courses are given.
        :param page_size: page size for result iteration.
        :param name: (optional) Name (can be fuzzy) of target courses.
        :param teacher: (optional) Teacher name of target courses.
        :param day_of_week: (optional) Day of week of target courses.
        :param week: (optional) Week of target courses.
        :param time_of_day: (optional) Time of day of target courses.
        """
        _args = {"year": "xnm", "term": "xqm", "name": "kch_id", "teacher": "jqh_id", "day_of_week": "xqj",
                 "week": "qsjsz", "time_of_day": "skjc"}
        year = year
        term = consts.TERMS[term]
        name = name if name else ''
        teacher = teacher if teacher else ''
        day_of_week = range_list_to_str(day_of_week) if day_of_week else []
        week = range_list_to_str(week) if week else []
        time_of_day = range_list_to_str(time_of_day) if time_of_day else []
        req_params = {}
        for (k, v) in _args.items():
            if k in dir():
                req_params[v] = locals()[k]

        req = partial(self._session.post, consts.COURSELIB_URL + str(self.student_id), **kwargs)

        return models.QueryResult(req, partial(schema_post_loader, models.LibCourse.Schema), req_params,
                                  page_size=page_size)
