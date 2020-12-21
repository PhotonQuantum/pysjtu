import pickle
from datetime import date
from functools import partial
from tempfile import NamedTemporaryFile

import httpx
import pytest
import respx

from pysjtu.client import Client, create_client
from pysjtu.exceptions import DumpWarning, GPACalculationException, LoadWarning, LoginException, ServiceUnavailable, \
    SessionException, SelectionNotAvailableException, TimeConflictException, FullCapacityException
from pysjtu.models import CourseRange, Exams, GPA, GPAQueryParams, LogicEnum, QueryResult, Schedule, Scores, Profile
from pysjtu.ocr import JCSSRecognizer
from pysjtu.session import BaseSession, Session
from .mock_server import app
from dataclasses import asdict


@pytest.fixture
def logged_session(mocker):
    mocker.patch.object(JCSSRecognizer, "recognize", return_value="ipsum")
    sess = Session(_mocker_app=app, retry=[0], timeout=1)
    sess.login("FeiLin", "WHISPERS")
    return sess


@pytest.fixture
def check_login():
    def _check_login(session):
        return "519027910001" in session.get("https://i.sjtu.edu.cn/xtgl/index_initMenu.html").text

    return _check_login


class TestSession:
    @respx.mock
    def test_base_url(self):
        respx.get("https://i.sjtu.edu.cn/test", content="1")
        respx.get("https://kbcx.sjtu.edu.cn/test", content="2")
        sess = Session()
        assert sess.base_url == "https://i.sjtu.edu.cn"
        assert sess.get("/test").text == "1"
        sess_2 = Session(base_url="https://kbcx.sjtu.edu.cn")
        assert sess_2.base_url == "https://kbcx.sjtu.edu.cn"
        assert sess_2.get("/test").text == "2"

    @respx.mock
    def test_secure_req(self):
        respx.get("http://secure.page.edu.cn", content=httpx.ConnectionClosed())
        respx.get("http://secure.page.edu.cn:8889", content=httpx.ConnectionClosed())
        respx.get("https://fail.page.edu.cn", content=httpx.ConnectionClosed())
        respx.get("https://secure.page.edu.cn")
        sess = Session()

        resp = sess._secure_req(partial(httpx.get, "http://secure.page.edu.cn"))
        assert resp.status_code == 200

        resp = sess._secure_req(partial(httpx.get, "http://secure.page.edu.cn:8889"))
        assert resp.status_code == 200

        with pytest.raises(httpx.exceptions.NetworkError):
            sess._secure_req(partial(httpx.get, "https://fail.page.edu.cn"))

    def test_context(self, mocker):
        tmpfile = NamedTemporaryFile()
        pickle.dump({"username": "FeiLin", "password": "WHISPERS"}, tmpfile)
        tmpfile.seek(0)

        mocker.patch.object(JCSSRecognizer, "recognize", return_value="ipsum")
        with Session(_mocker_app=app, session_file=tmpfile.file):
            pass
        tmpfile.seek(0)

        assert pickle.load(tmpfile)["cookies"]

    def test_init(self, mocker, check_login):
        tmpfile = NamedTemporaryFile()
        mocker.patch.object(JCSSRecognizer, "recognize", return_value="ipsum")
        sess = Session(_mocker_app=app, username="FeiLin", password="WHISPERS")
        assert check_login(sess)
        cookie = sess.cookies
        sess.dump(tmpfile.file)
        tmpfile.seek(0)

        with pytest.warns(LoadWarning):
            sess = Session(_mocker_app=app, cookies=cookie)
            assert check_login(sess)

        sess = Session(_mocker_app=app, session_file=tmpfile.file)
        assert check_login(sess)

    def test_req(self, logged_session, check_login):
        with pytest.raises(ServiceUnavailable):
            logged_session.get("https://i.sjtu.edu.cn/503")

        logged_session.get("https://i.sjtu.edu.cn/expire_me")
        assert logged_session.get("https://i.sjtu.edu.cn/xtgl/index_initMenu.html",
                                  validate_session=False).url.full_path == "/xtgl/login_slogin.html"
        with pytest.raises(SessionException):
            logged_session.get("https://i.sjtu.edu.cn/xtgl/index_initMenu.html", auto_renew=False)
        assert check_login(logged_session)

        logged_session.get("https://i.sjtu.edu.cn/expire_me")
        logged_session._username = None
        with pytest.raises(SessionException):
            logged_session.get("https://i.sjtu.edu.cn/xtgl/index_initMenu.html")

        with pytest.raises(httpx.exceptions.HTTPError):
            logged_session.get("https://i.sjtu.edu.cn/404")

    def test_req_methods(self, logged_session):
        assert logged_session.get("https://i.sjtu.edu.cn/ping").text == "pong"
        logged_session.head("https://i.sjtu.edu.cn/ping")
        assert logged_session.post("https://i.sjtu.edu.cn/ping", data="lorem ipsum").text == "lorem ipsum"
        assert logged_session.patch("https://i.sjtu.edu.cn/ping").text == "pong"
        assert logged_session.put("https://i.sjtu.edu.cn/ping").text == "pong"
        assert logged_session.delete("https://i.sjtu.edu.cn/ping").text == "pong"
        options = logged_session.options("https://i.sjtu.edu.cn/ping").headers["allow"]
        assert sorted(options.split(", ")) == ['DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT']

    @respx.mock
    def test_req_partial_url(self):
        respx.get("http://dummy.url/test_path", content="pass")
        assert Session(base_url="http://dummy.url").get("/test_path").text == "pass"

    def test_login(self, logged_session, check_login):
        assert check_login(logged_session)

        with pytest.raises(LoginException):
            logged_session.login("Cookie☆", "1145141919810")
            logged_session.login("Cookie☆", "buriburiburi")

    def test_logout(self, logged_session, check_login):
        logged_session.logout(purge_session=False)
        assert logged_session.get("https://i.sjtu.edu.cn/is_login").text == "False"
        assert check_login(logged_session)

        logged_session.logout()
        with pytest.raises(SessionException):
            logged_session.get("https://i.sjtu.edu.cn/xtgl/index_initMenu.html")

    def test_loads_dumps(self, logged_session, check_login):
        cookie = logged_session.cookies
        dumps = logged_session.dumps()

        sess = Session(_mocker_app=app)
        sess.loads({"username": "FeiLin", "password": "WHISPERS"})
        assert check_login(sess)

        with pytest.warns(LoadWarning):
            sess.loads({})
        assert sess.cookies == httpx.Cookies({})
        assert not sess._username
        assert not sess._password

        sess = Session(_mocker_app=app)
        with pytest.raises(TypeError):
            sess.loads({"cookies": "Cookie☆"})
        with pytest.warns(LoadWarning):
            sess.loads({"cookies": {}})
            sess.loads({"cookies": cookie})
        assert check_login(sess)
        with pytest.warns(DumpWarning):
            sess.dumps()

        sess = Session(_mocker_app=app)
        sess.loads(dumps)
        assert check_login(sess)

        # test auto renew mechanism
        logged_session.logout()
        sess = Session(_mocker_app=app)
        sess.loads(dumps)
        assert check_login(sess)

    def test_load_dump(self, logged_session, check_login, tmp_path):
        tmp_file = NamedTemporaryFile()
        logged_session.dump(tmp_file.file)
        tmp_file.seek(0)
        sess = Session(_mocker_app=app)
        sess.load(tmp_file.file)
        assert check_login(sess)

        tmp_file = tmp_path / "tmpfile_1"
        # noinspection PyTypeChecker
        open(tmp_file, mode="a").close()
        logged_session.dump(tmp_file)
        sess = Session(_mocker_app=app)
        sess.load(tmp_file)
        assert check_login(sess)

        tmp_file = str(tmp_path / "tmpfile_2")
        open(tmp_file, mode="a").close()
        logged_session.dump(tmp_file)
        sess = Session(_mocker_app=app)
        sess.load(tmp_file)
        assert check_login(sess)

        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            sess.load(0)
        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            sess.dump(0)

        empty_file = NamedTemporaryFile()
        sess = Session(_mocker_app=app)
        with pytest.warns(LoadWarning):
            sess.load(empty_file.file)

        empty_file = tmp_path / "empty_file"
        # noinspection PyTypeChecker
        open(empty_file, mode="a").close()
        sess = Session(_mocker_app=app)
        with pytest.warns(LoadWarning):
            sess.load(empty_file)

    def test_properties(self, logged_session):
        cookie = logged_session.cookies

        sess = Session(_mocker_app=app)
        assert sess.proxies == {}

        assert isinstance(sess.timeout, httpx.Timeout)
        sess.timeout = httpx.Timeout(1.0)
        sess.timeout = 1
        sess.timeout = (1, 5)
        with pytest.raises(TypeError):
            sess.timeout = "1"

        assert isinstance(sess.cookies, httpx.Cookies)
        with pytest.raises(SessionException):
            sess.cookies = {}
        sess._cookies = {}
        sess._cache_store = {"key": "value"}
        sess.cookies = cookie
        assert sess._cache_store == {}
        assert sess._cookies == sess.cookies


