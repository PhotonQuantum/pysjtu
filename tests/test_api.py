import pickle
from functools import partial
from tempfile import NamedTemporaryFile

import httpx
import pytest
import respx

from pysjtu.api import Session
from pysjtu.const import *
from pysjtu.exceptions import *
from pysjtu.ocr import NNRecognizer
from .mock_server import app


@pytest.fixture
def logged_session(mocker):
    mocker.patch.object(NNRecognizer, "recognize", return_value="ipsum")
    sess = Session(_mocker_app=app, retry=[0])
    sess.login("FeiLin", "WHISPERS")
    return sess


@pytest.fixture(scope="session")
def mocked_api():
    with respx.mock() as httpx_mock:
        httpx_mock.get(HOME_URL, content="asdf")


@pytest.fixture
def buggy_request():
    def _buggy_request():
        httpx.get("http://secure.page.edu.cn")

    return _buggy_request


@pytest.fixture
def check_login():
    def _check_login(session):
        return "519027910001" in session.get("https://i.sjtu.edu.cn/xtgl/index_initMenu.html").text
    return _check_login


class TestSession:
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

        mocker.patch.object(NNRecognizer, "recognize", return_value="ipsum")
        with Session(_mocker_app=app, session_file=tmpfile.file) as sess:
            pass
        tmpfile.seek(0)

        assert pickle.load(tmpfile)["cookies"]

    def test_init(self, mocker, check_login):
        tmpfile = NamedTemporaryFile()
        mocker.patch.object(NNRecognizer, "recognize", return_value="ipsum")
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

    def test_login(self, logged_session, check_login):
        assert check_login(logged_session)

        with pytest.raises(LoginException):
            logged_session.login("Cookie☆", "1145141919810")

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
            sess.load(0)
        with pytest.raises(TypeError):
            sess.dump(0)

    def test_properties(self, logged_session):
        cookie = logged_session.cookies

        sess = Session(_mocker_app=app)
        assert sess.proxies == {}
        sess.proxies = {"http": "http://127.0.0.1:8080"}

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
