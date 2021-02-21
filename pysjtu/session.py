import io
import pickle
import re
import time
import warnings
from functools import partial
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union
from urllib.parse import parse_qs, urljoin, urlparse

import httpx
from httpx.auth import AuthTypes
from httpx.config import (ProxiesTypes, TimeoutTypes, UNSET, UnsetType)
from httpx.dispatch.base import SyncDispatcher
from httpx.models import (
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestData,
    RequestFiles,
    Response,
    URLTypes,
)

from pysjtu.ocr import JCSSRecognizer, Recognizer
from . import consts
from .exceptions import DumpWarning, LoadWarning, LoginException, ServiceUnavailable, SessionException
from .utils import FileTypes


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

    :param username: JAccount username.
    :param password: JAccount password.
    :param cookies: The cookie to be used on each request.
    :param ocr: The captcha :class:`Recognizer`.
    :param session_file: The file which a session is loaded from & saved to.
    :param retry: A list contains retry delays. If it's exhausted, an exception will be raised.
    :param proxies: The proxy to be used on each request.
    :param timeout: The timeout to be used on each request.
    :param base_url: Base url of backend APIs.
    :param _mocker_app: An WSGI application to send requests to (for debug or test purposes).
    """
    _client: httpx.Client  # httpx session
    _retry: list = [.5] * 5 + list(range(1, 5))  # retry list
    _ocr: Recognizer
    _username: str
    _password: str
    _session_file: Optional[FileTypes]
    _base_url: str

    def _secure_req(self, ref: Callable) -> Response:
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

    def __init__(self, username: str = "", password: str = "", cookies: CookieTypes = None, ocr: Recognizer = None,
                 session_file: FileTypes = None, retry: list = None, proxies: ProxiesTypes = None,
                 timeout: TimeoutTypes = None, base_url: str = "https://i.sjtu.edu.cn", _mocker_app=None):
        self._client = httpx.Client(app=_mocker_app, proxies=proxies)
        self._ocr = ocr if ocr else JCSSRecognizer()
        self._username = ""
        self._password = ""
        self._cache_store = {}
        self._base_url = base_url
        # noinspection PyTypeChecker
        self._session_file = None
        if retry:
            self._retry = retry
        if timeout:
            self.timeout = timeout

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
            data: RequestData = None,
            files: RequestFiles = None,
            json: Any = None,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        """
        Send a request. If asked, validate the current session and renew it when necessary.

        :param method: HTTP method for the new `Request` object: `GET`, `OPTIONS`,
            `HEAD`, `POST`, `PUT`, `PATCH`, or `DELETE`.
        :param url: URL for the new `Request` object.
        :param params: (optional) Query parameters to include in the URL, as a
            string, dictionary, or list of two-tuples.
        :param data: (optional) Data to include in the body of the request, as a
            dictionary.
        :param files: (optional) A dictionary of upload files to include in the
            body of the request.
        :param json: (optional) A JSON serializable object to include in the body
            of the request.
        :param headers: (optional) Dictionary of HTTP headers to include in the
            request.
        :param cookies: (optional) Dictionary of Cookie items to include in the
            request.
        :param auth: (optional) An authentication class to use when sending the
            request.
        :param timeout: (optional) The timeout configuration to use when sending
            the request.
        :param allow_redirects: (optional) Enables or disables HTTP redirects.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        # complete the url in case base_url is omitted
        url_parsed = urlparse(url)
        url = url if all([getattr(url_parsed, attr) for attr in ["scheme", "netloc", "path"]]) \
            else urljoin(self._base_url, url)
        rtn = self._client.request(method=method,
                                   url=url,
                                   data=data,
                                   files=files,
                                   json=json,
                                   params=params,
                                   headers=headers,
                                   cookies=cookies,
                                   auth=auth,
                                   allow_redirects=allow_redirects,
                                   timeout=timeout)
        try:
            rtn.raise_for_status()
        except httpx.exceptions.HTTPError as e:
            if rtn.status_code == httpx.codes.SERVICE_UNAVAILABLE:
                raise ServiceUnavailable
            raise e
        if validate_session and rtn.url.full_path == "/xtgl/login_slogin.html":  # type: ignore
            if not auto_renew:
                raise SessionException("Session expired.")
            self._secure_req(partial(self.get, consts.LOGIN_URL, validate_session=False))  # refresh token
            # Sometimes JAccount OAuth token isn't expired
            if self.get(consts.HOME_URL,
                        validate_session=False).url.full_path == "/xtgl/login_slogin.html":  # type: ignore
                if self._username and self._password:
                    self.login(self._username, self._password)
                else:
                    raise SessionException("Session expired. Unable to renew session due to missing username or "
                                           "password")
            return self.request(method=method,
                                url=url,
                                data=data,
                                files=files,
                                json=json,
                                params=params,
                                headers=headers,
                                cookies=cookies,
                                auth=auth,
                                allow_redirects=allow_redirects,
                                timeout=timeout,
                                validate_session=validate_session,
                                auto_renew=False)  # disable auto_renew to avoid infinite recursion
        else:
            return rtn

    def get(
            self,
            url: URLTypes,
            *,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        """
        Send a GET request. If asked, validate the current session and renew it when necessary.

        :param url: URL for the new `Request` object.
        :param params: (optional) Query parameters to include in the URL, as a
            string, dictionary, or list of two-tuples.
        :param headers: (optional) Dictionary of HTTP headers to include in the
            request.
        :param cookies: (optional) Dictionary of Cookie items to include in the
            request.
        :param auth: (optional) An authentication class to use when sending the
            request.
        :param timeout: (optional) The timeout configuration to use when sending
            the request.
        :param allow_redirects: (optional) Enables or disables HTTP redirects.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return self.request(
            "GET",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            allow_redirects=allow_redirects,
            timeout=timeout,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    def options(
            self,
            url: URLTypes,
            *,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        """
        Send a OPTIONS request. If asked, validate the current session and renew it when necessary.

        :param url: URL for the new `Request` object.
        :param params: (optional) Query parameters to include in the URL, as a
            string, dictionary, or list of two-tuples.
        :param headers: (optional) Dictionary of HTTP headers to include in the
            request.
        :param cookies: (optional) Dictionary of Cookie items to include in the
            request.
        :param auth: (optional) An authentication class to use when sending the
            request.
        :param timeout: (optional) The timeout configuration to use when sending
            the request.
        :param allow_redirects: (optional) Enables or disables HTTP redirects.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return self.request(
            "OPTIONS",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            allow_redirects=allow_redirects,
            timeout=timeout,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    def head(
            self,
            url: URLTypes,
            *,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = False,  # NOTE: Differs to usual default.
            timeout: Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        """
        Send a HEAD request. If asked, validate the current session and renew it when necessary.

        :param url: URL for the new `Request` object.
        :param params: (optional) Query parameters to include in the URL, as a
            string, dictionary, or list of two-tuples.
        :param headers: (optional) Dictionary of HTTP headers to include in the
            request.
        :param cookies: (optional) Dictionary of Cookie items to include in the
            request.
        :param auth: (optional) An authentication class to use when sending the
            request.
        :param timeout: (optional) The timeout configuration to use when sending
            the request.
        :param allow_redirects: (optional) Enables or disables HTTP redirects.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return self.request(
            "HEAD",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            allow_redirects=allow_redirects,
            timeout=timeout,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    def post(
            self,
            url: URLTypes,
            *,
            data: RequestData = None,
            files: RequestFiles = None,
            json: Any = None,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        """
        Send a POST request. If asked, validate the current session and renew it when necessary.

        :param url: URL for the new `Request` object.
        :param params: (optional) Query parameters to include in the URL, as a
            string, dictionary, or list of two-tuples.
        :param data: (optional) Data to include in the body of the request, as a
            dictionary.
        :param files: (optional) A dictionary of upload files to include in the
            body of the request.
        :param json: (optional) A JSON serializable object to include in the body
            of the request.
        :param headers: (optional) Dictionary of HTTP headers to include in the
            request.
        :param cookies: (optional) Dictionary of Cookie items to include in the
            request.
        :param auth: (optional) An authentication class to use when sending the
            request.
        :param timeout: (optional) The timeout configuration to use when sending
            the request.
        :param allow_redirects: (optional) Enables or disables HTTP redirects.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return self.request(
            "POST",
            url,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            allow_redirects=allow_redirects,
            timeout=timeout,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    def put(
            self,
            url: URLTypes,
            *,
            data: RequestData = None,
            files: RequestFiles = None,
            json: Any = None,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        """
        Send a PUT request. If asked, validate the current session and renew it when necessary.

        :param url: URL for the new `Request` object.
        :param params: (optional) Query parameters to include in the URL, as a
            string, dictionary, or list of two-tuples.
        :param data: (optional) Data to include in the body of the request, as a
            dictionary.
        :param files: (optional) A dictionary of upload files to include in the
            body of the request.
        :param json: (optional) A JSON serializable object to include in the body
            of the request.
        :param headers: (optional) Dictionary of HTTP headers to include in the
            request.
        :param cookies: (optional) Dictionary of Cookie items to include in the
            request.
        :param auth: (optional) An authentication class to use when sending the
            request.
        :param timeout: (optional) The timeout configuration to use when sending
            the request.
        :param allow_redirects: (optional) Enables or disables HTTP redirects.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return self.request(
            "PUT",
            url,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            allow_redirects=allow_redirects,
            timeout=timeout,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    def patch(
            self,
            url: URLTypes,
            *,
            data: RequestData = None,
            files: RequestFiles = None,
            json: Any = None,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        """
        Sends a PATCH request. If asked, validates the current session and renews it when necessary.

        :param url: URL for the new `Request` object.
        :param params: (optional) Query parameters to include in the URL, as a
            string, dictionary, or list of two-tuples.
        :param data: (optional) Data to include in the body of the request, as a
            dictionary.
        :param files: (optional) A dictionary of upload files to include in the
            body of the request.
        :param json: (optional) A JSON serializable object to include in the body
            of the request.
        :param headers: (optional) Dictionary of HTTP headers to include in the
            request.
        :param cookies: (optional) Dictionary of Cookie items to include in the
            request.
        :param auth: (optional) An authentication class to use when sending the
            request.
        :param timeout: (optional) The timeout configuration to use when sending
            the request.
        :param allow_redirects: (optional) Enables or disables HTTP redirects.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return self.request(
            "PATCH",
            url,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            allow_redirects=allow_redirects,
            timeout=timeout,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    def delete(
            self,
            url: URLTypes,
            *,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        """
        Sends a DELETE request. If asked, validates the current session and renews it when necessary.

        :param url: URL for the new `Request` object.
        :param params: (optional) Query parameters to include in the URL, as a
            string, dictionary, or list of two-tuples.
        :param headers: (optional) Dictionary of HTTP headers to include in the
            request.
        :param cookies: (optional) Dictionary of Cookie items to include in the
            request.
        :param auth: (optional) An authentication class to use when sending the
            request.
        :param timeout: (optional) The timeout configuration to use when sending
            the request.
        :param allow_redirects: (optional) Enables or disables HTTP redirects.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return self.request(
            "DELETE",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            allow_redirects=allow_redirects,
            timeout=timeout,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    def login(self, username: str, password: str):
        """
        Log in JAccount using given username & password.

        :param username: JAccount username.
        :param password: JAccount password.
        :raises LoginException: Failed to login after several attempts.
        """
        self._cache_store = {}
        for i in self._retry:
            login_page_req = self._secure_req(partial(self.get, consts.LOGIN_URL, validate_session=False, headers=consts.HEADERS))
            uuid = re.findall(r"(?<=uuid\": ').*(?=')", login_page_req.text)[0]
            login_params = {k: v[0] for k, v in parse_qs(urlparse(str(login_page_req.url)).query).items()}

            captcha_img = self.get(consts.CAPTCHA_URL,
                                   params={"uuid": uuid, "t": int(time.time() * 1000)}).content
            captcha = self._ocr.recognize(captcha_img)

            login_params.update({"v": "", "uuid": uuid, "user": username, "pass": password, "captcha": captcha})
            result = self._secure_req(
                partial(self.post, consts.LOGIN_POST_URL, params=login_params, headers=consts.HEADERS))
            if "err=" not in result.url.query:  # type: ignore
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
            if isinstance(d["cookies"], httpx.models.Cookies):
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
    def proxies(self) -> Dict[str, SyncDispatcher]:
        """ Get or set the proxy to be used on each request. """
        return self._client.proxies

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
        self._secure_req(partial(self.get, consts.LOGIN_URL, validate_session=False, headers=consts.HEADERS))  # refresh JSESSION token
        if self.get(consts.HOME_URL, validate_session=False).url.full_path == "/xtgl/login_slogin.html":  # type: ignore
            self._client.cookies = bak_cookie
            raise SessionException("Invalid cookies. You may skip this validation by setting _cookies")
        self._cache_store = {}

    @property
    def timeout(self) -> TimeoutTypes:
        """ Get or set the timeout to be used on each request. """
        return self._client.timeout

    @timeout.setter
    def timeout(self, new_timeout: TimeoutTypes):
        if isinstance(new_timeout, (tuple, float, int, httpx.Timeout)) or new_timeout is None:
            self._client.timeout = httpx.Timeout(new_timeout)
        else:
            raise TypeError

    @property
    def base_url(self) -> str:
        """ Base url of backend APIs. """
        return self._base_url
