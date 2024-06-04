import io
import pickle
import re
import time
import warnings
from functools import partial
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Callable, Optional, Union
from urllib.parse import parse_qs, urlparse

import httpx
from httpx import Response

from pysjtu.ocr import JCSSRecognizer, Recognizer
from . import consts
from .consts import CAPTCHA_REFERER
from .exceptions import DumpWarning, LoadWarning, LoginException, ServiceUnavailable, SessionException
from .utils import FileTypes

CookieTypes = Union[httpx.Cookies, CookieJar]
URLTypes = Union[httpx.URL, str]


class BaseSession:
    """ Base session """
    _cache_store: dict

    def get(self, *args, **kwargs):
        raise NotImplementedError  # pragma: no cover

    def post(self, *args, **kwargs):
        raise NotImplementedError  # pragma: no cover


class Session(BaseSession):
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

    For additional keyword arguments, see https://www.python-httpx.org/api.

    :param username: JAccount username.
    :param password: JAccount password.
    :param cookies: The cookie to be used on each request.
    :param ocr: The captcha :class:`Recognizer`.
    :param session_file: The file which a session is loaded from & saved to.
    :param retry: A list contains retry delays. If it's exhausted, an exception will be raised.
    :param base_url: Base url of backend APIs.
    """
    _client: httpx.Client  # httpx session
    _retry: list = [.5] * 5 + list(range(1, 5))  # retry list
    _ocr: Recognizer
    _username: str
    _password: str
    _session_file: Optional[FileTypes]

    def _secure_req(self, ref: Callable) -> Response:
        """
        Send a request using HTTPS explicitly to work around an upstream bug.

        :param ref: a partial request call.
        :return: the response of the original request.
        """
        try:
            return ref()
        except httpx.NetworkError as e:
            req = e.request
            if req.url.scheme != "https":
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

    def __init__(self, username: str = "", password: str = "", cookies: Optional[CookieTypes] = None,
                 ocr: Optional[Recognizer] = None, session_file: Optional[FileTypes] = None,
                 retry: Optional[list] = None, base_url: str = "https://i.sjtu.edu.cn", **kwargs):
        self._client = httpx.Client(follow_redirects=True, base_url=base_url, **kwargs)
        self._ocr = ocr if ocr else JCSSRecognizer(**kwargs)
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

        if username and password:
            self.loads({"username": username, "password": password})
        elif cookies:
            self.loads({"cookies": cookies})

    def request(
            self,
            method: str,
            url: URLTypes,
            *,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> Response:
        """
        Send a request. If asked, validate the current session and renew it when necessary.

        For additional keyword arguments, see https://www.python-httpx.org/api.

        :param method: HTTP method for the new `Request` object: `GET`, `OPTIONS`,
            `HEAD`, `POST`, `PUT`, `PATCH`, or `DELETE`.
        :param url: URL for the new `Request` object.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        """
        rtn = self._client.request(method, url=url, **kwargs)
        try:
            rtn.raise_for_status()
        except httpx.HTTPError as e:
            if rtn.status_code == httpx.codes.SERVICE_UNAVAILABLE:
                raise ServiceUnavailable
            raise e
        if validate_session and rtn.url.raw_path == b"/xtgl/login_slogin.html":  # type: ignore
            if not auto_renew:
                raise SessionException("Session expired.")
            self._secure_req(partial(self.get, consts.LOGIN_URL, validate_session=False))  # refresh token
            # Sometimes JAccount OAuth token isn't expired
            if self.get(consts.HOME_URL,
                        validate_session=False).url.raw_path == b"/xtgl/login_slogin.html":  # type: ignore
                if self._username and self._password:
                    self.login(self._username, self._password)
                else:
                    raise SessionException("Session expired. Unable to renew session due to missing username or "
                                           "password")
            return self.request(method, url,
                                validate_session=validate_session,
                                auto_renew=False,  # disable auto_renew to avoid infinite recursion
                                **kwargs)
        else:
            return rtn

    def get(
            self,
            url: URLTypes,
            *,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> Response:
        """
        Send a GET request. If asked, validate the current session and renew it when necessary.

        For additional keyword arguments, see https://www.python-httpx.org/api.

        :param url: URL for the new `Request` object.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        """
        return self.request(
            "GET",
            url,
            validate_session=validate_session,
            auto_renew=auto_renew,
            **kwargs
        )

    def options(
            self,
            url: URLTypes,
            *,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> Response:
        """
        Send a OPTIONS request. If asked, validate the current session and renew it when necessary.

        For additional keyword arguments, see https://www.python-httpx.org/api.

        :param url: URL for the new `Request` object.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        """
        return self.request(
            "OPTIONS",
            url,
            validate_session=validate_session,
            auto_renew=auto_renew,
            **kwargs
        )

    def head(
            self,
            url: URLTypes,
            *,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> Response:
        """
        Send a HEAD request. If asked, validate the current session and renew it when necessary.

        For additional keyword arguments, see https://www.python-httpx.org/api.

        :param url: URL for the new `Request` object.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        """
        return self.request(
            "HEAD",
            url,
            validate_session=validate_session,
            auto_renew=auto_renew,
            **kwargs
        )

    def post(
            self,
            url: URLTypes,
            *,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> Response:
        """
        Send a POST request. If asked, validate the current session and renew it when necessary.

        For additional keyword arguments, see https://www.python-httpx.org/api.

        :param url: URL for the new `Request` object.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        """
        return self.request(
            "POST",
            url,
            validate_session=validate_session,
            auto_renew=auto_renew,
            **kwargs
        )

    def put(
            self,
            url: URLTypes,
            *,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> Response:
        """
        Send a PUT request. If asked, validate the current session and renew it when necessary.

        For additional keyword arguments, see https://www.python-httpx.org/api.

        :param url: URL for the new `Request` object.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        """
        return self.request(
            "PUT",
            url,
            validate_session=validate_session,
            auto_renew=auto_renew,
            **kwargs
        )

    def patch(
            self,
            url: URLTypes,
            *,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> Response:
        """
        Sends a PATCH request. If asked, validates the current session and renews it when necessary.

        For additional keyword arguments, see https://www.python-httpx.org/api.

        :param url: URL for the new `Request` object.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        """
        return self.request(
            "PATCH",
            url,
            validate_session=validate_session,
            auto_renew=auto_renew,
            **kwargs
        )

    def delete(
            self,
            url: URLTypes,
            *,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> Response:
        """
        Sends a DELETE request. If asked, validates the current session and renews it when necessary.

        For additional keyword arguments, see https://www.python-httpx.org/api.

        :param url: URL for the new `Request` object.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        """
        return self.request(
            "DELETE",
            url,
            validate_session=validate_session,
            auto_renew=auto_renew,
            **kwargs
        )

    def login(self, username: str, password: str):
        """
        Log in JAccount using given username & password.

        :param username: JAccount username.
        :param password: JAccount password.
        :raises LoginException: Failed to log in after several attempts.
        """
        self._cache_store = {}
        for i in self._retry:
            login_page_req = self._secure_req(
                partial(self.get, consts.LOGIN_URL, validate_session=False, headers=consts.HEADERS))
            uuid = re.findall(r"(?<=uuid=).*(?=\")", login_page_req.text)[0]
            login_params = {k: v[0] for k, v in parse_qs(urlparse(str(login_page_req.url)).query).items()}

            captcha_img = self.get(consts.CAPTCHA_URL,
                                   params={"uuid": uuid, "t": int(time.time() * 1000)},
                                   headers={"Referer": CAPTCHA_REFERER}).content
            captcha = self._ocr.recognize(captcha_img)

            login_params.update({"v": "", "uuid": uuid, "user": username, "pass": password, "captcha": captcha})
            result = self._secure_req(
                partial(self.post, consts.LOGIN_POST_URL, params=login_params, headers=consts.HEADERS))
            if b"err=" not in result.url.query:  # type: ignore
                self._username = username
                self._password = password
                return

            time.sleep(i)

        raise LoginException

    def logout(self, purge_session: bool = True):
        """
        Log out JAccount.

        :param purge_session: (optional) Whether to purge local session info. May causes inconsistency, so use with
            caution.
        """
        cookie_bak = self._client.cookies
        self.get(consts.LOGOUT_URL, params={"t": int(time.time() * 1000), "login_type": ""}, validate_session=False)
        if purge_session:
            self._username = ''
            self._password = ''
        else:
            self._client.cookies = cookie_bak

    def loads(self, d: dict):
        """
        Read a session from a given dict. A warning will be given if username or password field is missing.

        :param d: a dict contains a session.
        """
        renew_required = True

        if "cookies" in d.keys() and d["cookies"]:
            if isinstance(d["cookies"], httpx.Cookies):
                cj = d["cookies"]  # type: ignore
            elif isinstance(d["cookies"], dict):
                cj = CookieJar()  # type: ignore
                # noinspection PyTypeHints
                cj._cookies = d["cookies"]  # type: ignore
            else:
                raise TypeError
            try:
                self.cookies = cj
                renew_required = False
            except SessionException:
                pass
        else:
            self._cookies = {}

        if "username" not in d.keys() or "password" not in d.keys() or not d["username"] or not d["password"]:
            warnings.warn("Missing username or password field", LoadWarning)
            self._username = ""
            self._password = ""
            renew_required = False
        else:
            self._username = d["username"]
            self._password = d["password"]

        if renew_required:
            self.login(self._username, self._password)

    def load(self, fp: FileTypes):
        """
        Read a session from a given file. A warning will be given if username or password field is missing.

        :param fp: a binary file object / filepath contains a session.
        """
        if isinstance(fp, (io.RawIOBase, io.BufferedIOBase)):
            try:
                conf = pickle.load(fp)
            except EOFError:
                conf = {}
        elif isinstance(fp, (str, Path)):
            try:
                with open(fp, mode="rb") as f:
                    conf = pickle.load(f)
            except EOFError:
                conf = {}
        else:
            raise TypeError
        self.loads(conf)

    # noinspection PyProtectedMember
    def dumps(self) -> dict:
        """
        Return a dict represents the current session. A warning will be given if username or password field is missing.

        :return: a dict represents the current session.
        """
        if not self._username or not self._password:
            warnings.warn("Missing username or password field", DumpWarning)
        return {"username": self._username, "password": self._password,
                "cookies": self._client.cookies.jar._cookies}  # type: ignore

    def dump(self, fp: FileTypes):
        """
        Write the current session to a given file. A warning will be given if username or password field is missing.

        :param fp: a binary file object/ filepath as the destination of session data.
        """
        if isinstance(fp, (io.RawIOBase, io.BufferedIOBase)):
            pickle.dump(self.dumps(), fp)
        elif isinstance(fp, (str, Path)):
            with open(fp, mode="wb") as f:
                pickle.dump(self.dumps(), f)
        else:
            raise TypeError

    @property
    def _cookies(self) -> CookieTypes:
        """ Get or set the cookie to be used on each request. This protected property skips session validation. """
        return self._client.cookies

    @_cookies.setter
    def _cookies(self, new_cookie: CookieTypes):
        self._cache_store = {}
        # noinspection PyTypeHints
        self._client.cookies = new_cookie  # type: ignore

    @property
    def cookies(self) -> CookieTypes:
        """
        Get or set the cookie to be used on each request. Session validation is performed on each set event.

        :raises SessionException: when given cookie doesn't contain a valid session.
        """
        return self._client.cookies

    @cookies.setter
    def cookies(self, new_cookie: CookieTypes):
        bak_cookie = self._client.cookies
        # noinspection PyTypeHints
        self._client.cookies = new_cookie  # type: ignore
        self._secure_req(partial(self.get, consts.LOGIN_URL, validate_session=False,
                                 headers=consts.HEADERS))  # refresh JSESSION token
        if self.get(consts.HOME_URL, validate_session=False).url.raw_path == b"/xtgl/login_slogin.html":  # type: ignore
            self._client.cookies = bak_cookie
            raise SessionException("Invalid cookies. You may skip this validation by setting _cookies")
        self._cache_store = {}

    @property
    def timeout(self) -> httpx.Timeout:
        """ Get or set the timeout to be used on each request. """
        return self._client.timeout

    @timeout.setter
    def timeout(self, new_timeout: httpx.Timeout):
        self._client.timeout = new_timeout

    @property
    def base_url(self) -> httpx.URL:
        """ Base url of backend APIs. """
        return self._client.base_url
