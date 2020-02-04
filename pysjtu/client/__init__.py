import re
from datetime import datetime, date

from pysjtu import const
from pysjtu.client.api import ScheduleMixin, CourseLibMixin, ExamMixin, GPAMixin, ScoreMixin
from pysjtu.session import Session
from pysjtu.utils import has_callable


class Client(ScheduleMixin, CourseLibMixin, ExamMixin, GPAMixin, ScoreMixin):
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
    """
    _session: Session
    _term_start: date

    def __init__(self, session: Session):
        """
        A pysjtu client with schedule query, score query, exam query, etc.

        :param session: The :class:`Session` to be built upon.
        """
        super().__init__()
        _session_callable = ["get", "post"]

        _available_callable = map(lambda x: has_callable(session, x), ["get", "post"])
        if False in _available_callable:
            _missing_callable = [item[0] for item in zip(_session_callable, _available_callable) if not item[1]]
            raise TypeError(f"Missing callable(s) in given session object: {_missing_callable}")

        if not isinstance(getattr(session, "_cache_store", None), dict):
            raise TypeError("Missing dict in given session object: _cache_store")

        self._session = session

        # noinspection PyTypeChecker
        self._term_start = None  # type: ignore

    @property
    def term_start_date(self) -> date:
        """ Get the term start date for the current term. """
        if not self._term_start:
            raw = self._session.get(const.CALENDAR_URL + str(self.student_id))
            self._term_start = datetime.strptime(min(re.findall(r"\d{4}-\d{2}-\d{2}", raw.text)), "%Y-%m-%d").date()
        return self._term_start

    # noinspection PyProtectedMember
    @property
    def student_id(self) -> int:
        """ Get the student id of the current session. """
        if "student_id" not in self._session._cache_store:
            rtn = self._session.get(const.HOME_URL)
            self._session._cache_store["student_id"] = int(
                re.findall(r"(?<=id=\"sessionUserKey\" value=\")\d*", rtn.text)[0])
        return self._session._cache_store["student_id"]


def create_client(username: str, password: str, _mocker_app=None) -> Client:
    """
    Create a new :class:`Client` with default options.
    To change :class:`Session` settings or preserve your session, use :class:`Session` and :class:`Client` instead.

    :param username: JAccount username.
    :param password: JAccount password.
    :param _mocker_app: An WSGI application to send requests to (for debug or test purposes).
    :return: an authenticated :class:`Client`.
    """
    sess = Session(username=username, password=password, _mocker_app=_mocker_app)
    return Client(session=sess)
