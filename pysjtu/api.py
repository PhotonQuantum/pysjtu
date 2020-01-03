import re
import requests
import functools
from json.decoder import JSONDecodeError
from . import model
from . import const

class SessionException(Exception):
    pass

class Session:
    def __init__(self):
        self._sess = requests.session()

    @property
    @functools.lru_cache
    def student_id(self):
        print("getting id")
        rtn = self._sess.get(const.HOME_URL)
        return re.findall(r"(?<=id=\"sessionUserKey\" value=\")\d*", rtn.text)[0]

    @property
    def cookies(self):
        return self._sess.cookies

    @cookies.setter
    def cookies(self, new_cookie):
        Session.student_id.fget.cache_clear()
        self._sess.cookies = new_cookie

    def schedule(self, year, term):
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