@pytest.fixture
def logged_client(logged_session):
    return Client(logged_session)


class TestClient:
    class DummySession(BaseSession):
        _cache_store = {}

        def get(self): ...

        def post(self): ...

    class DummySession2:
        def get(self): ...

        def post(self): ...

    # noinspection PyTypeChecker
    def test_init(self, logged_session):
        Client(logged_session)
        Client(self.DummySession())
        with pytest.raises(TypeError):
            Client(0)
        with pytest.raises(TypeError):
            Client(self.DummySession2())
        client = create_client("FeiLin", "WHISPERS", _mocker_app=app)
        assert client.student_id == 519027910001

    def test_student_id(self, logged_client):
        assert logged_client.student_id == 519027910001

    def test_term_start_date(self, logged_client):
        assert logged_client.term_start_date == date(2019, 9, 9)

    def test_gpa_query_params(self, logged_client):
        assert isinstance(logged_client.default_gpa_query_params, GPAQueryParams)

    def test_schedule(self, logged_client):
        schedule = logged_client.schedule(2019, 0)
        assert isinstance(schedule, Schedule)
        assert len(schedule) == 3

    def test_get_score(self, logged_client):
        score = logged_client.score(2019, 0)
        assert isinstance(score, Scores)
        assert len(score) == 3
        assert len(score[0].detail) == 2

    def test_exam(self, logged_client):
        exam = logged_client.exam(2019, 0)
        assert isinstance(exam, Exams)
        assert len(exam) == 3

    def test_course(self, logged_client):
        courses = logged_client.query_courses(2019, 0, name="高等数学", page_size=40)
        assert isinstance(courses, QueryResult)
        assert len(courses) == 90
        assert len(list(courses)) == 90

    def test_gpa_fail(self, logged_client):
        params = logged_client.default_gpa_query_params
        params.condition_logic = LogicEnum.AND
        with pytest.raises(GPACalculationException) as e:
            logged_client.gpa(params)
        assert str(e.value) == "Unauthorized."
        params.condition_logic = LogicEnum.OR
        params.course_range = CourseRange.ALL
        with pytest.raises(GPACalculationException) as e:
            logged_client.gpa(params)
        assert str(e.value) == "Calculation failure."
        params.course_range = CourseRange.CORE
        gpa = logged_client.gpa(params)
        assert isinstance(gpa, GPA)

    def test_selection(self, logged_client):
        with pytest.raises(SelectionNotAvailableException):
            sectors = logged_client.course_selection_sectors
        logged_client._session.get("/test_selection")
        for _ in range(3):
            sectors = logged_client.course_selection_sectors
        assert logged_client._session.get("get_session?key=query_all_sectors").text == "3"
        assert len(sectors) == 6

        for _ in range(3):
            classes = sectors[0].classes
        assert logged_client._session.get("get_session?key=query_courses").text == "1"
        _ = logged_client.course_selection_sectors[0].classes
        assert logged_client._session.get("get_session?key=query_courses").text == "2"

        # noinspection PyUnboundLocalVariable
        _class = classes[0]
        with pytest.raises(TimeConflictException):
            _class.register()
        logged_client._session.get("test_no_conflict")
        with pytest.raises(FullCapacityException):
            _class.register()
        logged_client._session.get("test_no_full")
        _class.register()
        assert _class.is_registered() is True
        _class.deregister()
        assert _class.is_registered() is False

        _ = _class.register_id
        assert logged_client._session.get("get_session?key=query_classes").text == "1"
        logged_client.flush_selection_class_cache()
        _ = logged_client.course_selection_sectors[0].classes[0].register_id
        assert logged_client._session.get("get_session?key=query_classes").text == "2"

    def test_profile(self, logged_client):
        profile_1 = logged_client.profile
        assert isinstance(profile_1, Profile)
        assert logged_client._session.get("get_session?key=query_profile").text == "1"

        profile_2 = logged_client.profile
        assert profile_1 == profile_2
        assert logged_client._session.get("get_session?key=query_profile").text == "1"
