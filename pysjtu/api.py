import io
import pickle
import re
import time
import warnings
from functools import partial
from http.cookiejar import CookieJar
from urllib.parse import urlparse, parse_qs

import httpx
from httpx.config import UNSET

from . import const
from . import model
from . import schema
from .exceptions import *
from .utils import has_callable, range_list_to_str, schema_post_loader
from .ocr import NNRecognizer


class Session:
    """
    A pysjtu session with login management, cookie persistence, etc.

    Usage::

        >>> import pysjtu
        >>> s = pysjtu.Session()
        >>> s.login('user@sjtu.edu.cn', 'something_secret')
        >>> s.get('https://i.sjtu.edu.cn')
        <Response [200 OK]>
        >>> s.dump('session_file')

    Or as a context manager::

        >>> with pysjtu.Session(username='user@sjtu.edu.cn', password='something_secret') as s:
        ...     s.get('https://i.sjtu.edu.cn')
        ...     s.dump('session_file')
        <Response [200 OK]>

        >>> with pysjtu.Session(session_file='session_file', mode='r+b')) as s:
        ...     s.get('https://i.sjtu.edu.cn')
        <Response [200 OK]>
    """
    _client = None  # httpx session
    _retry = [.5] * 5 + list(range(1, 5))  # retry list

    def _secure_req(self, ref):
        """
        Send a request using HTTPS explicitly to work around an upstream bug.

        :param ref: a partial request call.
        :return: the response of the original request.
        """
        try:
            return ref()
        except httpx.exceptions.NetworkError as e:
            req = e.request
            if not req.url.is_ssl:
                req.url = req.url.copy_with(scheme="https", port=None)
            else:
                raise e
            return self._client.send(req)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close()
        if self._session_file:
            if isinstance(self._session_file, (io.RawIOBase, io.BufferedIOBase)):
                self._session_file.seek(0)
            self.dump(self._session_file)

    def __init__(self, username="", password="", cookies=None, ocr=None, session_file=None, retry=None):
        self._client = httpx.Client()
        if not ocr:
            self._ocr = NNRecognizer()
        self._username = ""
        self._password = ""
        self._cache_store = {}
        # noinspection PyTypeChecker
        self._session_file = None
        if retry:
            self._retry = retry

        if session_file:
            self.load(session_file)
            self._session_file = session_file
        elif cookies or (username and password):
            self.loads({"username": username, "password": password, "cookies": cookies})

    def request(self, *args, validate_session=True, auto_renew=True, **kwargs):
        """
        Send a request. If asked, validate the current session and renew it when necessary.

        :param args: same as httpx.request.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :param kwargs: same as httpx.request.
        :return: an :class:`Response` object.
        """
        rtn = self._client.request(*args, **kwargs)
        try:
            rtn.raise_for_status()
        except httpx.exceptions.HTTPError as e:
            if rtn.status_code == httpx.codes.SERVICE_UNAVAILABLE:
                raise ServiceUnavailable
            else:
                raise e
        if validate_session and rtn.url.full_path == "/xtgl/login_slogin.html":
            if not auto_renew:
                raise SessionException("Session expired.")
            else:
                self._secure_req(partial(self.get, const.LOGIN_URL, validate_session=False))  # refresh JSESSION token
                # Sometimes the old session will be retrieved, so we won't need to login again
                if self._client.get(const.HOME_URL).url.full_path == "/xtgl/login_slogin.html":
                    if self._username and self._password:
                        self.login(self._username, self._password)
                    else:
                        raise SessionException("Session expired. Unable to renew session due to missing username or "
                                               "password")
                rtn = self._client.request(*args, **kwargs)
        return rtn

    def get(self, *args, validate_session=True, auto_renew=True, **kwargs):
        """
        Send a GET request. If asked, validate the current session and renew it when necessary.

        :param args: same as httpx.request.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :param kwargs: same as httpx.request.
        :return: an :class:`Response` object.
        """
        return self.request("GET", *args, validate_session=validate_session, auto_renew=auto_renew, **kwargs)

    def options(self, *args, validate_session=True, auto_renew=True, **kwargs):
        """
        Send a OPTIONS request. If asked, validate the current session and renew it when necessary.

        :param args: same as httpx.request.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :param kwargs: same as httpx.request.
        :return: an :class:`Response` object.
        """
        return self.request("OPTIONS", *args, validate_session=validate_session, auto_renew=auto_renew, **kwargs)

    def head(self, *args, validate_session=True, auto_renew=True, **kwargs):
        """
        Send a HEAD request. If asked, validate the current session and renew it when necessary.

        :param args: same as httpx.request.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :param kwargs: same as httpx.request.
        :return: an :class:`Response` object.
        """
        return self.request("HEAD", *args, validate_session=validate_session, auto_renew=auto_renew, **kwargs)

    def post(self, *args, validate_session=True, auto_renew=True, **kwargs):
        """
        Send a POST request. If asked, validate the current session and renew it when necessary.

        :param args: same as httpx.request.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :param kwargs: same as httpx.request.
        :return: an :class:`Response` object.
        """
        return self.request("POST", *args, validate_session=validate_session, auto_renew=auto_renew, **kwargs)

    def put(self, *args, validate_session=True, auto_renew=True, **kwargs):
        """
        Send a PUT request. If asked, validate the current session and renew it when necessary.

        :param args: same as httpx.request.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :param kwargs: same as httpx.request.
        :return: an :class:`Response` object
        """
        return self.request("PUT", *args, validate_session=validate_session, auto_renew=auto_renew, **kwargs)

    def patch(self, *args, validate_session=True, auto_renew=True, **kwargs):
        """
        Sends a PATCH request. If asked, validates the current session and renews it when necessary.

        :param args: same as httpx.request.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :param kwargs: same as httpx.request
        :return: an :class:`Response` object.
        """
        return self.request("PATCH", *args, validate_session=validate_session, auto_renew=auto_renew, **kwargs)

    def delete(self, *args, validate_session=True, auto_renew=True, **kwargs):
        """
        Sends a DELETE request. If asked, validates the current session and renews it when necessary.

        :param args: same as httpx.request.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :param kwargs: same as httpx.request.
        :return: an :class:`Response` object.
        """
        return self.request("DELETE", *args, validate_session=validate_session, auto_renew=auto_renew, **kwargs)

    def login(self, username, password):
        """
        Log in JAccount using given username & password.

        :param username: JAccount username.
        :param password: JAccount password.
        :raises LoginException: Failed to login after several attempts.
        """
        self._cache_store = {}
        for i in self._retry:
            login_page_req = self._secure_req(partial(self.get, const.LOGIN_URL, validate_session=False))
            uuid = re.findall(r"(?<=uuid\": ').*(?=')", login_page_req.text)[0]
            login_params = parse_qs(urlparse(str(login_page_req.url)).query)
            login_params = {k: v[0] for k, v in login_params.items()}

            captcha_img = self.get(const.CAPTCHA_URL,
                                   params={"uuid": uuid, "t": int(time.time() * 1000)}).content
            captcha = self._ocr.recognize(captcha_img)

            login_params.update({"v": "", "uuid": uuid, "user": username, "pass": password, "captcha": captcha})
            result = self._secure_req(
                partial(self.post, const.LOGIN_POST_URL, params=login_params, headers=const.HEADERS))
            if "err=1" not in result.url.query:
                self._username = username
                self._password = password
                return

            time.sleep(i)

        raise LoginException

    def logout(self, purge_session=True):
        """
        Log out JAccount.

        :param purge_session: (optional) Whether to purge local session info. May causes inconsistency, so use with
            caution.
        """
        cookie_bak = self._client.cookies
        self.get(const.LOGOUT_URL, params={"t": int(time.time() * 1000), "login_type": ""}, validate_session=False)
        if purge_session:
            self._username = ''
            self._password = ''
        else:
            self._client.cookies = cookie_bak

    def loads(self, d):
        """
        Read a session from a given dict. A warning will be given if username or password field is missing.

        :param d: a dict contains a session.
        """
        renew_required = True

        if "username" not in d.keys() or "password" not in d.keys() or not d["username"] or not d["password"]:
            warnings.warn("Missing username or password field", LoadWarning)
            self._username = ""
            self._password = ""
            renew_required = False
        else:
            self._username = d["username"]
            self._password = d["password"]

        if "cookies" in d.keys() and d["cookies"]:
            cj = CookieJar()
            cj._cookies = d["cookies"]
            try:
                self.cookies = cj
                renew_required = False
            except SessionException:
                pass
        else:
            self._cookies = {}

        if renew_required:
            self.login(self._username, self._password)

    def load(self, fp):
        """
        Read a session from a given file. A warning will be given if username or password field is missing.

        :param fp: a binary file object / filepath contains a session.
        """
        if isinstance(fp, (io.RawIOBase, io.BufferedIOBase)):
            conf = pickle.load(fp)
        elif isinstance(fp, str):
            with open(fp, mode="rb") as f:
                conf = pickle.load(f)
        else:
            raise TypeError
        self.loads(conf)

    # noinspection PyProtectedMember
    def dumps(self):
        """
        Return a dict represents the current session. A warning will be given if username or password field is missing.

        :return: a dict represents the current session.
        """
        if not self._username or not self._password:
            warnings.warn("Missing username or password field", DumpWarning)
        return {"username": self._username, "password": self._password,
                "cookies": self._client.cookies.jar._cookies}

    def dump(self, fp):
        """
        Write the current session to a given file. A warning will be given if username or password field is missing.

        :param fp: a binary file object/ filepath as the destination of session data.
        """
        if isinstance(fp, (io.RawIOBase, io.BufferedIOBase)):
            pickle.dump(self.dumps(), fp)
        elif isinstance(fp, str):
            with open(fp, mode="wb") as f:
                pickle.dump(self.dumps(), f)
        else:
            raise TypeError

    @property
    def proxies(self):
        """
        Get or set the proxy to be used on each request.
        """
        return self._client.proxies

    @proxies.setter
    def proxies(self, new_proxy):
        self._client.proxies = new_proxy

    @property
    def _cookies(self):
        """
        Get or set the cookie to be used on each request. This protected property skips session validation.
        """
        return self._client.cookies

    @_cookies.setter
    def _cookies(self, new_cookie):
        self._student_id = None
        self._client.cookies = new_cookie

    @property
    def cookies(self):
        """
        Get or set the cookie to be used on each request. Session validation is performed on each set event.

        :raises SessionException: when given cookie doesn't contain a valid session.
        """
        return self._client.cookies

    @cookies.setter
    def cookies(self, new_cookie):
        bak_cookie = self._client.cookies
        self._client.cookies = new_cookie
        self._secure_req(partial(self.get, const.LOGIN_URL, validate_session=False))  # refresh JSESSION token
        if self.get(const.HOME_URL, validate_session=False).url.full_path == "/xtgl/login_slogin.html":
            self._client.cookies = bak_cookie
            raise SessionException("Invalid cookies. You may skip this validation by setting _cookies")
        self._cache_store = {}

    @property
    def timeout(self):
        """
        Get or set the timeout to be used on each request.
        """
        return self._client.timeout

    @timeout.setter
    def timeout(self, new_timeout):
        if isinstance(new_timeout, int):
            self._client.timeout = httpx.Timeout(new_timeout)
        elif isinstance(new_timeout, httpx.Timeout):
            self._client.timeout = new_timeout
        else:
            raise TypeError


