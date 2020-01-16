import pickle
import re
import time
from functools import partial
from json.decoder import JSONDecodeError
from typing import List
from urllib.parse import urlparse, parse_qs

import requests

from . import const
from . import model
from . import schema
from . import util


class SessionException(Exception):
    pass


class ServiceUnavailable(Exception):
    pass


class Session:
    _sess: requests.Session
    _retry = [.5] * 5 + list(range(1, 5))

    def _secure_req(self, ref):
        try:
            return ref()
        except requests.exceptions.ConnectionError as e:
            req = e.request
            if req.url[:7] == "http://":
                req.url = req.url.replace("http://", "https://")
            else:
                raise e
            return self._sess.send(req)

    @staticmethod
    def _http_error_handler(req, *args, **kwargs):
        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError:
            if req.status_code == 503:
                raise ServiceUnavailable

    def __init__(self, retry=None):
        self._sess = requests.session()
        self._sess.hooks = {"response": Session._http_error_handler}
        self._student_id = None
        self._term_start = None
        if retry: self._retry = retry

    def login(self, username, password):
        self._student_id = None
        for i in self._retry:
            login_page_req = self._secure_req(partial(self._sess.get, const.LOGIN_URL))
            uuid = re.findall(r"(?<=uuid\": ').*(?=')", login_page_req.text)[0]
            login_params = parse_qs(urlparse(login_page_req.url).query)
            login_params = dict(map(lambda x: (x[0], x[1][0]), login_params.items()))

            captcha_img = self._sess.get(const.CAPTCHA_URL, params={"uuid": uuid, "t": int(time.time() * 1000)}).content
            captcha = util.recognize_captcha(captcha_img)

            login_params.update({"v": "", "uuid": uuid, "user": username, "pass": password, "captcha": captcha})
            result = self._secure_req(
                partial(self._sess.post, const.LOGIN_POST_URL, params=login_params, headers=const.HEADERS))
            if "err=1" not in result.url: return

            time.sleep(i)

    def load(self, fn):
        with open(fn, mode="rb") as f:
            self.cookies = pickle.load(f)

    def dump(self, fn):
        with open(fn, mode="wb") as f:
            pickle.dump(self._sess.cookies, f)

    @property
    def proxies(self):
        return self._sess.proxies

    @proxies.setter
    def proxies(self, new_proxy: list):
        self._sess.proxies = new_proxy

    @property
    def cookies(self):
        return self._sess.cookies

    @cookies.setter
    def cookies(self, new_cookie):
        bak_cookie = self._sess.cookies
        self._student_id = None
        self._sess.cookies = new_cookie
        try:
            self._secure_req(partial(self._sess.get, const.LOGIN_URL, timeout=5))  # refresh JSESSION token
        except requests.ReadTimeout:
            self._sess.cookies = bak_cookie
            raise SessionException
        if "login" in self._sess.get(const.HOME_URL).url:
            self._sess.cookies = bak_cookie
            raise SessionException

    @property
    def term_start_date(self):
        if not self._term_start:
            raw = self._sess.get(const.CALENDAR_URL + self.student_id)
            self._term_start = min(re.findall(r"\d{4}-\d{2}-\d{2}", raw.text))
        return self._term_start

    @property
    def student_id(self):
        if not self._student_id:
            rtn = self._sess.get(const.HOME_URL)
            self._student_id = re.findall(r"(?<=id=\"sessionUserKey\" value=\")\d*", rtn.text)[0]
        return self._student_id

    def schedule(self, year, term) -> model.Schedule:
        raw = self._sess.post(const.SCHEDULE_URL, data={"xnm": year, "xqm": const.TERMS[term]})
        schedule = model.Schedule(year, term)
        try:
            schedule.load(raw.json()["kbList"])
        except JSONDecodeError:
            raise SessionException
        return schedule

    def _get_score_detail(self, year, term, class_id) -> List[model.ScoreFactor]:
        raw = self._sess.post(const.SCORE_DETAIL_URL + self.student_id,
                              data={"xnm": year, "xqm": const.TERMS[term], "jxb_id": class_id, "_search": False,
                                    "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                    "queryModel.currentPage": 1, "queryModel.sortName": "",
                                    "queryModel.sortOrder": "asc", "time": 1})
        factors = schema.ScoreFactorSchema(many=True).load(raw.json()["items"][:-1])
        return factors

    def score(self, year, term) -> model.Scores:
        raw = self._sess.post(const.SCORE_URL, data={"xnm": year, "xqm": const.TERMS[term], "_search": False,
                                                     "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                                     "queryModel.currentPage": 1, "queryModel.sortName": "",
                                                     "queryModel.sortOrder": "asc", "time": 1})
        scores = model.Scores(year, term, self._get_score_detail)
        try:
            scores.load(raw.json()["items"])
        except JSONDecodeError:
            raise SessionException
        return scores

    def exam(self, year, term) -> model.Exams:
        raw = self._sess.post(const.EXAM_URL,
                              data={"xnm": year, "xqm": const.TERMS[term], "_search": False, "ksmcdmb_id": None,
                                    "kch": None, "kc": None, "ksrq": None, "kkbm_id": None,
                                    "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                    "queryModel.currentPage": 1, "queryModel.sortName": "",
                                    "queryModel.sortOrder": "asc", "time": 1})
        scores = model.Exams(year, term)
        try:
            scores.load(raw.json()["items"])
        except JSONDecodeError:
            raise SessionException
        return scores

    def query_courses(self, year, term, name=None, teacher=None, day_of_week=None, week=None, time_of_day=None):
        _args = {"year": "xnm", "term": "xqm", "name": "kch_id", "teacher": "jqh_id", "day_of_week": "xqj",
                 "week": "qsjsz", "time_of_day": "skjc"}
        year = year
        term = const.TERMS[term]
        name = name
        teacher = teacher
        day_of_week = util.range_list_to_str(day_of_week) if day_of_week else None
        week = util.range_list_to_str(week) if week else None
        time_of_day = util.range_list_to_str(time_of_day) if time_of_day else None
        req_params = {}
        for (k, v) in _args.items():
            if k in dir():
                req_params[v] = locals()[k]

        req = partial(self._sess.post, const.COURSELIB_URL + self.student_id)

        return model.QueryResult(req, partial(util.schema_post_loader, schema.LibCourseSchema), req_params)

    def _elect(self, params):
        r = self._sess.post(const.ELECT_URL + self.student_id, data=params)
        return r.json()
