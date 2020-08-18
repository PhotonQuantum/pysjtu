import asyncio
import datetime
import inspect
import io
import pickle
import re
import time
import warnings
from collections import defaultdict
from functools import partial
import http.cookies
from http.cookies import Morsel, SimpleCookie
from pathlib import Path
from typing import Callable, Mapping, Optional, cast
from urllib.parse import parse_qs, urljoin, urlparse

import aiohttp
from aiohttp import ClientResponse
from yarl import URL
from aiohttp.cookiejar import CookieJar
from aiohttp.helpers import is_ip_address
from aiohttp.typedefs import LooseCookies

from pysjtu.ocr import NNRecognizer, Recognizer
from . import consts
from .exceptions import DumpWarning, LoadWarning, LoginException, SessionException
from .utils import FileTypes

http.cookies._is_legal_key = lambda x: True

class MyCookieJar(CookieJar):
    def _do_expiration(self) -> None:
        now = datetime.datetime.now(datetime.timezone.utc)
        if self._next_expiration > now:
            return
        if not self._expirations:
            return
        next_expiration = self.MAX_TIME
        to_del = []
        cookies = self._cookies
        expirations = self._expirations
        for (domain, path, name), when in expirations.items():
            if when <= now:
                cookies[(domain, path)].pop(name, None)
                to_del.append((domain, path, name))
                self._host_only_cookies.discard((domain, path, name))
            else:
                next_expiration = min(next_expiration, when)
        for key in to_del:
            del expirations[key]

        try:
            self._next_expiration = (next_expiration.replace(microsecond=0) +
                                     datetime.timedelta(seconds=1))
        except OverflowError:
            self._next_expiration = self.MAX_TIME

    def _expire_cookie(self, when: datetime.datetime, domain: str, path: str, name: str) -> None:
        self._next_expiration = min(self._next_expiration, when)
        self._expirations[(domain, path, name)] = when

    def update_cookies(self,
                       cookies: LooseCookies,
                       response_url: URL=URL()) -> None:
        """Update cookies."""
        hostname = response_url.raw_host

        if not self._unsafe and is_ip_address(hostname):
            # Don't accept cookies from IPs
            return

        if isinstance(cookies, Mapping):
            cookies = cookies.items()  # type: ignore

        for name, cookie in cookies:
            if not isinstance(cookie, Morsel):
                tmp = SimpleCookie()
                tmp[name] = cookie  # type: ignore
                cookie = tmp[name]

            path = cookie["path"]
            if not path or not path.startswith("/"):
                # Set the cookie's path to the response path
                path = response_url.path
                if not path.startswith("/"):
                    path = "/"
                else:
                    # Cut everything from the last slash to the end
                    path = "/" + path[1:path.rfind("/")]
                cookie["path"] = path

            domain = cookie["domain"]

            # ignore domains with trailing dots
            if domain.endswith('.'):
                domain = ""
                del cookie["domain"]

            if not domain and hostname is not None:
                # Set the cookie's domain to the response hostname
                # and set its host-only-flag
                self._host_only_cookies.add((hostname, path, name))
                domain = cookie["domain"] = hostname

            if domain.startswith("."):
                # Remove leading dot
                domain = domain[1:]
                cookie["domain"] = domain

            if hostname and not self._is_domain_match(domain, hostname):
                # Setting cookies for different domains is not allowed
                continue

            max_age = cookie["max-age"]
            if max_age:
                try:
                    delta_seconds = int(max_age)
                    try:
                        max_age_expiration = (
                                datetime.datetime.now(datetime.timezone.utc) +
                                datetime.timedelta(seconds=delta_seconds))
                    except OverflowError:
                        max_age_expiration = self.MAX_TIME
                    self._expire_cookie(max_age_expiration,
                                        domain, path, name)
                except ValueError:
                    cookie["max-age"] = ""

            else:
                expires = cookie["expires"]
                if expires:
                    expire_time = self._parse_date(expires)
                    if expire_time:
                        self._expire_cookie(expire_time,
                                            domain, path, name)
                    else:
                        cookie["expires"] = ""

            self._cookies[(domain, path)][name] = cookie

        self._do_expiration()
    def filter_cookies(self, request_url: URL=URL()):
        """Returns this jar's cookies filtered by their attributes."""
        self._do_expiration()
        request_url = URL(request_url)
        filtered = SimpleCookie()
        hostname = request_url.raw_host or ""
        is_not_secure = request_url.scheme not in ("https", "wss")

        for cookie in self:
            name = cookie.key
            domain = cookie["domain"]
            path = cookie["path"]

            # Send shared cookies
            if not domain:
                filtered[name] = cookie.value
                continue

            if not self._unsafe and is_ip_address(hostname):
                continue

            if (domain, path, name) in self._host_only_cookies:
                if domain != hostname:
                    continue
            elif not self._is_domain_match(domain, hostname):
                continue

            if not self._is_path_match(request_url.path, path):
                continue

            if is_not_secure and cookie["secure"]:
                continue

            # It's critical we use the Morsel so the coded_value
            # (based on cookie version) is preserved
            mrsl_val = cast('Morsel[str]', cookie.get(cookie.key, Morsel()))
            mrsl_val.set(cookie.key, cookie.value, cookie.coded_value)
            filtered[name] = mrsl_val

        return filtered

    def save_dict(self) -> dict:
        def serialize_morsel(morsel: Morsel) -> dict:
            morsel_dict = {
                "key": morsel.key,
                "value": morsel.value,
                "coded_value": morsel.coded_value
            }
            morsel_dict.update(dict(morsel))
            return morsel_dict

        return {host: {key: serialize_morsel(morsel) for key, morsel in cookies.items()} for host, cookies in
                self._cookies.items()}

    def load_dict(self, cookie_jar: dict):
        def deserialize_morsel(morsel_dict: dict) -> Morsel:
            _morsel_dict = morsel_dict.copy()
            morsel = Morsel()
            morsel.set(_morsel_dict.pop("key"), _morsel_dict.pop("value"), _morsel_dict.pop("coded_value"))
            morsel.update(_morsel_dict)
            return morsel

        deserialize_cookie = lambda cookie_dict: SimpleCookie(cookie_dict)

        _cookies = {host: deserialize_cookie({key: deserialize_morsel(morsel) for key, morsel in cookies.items()}) for
                    host, cookies in cookie_jar.items()}
        self._cookies = defaultdict(SimpleCookie, _cookies)


