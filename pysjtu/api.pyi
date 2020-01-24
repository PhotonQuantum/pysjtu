import typing

import httpx
from httpx.auth import AuthTypes
from httpx.config import (
    UNSET,
    TimeoutTypes,
    UnsetType,
    ProxiesTypes
)
from httpx.models import (
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestData,
    RequestFiles,
    Response,
    URLTypes,
)

from . import model
from .ocr import Recognizer


class Session:
    _client: httpx.Client
    _ocr: Recognizer
    _retry: list
    _username: str
    _password: str
    _cache_store: dict
    _release_when_exit: bool
    _session_file: typing.BinaryIO

    def _secure_req(self, ref: typing.Callable) -> Response:
        pass

    def __enter__(self) -> Session:
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __init__(self, username: str = "", password: str = "", cookies: CookieTypes = None,
                 ocr: Recognizer = None, session_file: typing.BinaryIO = None, retry: list = None):
        pass

    def request(
            self,
            method: str,
            url: URLTypes,
            *,
            data: RequestData = None,
            files: RequestFiles = None,
            json: typing.Any = None,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: typing.Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        pass

    def get(
            self,
            url: URLTypes,
            *,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: typing.Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        pass

    def options(
            self,
            url: URLTypes,
            *,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: typing.Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        pass

    def head(
            self,
            url: URLTypes,
            *,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = False,  # NOTE: Differs to usual default.
            timeout: typing.Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        pass

    def post(
            self,
            url: URLTypes,
            *,
            data: RequestData = None,
            files: RequestFiles = None,
            json: typing.Any = None,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: typing.Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        pass

    def put(
            self,
            url: URLTypes,
            *,
            data: RequestData = None,
            files: RequestFiles = None,
            json: typing.Any = None,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: typing.Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        pass

    def patch(
            self,
            url: URLTypes,
            *,
            data: RequestData = None,
            files: RequestFiles = None,
            json: typing.Any = None,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: typing.Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        pass

    def delete(
            self,
            url: URLTypes,
            *,
            params: QueryParamTypes = None,
            headers: HeaderTypes = None,
            cookies: CookieTypes = None,
            auth: AuthTypes = None,
            allow_redirects: bool = True,
            timeout: typing.Union[TimeoutTypes, UnsetType] = UNSET,
            validate_session: bool = True,
            auto_renew: bool = True
    ) -> Response:
        pass

    def login(self, username: str, password: str):
        pass

    def logout(self, purge_session: bool = True):
        pass

    def loads(self, d: dict):
        pass

    def load(self, fp: typing.BinaryIO):
        pass

    def dumps(self) -> dict:
        pass

    def dump(self, fp: typing.BinaryIO):
        pass

    @property
    def proxies(self) -> ProxiesTypes:
        pass

    @proxies.setter
    def proxies(self, new_proxy: ProxiesTypes):
        pass

    @property
    def _cookies(self) -> CookieTypes:
        pass

    @_cookies.setter
    def _cookies(self, new_cookie: CookieTypes):
        pass

    @property
    def cookies(self) -> CookieTypes:
        pass

    @cookies.setter
    def cookies(self, new_cookie: CookieTypes):
        pass

    @property
    def timeout(self) -> TimeoutTypes:
        pass

    @timeout.setter
    def timeout(self, new_timeout: TimeoutTypes):
        pass


class Client:
    _session: Session

    def __init__(self, session: Session):
        pass

    @property
    def term_start_date(self) -> str:
        pass

    @property
    def student_id(self) -> str:
        pass

    @property
    def default_gpa_query_params(self) -> model.GPAQueryParams:
        pass

    def schedule(self, year: int, term: int, timeout: TimeoutTypes = UNSET) -> model.Schedule:
        pass

    def _get_score_detail(self, year: int, term: int, class_id: str, timeout: TimeoutTypes = UNSET) -> typing.List[
        model.ScoreFactor]:
        pass

    def score(self, year: int, term: int, timeout: TimeoutTypes = UNSET) -> model.Scores:
        pass

    def exam(self, year: int, term: int, timeout: TimeoutTypes = UNSET) -> model.Exams:
        pass

    def query_courses(self, year: int, term: int, name: str = None, teacher: str = None, day_of_week: list = None,
                      week: list = None, time_of_day: list = None,
                      timeout: TimeoutTypes = UNSET) -> model.QueryResult:
        pass

    def query_gpa(self, query_params: model.GPAQueryParams, timeout: TimeoutTypes = UNSET) -> model.Exams:
        pass

    def _elect(self, params):
        pass
