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


@respx.mock
def test_session_secure_req():
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


def test_session_login(logged_session):
    assert "519027910001" in logged_session.get("https://i.sjtu.edu.cn/xtgl/index_initMenu.html").text

    with pytest.raises(LoginException):
        logged_session.login("Cookie☆", "1145141919810")


def test_session_context(mocker, logged_session):
    tmpfile = NamedTemporaryFile()
    pickle.dump({"username": "FeiLin", "password": "WHISPERS"}, tmpfile)
    tmpfile.seek(0)

    mocker.patch.object(NNRecognizer, "recognize", return_value="ipsum")
    with Session(_mocker_app=app, session_file=tmpfile.file) as sess:
        pass
    tmpfile.seek(0)

    assert pickle.load(tmpfile)["cookies"]


def test_session_req(logged_session):
    with pytest.raises(ServiceUnavailable):
        logged_session.get("https://i.sjtu.edu.cn/503")

    logged_session.get("https://i.sjtu.edu.cn/expire_me")
    assert logged_session.get("https://i.sjtu.edu.cn/xtgl/index_initMenu.html",
                              validate_session=False).url.full_path == "/xtgl/login_slogin.html"
    with pytest.raises(SessionException):
        logged_session.get("https://i.sjtu.edu.cn/xtgl/index_initMenu.html", auto_renew=False)
    assert "519027910001" in logged_session.get("https://i.sjtu.edu.cn/xtgl/index_initMenu.html").text

    logged_session.get("https://i.sjtu.edu.cn/expire_me")
    logged_session._username = None
    with pytest.raises(SessionException):
        logged_session.get("https://i.sjtu.edu.cn/xtgl/index_initMenu.html")

    with pytest.raises(httpx.exceptions.HTTPError):
        logged_session.get("https://i.sjtu.edu.cn/404")
