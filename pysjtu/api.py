import pickle
import re
import time
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


class Session:
    _retry = [.5] * 5 + list(range(1, 5))

    def __init__(self, retry=None):
        self._sess = requests.session()
        self._student_id = None
        self._term_start = None
        if retry: self._retry = retry

    def login(self, username, password):
        self._student_id = None
        for i in self._retry:
            login_page_req = self._sess.get(const.LOGIN_URL)
            uuid = re.findall(r"(?<=uuid\": ').*(?=')", login_page_req.text)[0]
            login_params = parse_qs(urlparse(login_page_req.url).query)
            login_params = dict(map(lambda x: (x[0], x[1][0]), login_params.items()))

            captcha_img = self._sess.get(const.CAPTCHA_URL, params={"uuid": uuid, "t": int(time.time() * 1000)}).content
            captcha = util.recognize_captcha(captcha_img)

            login_params.update({"v": "", "uuid": uuid, "user": username, "pass": password, "captcha": captcha})
            result = self._sess.post(const.LOGIN_POST_URL, params=login_params, headers=const.HEADERS)
            if "err=1" not in result.url: return

            time.sleep(i)

    def load(self, fn):
        with open(fn, mode="rb") as f:
            self.cookies = pickle.load(f)

    def dump(self, fn):
        with open(fn, mode="wb") as f:
            pickle.dump(self._sess.cookies, f)

    @property
    def cookies(self):
        return self._sess.cookies

    @cookies.setter
    def cookies(self, new_cookie):
        self._student_id = None
        self._sess.cookies = new_cookie
        self._sess.get(const.LOGIN_URL)  # refresh JSESSION token
        if "login" in self._sess.get(const.HOME_URL).url:
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

    def _elect(self, params):
        r = self._sess.post(const.ELECT_URL + self.student_id, data=params)
        return r.json()
