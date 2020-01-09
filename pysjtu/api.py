import re
import time
import pickle
import requests
import functools
from urllib.parse import urlparse, parse_qs
from json.decoder import JSONDecodeError
from . import model
from . import const
from . import util
from typing import List

class SessionException(Exception):
    pass


class Session:
    _retry = [.5] * 5 + list(range(1, 5))

    def __init__(self, retry=None):
        self._sess = requests.session()
        if retry: self._retry = retry

    def login(self, username, password):
        for i in self._retry:
            login_page_req = self._sess.get(const.LOGIN_URL)
            uuid = re.findall(r"(?<=uuid\": ').*(?=')", login_page_req.text)[0]
            login_params = parse_qs(urlparse(login_page_req.url).query)
            login_params = dict(map(lambda x: (x[0], x[1][0]), login_params.items()))

            captcha_img = self._sess.get(const.CAPTCHA_URL, params={"uuid": uuid, "t": int(time.time() * 1000)}).content
            captcha = util.recognize_captcha(captcha_img)

            login_params.update({"v": "", "uuid": uuid, "user": username, "pass": password, "captcha": captcha})
            result = self._sess.post(const.LOGIN_POST_URL, params=login_params, headers=const.headers)
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
        Session.student_id.fget.cache_clear()
        self._sess.cookies = new_cookie
        self._sess.get(const.LOGIN_URL) # refresh JSESSION token
        if "login" in self._sess.get(const.HOME_URL).url:
            raise SessionException

    @property
    @functools.lru_cache
    def student_id(self):
        rtn = self._sess.get(const.HOME_URL)
        return re.findall(r"(?<=id=\"sessionUserKey\" value=\")\d*", rtn.text)[0]

    def schedule(self, year, term) -> model.Schedule:
        raw = self._sess.post(const.SCHEDULE_URL, data={"xnm": year, "xqm": const.TERMS[term]})
        schedule = model.Schedule()
        try:
            schedule.load(raw.json()["kbList"])
        except JSONDecodeError:
            raise SessionException
        return schedule

    def _elect(self, params):
        r = self._sess.post(const.ELECT_URL + self.student_id, data=params)
        return r.json()