class BaseSession:
    """ Base session """
    _cache_store: dict

    async def get(self, *args, **kwargs):
        raise NotImplementedError  # pragma: no cover

    async def post(self, *args, **kwargs):
        raise NotImplementedError  # pragma: no cover


class AsyncSession(BaseSession):
    """
    A pysjtu session with login management, cookie persistence, etc.

    Usage::

        >>> import pysjtu
        >>> s = pysjtu.AsyncSession()
        >>> s.login('user@sjtu.edu.cn', 'something_secret')
        >>> s.get('https://i.sjtu.edu.cn')
        <Response [200 OK]>
        >>> s.dump('session_file')

    Or as a context manager::

        >>> with pysjtu.AsyncSession(username='user@sjtu.edu.cn', password='something_secret') as s:
        ...     s.get('https://i.sjtu.edu.cn')
        ...     s.dump('session_file')
        <Response [200 OK]>

        >>> with pysjtu.AsyncSession(session_file='session_file', mode='r+b')) as s:
        ...     s.get('https://i.sjtu.edu.cn')
        <Response [200 OK]>

    :param username: JAccount username.
    :param password: JAccount password.
    :param cookies: The cookie to be used on each request.
    :param ocr: The captcha :class:`Recognizer`.
    :param session_file: The file which a session is loaded from & saved to.
    :param retry: A list contains retry delays. If it's exhausted, an exception will be raised.
    :param timeout: The timeout to be used on each request.
    :param base_url: Base url of backend APIs.
    :param _mocker_app: An WSGI application to send requests to (for debug or test purposes).
    """
    _client: aiohttp.ClientSession  # httpx session
    _retry: list = [.5] * 5 + list(range(1, 5))  # retry list
    _ocr: Recognizer
    _username: str
    _password: str
    _session_file: Optional[FileTypes]
    _base_url: str
    _renew_required: bool
    _login_lock: asyncio.Lock

    async def _secure_req(self, ref: Callable) -> ClientResponse:
        """
        Send a request using HTTPS explicitly to work around an upstream bug.

        :param ref: a partial request call.
        :return: the response of the original request.
        """
        return await ref()
        # try:
        #     return ref()
        # except httpx.exceptions.NetworkError as e:
        #     req = e.request
        #     if not req.url.is_ssl:
        #         req.url = req.url.copy_with(scheme="https", port=None)
        #     else:
        #         raise e
        #     return await self._client.send(req)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.close()
        if self._session_file:
            if isinstance(self._session_file, (io.RawIOBase, io.BufferedIOBase)):
                self._session_file.seek(0)
            self.dump(self._session_file)

    def __init__(self, username: str = "", password: str = "", cookies=None, ocr: Recognizer = None,
                 session_file: FileTypes = None, retry: list = None,
                 timeout=None, base_url: str = "https://i.sjtu.edu.cn", _mocker_app=None):
        self._client = aiohttp.ClientSession(cookie_jar=MyCookieJar())
        self._ocr = ocr if ocr else NNRecognizer()
        self._username = ""
        self._password = ""
        self._cache_store = {}
        self._base_url = base_url
        # noinspection PyTypeChecker
        self._session_file = None
        self._renew_required = False
        self._login_lock = asyncio.Lock()
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

    async def request(
            self,
            method: str,
            url: str,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs,
    ) -> ClientResponse:
        """
        Send a request. If asked, validate the current session and renew it when necessary.

        :param method: HTTP method for the new `Request` object: `GET`, `OPTIONS`,
            `HEAD`, `POST`, `PUT`, `PATCH`, or `DELETE`.
        :param url: URL for the new `Request` object.
        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        if validate_session:
            if self._renew_required:
                await self.login(self._username, self._password)
            while self._login_lock.locked():
                await asyncio.sleep(100)
        # complete the url in case base_url is omitted
        url_parsed = urlparse(url)
        url = url if all([getattr(url_parsed, attr) for attr in ["scheme", "netloc", "path"]]) \
            else urljoin(self._base_url, url)
        rtn = await self._client.request(method, url, **kwargs)
        rtn.raise_for_status()
        # try:
        #     rtn.raise_for_status()
        # except httpx.exceptions.HTTPError as e:
        #     if rtn.status_code == httpx.codes.SERVICE_UNAVAILABLE:
        #         raise ServiceUnavailable
        #     raise e
        if validate_session and rtn.url.path == "/xtgl/login_slogin.html":  # type: ignore
            if not auto_renew:
                raise SessionException("Session expired.")
            async with self._login_lock:
                await self._secure_req(partial(self.get, consts.LOGIN_URL, validate_session=False))  # refresh token
                # Sometimes JAccount OAuth token isn't expired
                if (await self.get(consts.HOME_URL,
                                   validate_session=False)).url.path == "/xtgl/login_slogin.html":  # type: ignore
                    if self._username and self._password:
                        await self.login(self._username, self._password)
                    else:
                        raise SessionException("Session expired. Unable to renew session due to missing username or "
                                               "password")
            # disable auto_renew to avoid infinite recursion
            return await self.request(method, url, **kwargs, validate_session=validate_session, auto_renew=False)
        else:
            return rtn

    async def get(
            self,
            url,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> ClientResponse:
        """
        Send a GET request. If asked, validate the current session and renew it when necessary.

        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return await self.request(
            "GET", url, **kwargs,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    async def options(
            self,
            url,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> ClientResponse:
        """
        Send a OPTIONS request. If asked, validate the current session and renew it when necessary.

        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return await self.request(
            "OPTIONS",
            url,
            **kwargs,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    async def head(
            self,
            url,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> ClientResponse:
        """
        Send a HEAD request. If asked, validate the current session and renew it when necessary.

        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return await self.request(
            "HEAD",
            url,
            **kwargs,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    async def post(
            self,
            url,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> ClientResponse:
        """
        Send a POST request. If asked, validate the current session and renew it when necessary.

        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return await self.request(
            "POST",
            url,
            **kwargs,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    async def put(
            self,
            url,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> ClientResponse:
        """
        Send a PUT request. If asked, validate the current session and renew it when necessary.

        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return await self.request(
            "PUT",
            url,
            **kwargs,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    async def patch(
            self,
            url,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> ClientResponse:
        """
        Sends a PATCH request. If asked, validates the current session and renews it when necessary.

        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return await self.request(
            "PATCH",
            url,
            **kwargs,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    async def delete(
            self,
            url,
            validate_session: bool = True,
            auto_renew: bool = True,
            **kwargs
    ) -> ClientResponse:
        """
        Sends a DELETE request. If asked, validates the current session and renews it when necessary.

        :param validate_session: (optional) Whether to validate the current session.
        :param auto_renew: (optional) Whether to renew the session when it expires. Works when validate_session is True.
        :return: an :class:`Response` object.
        """
        return await self.request(
            "DELETE",
            url,
            **kwargs,
            validate_session=validate_session,
            auto_renew=auto_renew
        )

    async def login(self, username: str, password: str):
        """
        Log in JAccount using given username & password.

        :param username: JAccount username.
        :param password: JAccount password.
        :raises LoginException: Failed to login after several attempts.
        """
        lock_acquired = False
        if not self._login_lock.locked():
            await self._login_lock.acquire()
            lock_acquired = True
        try:
            self._cache_store = {}
            for i in self._retry:
                login_page_req = await self._secure_req(partial(self.get, consts.LOGIN_URL, validate_session=False))
                uuid = re.findall(r"(?<=uuid\": ').*(?=')", await login_page_req.text())[0]
                login_params = {k: v[0] for k, v in parse_qs(urlparse(str(login_page_req.url)).query).items()}

                captcha_img = (await self.get(consts.CAPTCHA_URL,
                                              params={"uuid": uuid, "t": int(time.time() * 1000)},
                                              validate_session=False)).content
                captcha = self._ocr.recognize(await captcha_img.read())
                if inspect.iscoroutine(captcha):
                    captcha = await captcha

                login_params.update({"v": "", "uuid": uuid, "user": username, "pass": password, "captcha": captcha})
                result = await self._secure_req(
                    partial(self.post, consts.LOGIN_POST_URL, params=login_params, headers=consts.HEADERS,
                            validate_session=False))
                if result.url.query.get("err") is None:  # type: ignore
                    self._username = username
                    self._password = password
                    self._renew_required = False
                    return

                await asyncio.sleep(i)

            raise LoginException
        finally:
            if lock_acquired:
                self._login_lock.release()

    async def logout(self, purge_session: bool = True):
        """
        Log out JAccount.

        :param purge_session: (optional) Whether to purge local session info. May causes inconsistency, so use with
            caution.
        """
        cookie_bak = self._client.cookie_jar.save_dict()
        await self.get(consts.LOGOUT_URL, params={"t": int(time.time() * 1000), "login_type": ""},
                       validate_session=False)
        if purge_session:
            self._username = ''
            self._password = ''
        else:
            self._client.cookie_jar.load_dict(cookie_bak)

    def loads(self, d: dict):
        """
        Read a session from a given dict. A warning will be given if username or password field is missing.

        :param d: a dict contains a session.
        """
        self._renew_required = True
        self._cache_store = d.get("cache_store", {})

        if d.get("cookies"):
            self._renew_required = False
            self._client.cookie_jar.load_dict(d["cookies"])

        if "username" not in d.keys() or "password" not in d.keys() or not d["username"] or not d["password"]:
            warnings.warn("Missing username or password field", LoadWarning)
            self._username = ""
            self._password = ""
            self._renew_required = False
        else:
            self._username = d["username"]
            self._password = d["password"]

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
                "cookies": self._client.cookie_jar.save_dict(),
                "cache_store": self._cache_store}  # type: ignore

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
    def cookies(self) -> dict:
        """
        Get or set the cookie to be used on each request. AsyncSession validation is performed on each set event.

        :raises SessionException: when given cookie doesn't contain a valid session.
        """
        return self._client.cookie_jar.save_dict()

    @cookies.setter
    def cookies(self, new_cookie: dict):
        # noinspection PyTypeHints
        self._client.cookie_jar.load_dict(new_cookie)

    @property
    def base_url(self) -> str:
        """ Base url of backend APIs. """
        return self._base_url

    @property
    def username(self) -> str:
        return self._username

    async def close(self):
        await self._client.close()