class Client:
    """
    A pysjtu client with schedule query, score query, exam query, etc.

    Usage::

        >>> import pysjtu
        >>> s = pysjtu.Session(username="user@sjtu.edu.cn", password="something_secret")
        >>> client = pysjtu.Client(session=s)
        >>> sched = client.schedule(2019, 0)
        >>> sched.all()
        [<ScheduleCourse 军事理论 week=[range(9, 17)] day=1 time=range(1, 3)>, ...]
        >>> sched.filter(time=range(3,5), day=range(2, 4))
        [<ScheduleCourse 程序设计思想与方法（C++） week=[range(1, 10), range(11, 17)] day=2 time=range(3, 5)>,
        <ScheduleCourse 大学英语（4） week=[range(1, 17)] day=3 time=range(3, 5)>]
    """

    def __init__(self, session):
        _session_callable = ["get", "post"]

        _available_callable = map(lambda x: has_callable(session, x), ["get", "post"])
        if False in _available_callable:
            _missing_callable = [item[0] for item in zip(_session_callable, _available_callable) if not item[1]]
            raise TypeError(f"Missing callable(s) in given session object: {_missing_callable}")

        if not isinstance(getattr(session, "_cache_store", None), dict):
            raise TypeError("Missing dict in given session object: _cache_store")

        self._session = session

        self._term_start = None
        self._default_gpa_query_params = None

    @property
    def term_start_date(self):
        """
        Get the term start date for the current term.
        """
        if not self._term_start:
            raw = self._session.get(const.CALENDAR_URL + self.student_id)
            self._term_start = min(re.findall(r"\d{4}-\d{2}-\d{2}", raw.text))
        return self._term_start

    # noinspection PyProtectedMember
    @property
    def student_id(self):
        """
        Get the student id of the current session.
        """
        if "student_id" not in self._session._cache_store:
            rtn = self._session.get(const.HOME_URL)
            self._session._cache_store["student_id"] = re.findall(r"(?<=id=\"sessionUserKey\" value=\")\d*", rtn.text)[
                0]
        return self._session._cache_store["student_id"]

    @property
    def default_gpa_query_params(self):
        """
        Get default gpa query params defined by the website.
        """
        if not self._default_gpa_query_params:
            rtn = self._session.get(const.GPA_PARAMS_URL, params={"_": int(time.time() * 1000), "su": self.student_id})
            self._default_gpa_query_params = schema.GPAQueryParamsSchema().load(rtn.json())

        return self._default_gpa_query_params

    def schedule(self, year, term, timeout=UNSET):
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

    def _get_score_detail(self, year, term, class_id, timeout=UNSET):
        raw = self._session.post(const.SCORE_DETAIL_URL + self.student_id,
                                 data={"xnm": year, "xqm": const.TERMS[term], "jxb_id": class_id, "_search": False,
                                       "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                       "queryModel.currentPage": 1, "queryModel.sortName": "",
                                       "queryModel.sortOrder": "asc", "time": 1}, timeout=timeout)
        factors = schema.ScoreFactorSchema(many=True).load(raw.json()["items"][:-1])
        return factors

    def score(self, year, term, timeout=UNSET):
        """
        Fetch your scores of specific year & term.

        :param year: year for the new :class:`Scores` object.
        :param term: term for the new :class:`Scores` object.
        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A new :class:`Scores` object.
        """
        raw = self._session.post(const.SCORE_URL, data={"xnm": year, "xqm": const.TERMS[term], "_search": False,
                                                        "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                                        "queryModel.currentPage": 1, "queryModel.sortName": "",
                                                        "queryModel.sortOrder": "asc", "time": 1}, timeout=timeout)
        scores = model.Scores(year, term, partial(self._get_score_detail, timeout=timeout))
        scores.load(raw.json()["items"])
        return scores

    def exam(self, year, term, timeout=UNSET):
        """
        Fetch your exams schedule of specific year & term.

        :param year: year for the new :class:`Exams` object.
        :param term: term for the new :class:`Exams` object.
        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A new :class:`Exams` object.
        """
        raw = self._session.post(const.EXAM_URL + self.student_id,
                                 data={"xnm": year, "xqm": const.TERMS[term], "_search": False, "ksmcdmb_id": '',
                                       "kch": '', "kc": '', "ksrq": '', "kkbm_id": '',
                                       "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                       "queryModel.currentPage": 1, "queryModel.sortName": "",
                                       "queryModel.sortOrder": "asc", "time": 1}, timeout=timeout)
        scores = model.Exams(year, term)
        scores.load(raw.json()["items"])
        return scores

    def query_courses(self, year, term, name=None, teacher=None, day_of_week=None, week=None, time_of_day=None,
                      timeout=UNSET):
        """
        Query courses matching given criteria from the whole course lib of SJTU.

        :param year: year in which target courses are given.
        :param term: term in which target courses are given.
        :param name: (optional) Name (can be fuzzy) of target courses.
        :param teacher: (optional) Teacher name of target courses.
        :param day_of_week: (optional) Day of week of target courses.
        :param week: (optional) Week of target courses.
        :param time_of_day: (optional) Time of day of target courses.
        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A new :class:`QueryResult` object.
        """
        _args = {"year": "xnm", "term": "xqm", "name": "kch_id", "teacher": "jqh_id", "day_of_week": "xqj",
                 "week": "qsjsz", "time_of_day": "skjc"}
        year = year
        term = const.TERMS[term]
        name = name if name else ''
        teacher = teacher if teacher else ''
        day_of_week = range_list_to_str(day_of_week) if day_of_week else ''
        week = range_list_to_str(week) if week else ''
        time_of_day = range_list_to_str(time_of_day) if time_of_day else ''
        req_params = {}
        for (k, v) in _args.items():
            if k in dir():
                req_params[v] = locals()[k]

        req = partial(self._session.post, const.COURSELIB_URL + self.student_id, timeout=timeout)

        return model.QueryResult(req, partial(schema_post_loader, schema.LibCourseSchema), req_params)

    def query_gpa(self, query_params, timeout=UNSET):
        """
        Query your GP & GPA and their rankings of specific year & term.

        :param query_params: parameters for this query.
            A default one can be fetched by property `default_gpa_query_params`.
        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A new :class:`GPA` object.
        """
        compiled_params = schema.GPAQueryParamsSchema().dump(query_params)
        calc_rtn = self._session.post(const.GPA_CALC_URL + self.student_id, data=compiled_params, timeout=timeout)
        if calc_rtn.text != "\"统计成功！\"":
            if calc_rtn.text == "\"统计失败！\"":
                raise GPACalculationException("Calculation failure.")
            if "无功能权限" in calc_rtn.text:
                raise GPACalculationException("Unauthorized.")
        compiled_params.update({"_search": False,
                                "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                "queryModel.currentPage": 1, "queryModel.sortName": "",
                                "queryModel.sortOrder": "asc", "time": 0})
        raw = self._session.post(const.GPA_QUERY_URL + self.student_id, data=compiled_params, timeout=timeout)
        return schema.GPASchema().load(raw.json()["items"][0])

    def _elect(self, params):
        r = self._session.post(const.ELECT_URL + self.student_id, data=params)
        return r.json()
