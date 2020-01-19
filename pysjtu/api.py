import pickle
import re
import time
import typing
from functools import partial
from http.cookiejar import CookieJar
from urllib.parse import urlparse, parse_qs
import warnings

import httpx
from httpx.config import UNSET

from . import const
from . import model
from . import schema
from . import util


class LoadWarning(UserWarning):
    pass


class DumpWarning(UserWarning):
    pass


class GPACalculationException(Exception):
    pass


class SessionException(Exception):
    pass


class LoginException(Exception):
    pass


class ServiceUnavailable(Exception):
    pass


class Session:
    _client = None
    _retry = [.5] * 5 + list(range(1, 5))

    def _secure_req(self, ref):
        try:
            return ref()
        except httpx.exceptions.NetworkError as e:
            req = e.request
            if not req.url.is_ssl:
                req.url = req.url.copy_with(scheme="https", port=None)
            else:
                raise e
            return self._client.send(req)

    def __init__(self, retry=None):
        self._client = httpx.Client()
        self._username = None
        self._password = None
        self._student_id = None
        self._term_start = None
        self._default_gpa_query_params = None
        if retry: self._retry = retry

    def request(self, *args, **kwargs):
        rtn = self._client.request(*args, **kwargs)
        try:
            rtn.raise_for_status()
        except httpx.exceptions.HTTPError as e:
            if rtn.status_code == httpx.codes.SERVICE_UNAVAILABLE:
                raise ServiceUnavailable
            else:
                raise e
        if rtn.url.full_path == "/xtgl/login_slogin.html":
            self._secure_req(partial(self.get, const.LOGIN_URL))  # refresh JSESSION token
            # Sometimes the old session will be retrieved, so we won't need to login again
            if self._client.get(const.HOME_URL).url.full_path == "/xtgl/login_slogin.html":
                if self._username and self._password:
                    self.login(self._username, self._password)
                else:
                    raise SessionException
            rtn = self._client.request(*args, **kwargs)
        return rtn

    def get(self, *args, **kwargs):
        return self.request("GET", *args, **kwargs)

    def options(self, *args, **kwargs):
        return self.request("OPTIONS", *args, **kwargs)

    def head(self, *args, **kwargs):
        return self.request("HEAD", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request("POST", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request("PUT", *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.request("PATCH", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request("DELETE", *args, **kwargs)

    def login(self, username, password):
        self._student_id = None
        for i in self._retry:
            login_page_req = self._secure_req(partial(self.get, const.LOGIN_URL))
            uuid = re.findall(r"(?<=uuid\": ').*(?=')", login_page_req.text)[0]
            login_params = parse_qs(urlparse(str(login_page_req.url)).query)
            login_params = {k: v[0] for k, v in login_params.items()}

            captcha_img = self.get(const.CAPTCHA_URL,
                                   params={"uuid": uuid, "t": int(time.time() * 1000)}).content
            captcha = util.recognize_captcha(captcha_img)

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
        cookie_bak = self._client.cookies
        self._client.get(const.LOGOUT_URL, params={"t": int(time.time()*1000), "login_type": ""})
        if purge_session:
            self._username = None
            self._password = None
        else:
            self._client.cookies = cookie_bak

    def loads(self, d):
        renew_required = True

        if "username" not in d.keys() or "password" not in d.keys() or not d["username"] or not d["password"]:
            warnings.warn("Missing username or password field", LoadWarning)
            renew_required = False
        else:
            self._username = d["username"]
            self._password = d["password"]

        if "cookies" in d.keys():
            cj = CookieJar()
            cj._cookies = d["cookies"]
            try:
                self.cookies = cj
                renew_required = False
            except SessionException:
                pass

        if renew_required:
            self.login(self._username, self._password)

    def load(self, fp):
        conf = pickle.load(fp)
        self.loads(conf)

    def dumps(self):
        if not self._username or not self._password:
            warnings.warn("Missing username or password field", DumpWarning)
        return {"username": self._username, "password": self._password,
                "cookies": self._client.cookies.jar._cookies}

    def dump(self, fp):
        pickle.dump(self.dumps(), fp)

    @property
    def proxies(self):
        return self._client.proxies

    @proxies.setter
    def proxies(self, new_proxy: list):
        self._client.proxies = new_proxy

    @property
    def _cookies(self):
        return self._client.cookies

    @_cookies.setter
    def _cookies(self, new_cookie):
        self._student_id = None
        self._client.cookies = new_cookie

    @property
    def cookies(self):
        return self._client.cookies

    @cookies.setter
    def cookies(self, new_cookie):
        bak_cookie = self._client.cookies
        self._student_id = None
        self._client.cookies = new_cookie
        self._secure_req(partial(self.get, const.LOGIN_URL))  # refresh JSESSION token
        if self._client.get(const.HOME_URL).url.full_path == "/xtgl/login_slogin.html":
            self._client.cookies = bak_cookie
            raise SessionException("Invalid cookies. You may skip this validation by setting _cookies")

    @property
    def timeout(self):
        return self._client.timeout

    @timeout.setter
    def timeout(self, new_timeout):
        if isinstance(new_timeout, int):
            self._client.timeout = httpx.Timeout(new_timeout)
        elif isinstance(new_timeout, httpx.Timeout):
            self._client.timeout = new_timeout
        else:
            raise TypeError

    @property
    def term_start_date(self):
        if not self._term_start:
            raw = self.get(const.CALENDAR_URL + self.student_id)
            self._term_start = min(re.findall(r"\d{4}-\d{2}-\d{2}", raw.text))
        return self._term_start

    @property
    def student_id(self):
        if not self._student_id:
            rtn = self.get(const.HOME_URL)
            self._student_id = re.findall(r"(?<=id=\"sessionUserKey\" value=\")\d*", rtn.text)[0]
        return self._student_id

    @property
    def default_gpa_query_params(self) -> model.GPAQueryParams:
        if not self._default_gpa_query_params:
            rtn = self.get(const.GPA_PARAMS_URL, params={"_": int(time.time() * 1000), "su": self.student_id})
            raw_params = {item["zdm"]: item["szz"] for item in filter(lambda x: "szz" in x.keys(), rtn.json())}
            self._default_gpa_query_params = schema.GPAQueryParamsSchema().load(raw_params)

        return self._default_gpa_query_params

    def schedule(self, year, term, timeout=UNSET) -> model.Schedule:
        raw = self.post(const.SCHEDULE_URL, data={"xnm": year, "xqm": const.TERMS[term]}, timeout=timeout)
        schedule = model.Schedule(year, term)
        schedule.load(raw.json()["kbList"])
        return schedule

    def _get_score_detail(self, year, term, class_id, timeout=UNSET) -> typing.List[model.ScoreFactor]:
        raw = self.post(const.SCORE_DETAIL_URL + self.student_id,
                        data={"xnm": year, "xqm": const.TERMS[term], "jxb_id": class_id, "_search": False,
                              "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                              "queryModel.currentPage": 1, "queryModel.sortName": "",
                              "queryModel.sortOrder": "asc", "time": 1}, timeout=timeout)
        factors = schema.ScoreFactorSchema(many=True).load(raw.json()["items"][:-1])
        return factors

    def score(self, year, term, timeout=UNSET) -> model.Scores:
        raw = self.post(const.SCORE_URL, data={"xnm": year, "xqm": const.TERMS[term], "_search": False,
                                               "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                               "queryModel.currentPage": 1, "queryModel.sortName": "",
                                               "queryModel.sortOrder": "asc", "time": 1}, timeout=timeout)
        scores = model.Scores(year, term, self._get_score_detail)
        scores.load(raw.json()["items"])
        return scores

    def exam(self, year, term, timeout=UNSET) -> model.Exams:
        raw = self.post(const.EXAM_URL + self.student_id,
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
        _args = {"year": "xnm", "term": "xqm", "name": "kch_id", "teacher": "jqh_id", "day_of_week": "xqj",
                 "week": "qsjsz", "time_of_day": "skjc"}
        year = year
        term = const.TERMS[term]
        name = name if name else ''
        teacher = teacher if teacher else ''
        day_of_week = util.range_list_to_str(day_of_week) if day_of_week else ''
        week = util.range_list_to_str(week) if week else ''
        time_of_day = util.range_list_to_str(time_of_day) if time_of_day else ''
        req_params = {}
        for (k, v) in _args.items():
            if k in dir():
                req_params[v] = locals()[k]

        req = partial(self.post, const.COURSELIB_URL + self.student_id, timeout=timeout)

        return model.QueryResult(req, partial(util.schema_post_loader, schema.LibCourseSchema), req_params)

    def query_gpa(self, query_params: model.GPAQueryParams, timeout=UNSET):
        compiled_params = schema.GPAQueryParamsSchema().dump(query_params)
        calc_rtn = self.post(const.GPA_CALC_URL + self.student_id, data=compiled_params, timeout=timeout)
        if calc_rtn.text != "\"统计成功！\"": raise GPACalculationException
        compiled_params.update({"_search": False,
                                "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                "queryModel.currentPage": 1, "queryModel.sortName": "",
                                "queryModel.sortOrder": "asc", "time": 0})
        raw = self.post(const.GPA_QUERY_URL + self.student_id, data=compiled_params, timeout=timeout)
        return schema.GPASchema().load(raw.json()["items"][0])

    def _elect(self, params):
        r = self.post(const.ELECT_URL + self.student_id, data=params)
        return r.json()
