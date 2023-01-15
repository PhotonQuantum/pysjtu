import re
from datetime import date, datetime

from pysjtu import consts
from pysjtu.client.api import CourseLibMixin, ExamMixin, GPAMixin, ScheduleMixin, ScoreMixin, SelectionMixin, \
    ProfileMixin
from pysjtu.client.base import BaseClient
from pysjtu.session import BaseSession, Session
from pysjtu.utils import forward_method_args


class Client(ProfileMixin, SelectionMixin, ScheduleMixin, CourseLibMixin, ExamMixin, GPAMixin, ScoreMixin, BaseClient):
    """
    A pysjtu client with schedule query, score query, exam query, etc.

    Usage::

        >>> import pysjtu
        >>> s = pysjtu.Session(username="user@sjtu.edu.cn", password="something_secret")
        >>> client = pysjtu.Client(session=s)
        >>> sched = client.schedule(2019, 0)
        >>> sched
        [<ScheduleCourse 军事理论 week=[range(9, 17)] day=1 time=range(1, 3)>, ...]
        >>> sched.filter(time=range(3,5), day=range(2, 4))
        [<ScheduleCourse 程序设计思想与方法（C++） week=[range(1, 10), range(11, 17)] day=2 time=range(3, 5)>,
        <ScheduleCourse 大学英语（4） week=[range(1, 17)] day=3 time=range(3, 5)>]

    :param session: The :class:`Session` to be built upon.
    """
    _session: BaseSession
    _term_start: date

    def __init__(self, session: BaseSession):
        super().__init__()
        if not isinstance(session, BaseSession):
            raise TypeError("'session' isn't an instance of BaseSession.")
        self._session = session

        # noinspection PyTypeChecker
        self._term_start = None  # type: ignore

    @property
    def term_start_date(self) -> date:
        """ Get the term start date for the current term. """
        if not self._term_start:
            raw = self._session.get(consts.CALENDAR_URL + str(self.student_id))
            self._term_start = datetime.strptime(min(re.findall(r"\d{4}-\d{2}-\d{2}", raw.text)), "%Y-%m-%d").date()
        return self._term_start

    # noinspection PyProtectedMember
    @property
    def student_id(self) -> int:
        """ Get the student id of the current session. """
        if "student_id" not in self._session._cache_store:
            rtn = self._session.get(consts.HOME_URL)
            self._session._cache_store["student_id"] = int(
                re.findall(r"(?<=id=\"sessionUserKey\" value=\")\d*", rtn.text)[0])
        return self._session._cache_store["student_id"]


@forward_method_args(Session.__init__)
def create_client(*args, **kwargs) -> Client:
    """
    Create a new :class:`Client` with given options.

    This is just a shortcut for ``Client(Session(*args, **kwargs))``.
    To manipulate or reuse underlying Session object, use :class:`pysjtu.session.Session` and :class:`Client` instead.

    :return: an authenticated :class:`Client`.
    """
    sess = Session(*args, **kwargs)
    return Client(session=sess)
