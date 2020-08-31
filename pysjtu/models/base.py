import time
from enum import IntEnum
from typing import Callable, Generic, List, Tuple, Type, TypeVar, Union

from marshmallow import Schema  # type: ignore

from pysjtu.utils import overlap, parse_slice, range_in_set


class Gender(IntEnum):
    male = 1
    female = 2


class Result:
    """ Base class for Result """

    def __repr__(self):
        raise NotImplementedError  # pragma: no cover


class PARTIAL:
    pass


class LazyResult(Result):
    """ Base class for LazyResult """
    _load_func: Callable = None

    def __getattribute__(self, item):
        value = super().__getattribute__(item)
        if value == PARTIAL:
            update_dict = self._load_func()
            for k, v in update_dict.items():
                super().__setattr__(k, v)
            value = super().__getattribute__(item)
        return value


T_Result = TypeVar("T_Result", bound=Result)


class QueryResult(Generic[T_Result]):
    """
    A key accessible, sliceable, and iterable interface to query result collections.

    A QueryResult object is constructed with a raw data callable reference.

    A QueryResult object is returned by a query operation, and isn't meant to be constructed by a user.

    A QueryResult object is lazy, which means network I/Os won't be performed until items are actually accessed.

    :param method_ref: The request method to be called when fetching data.
    :param post_ref: The schema load method to be called on fetched data.
    :param query_params: Parameters for this query.
    :param page_size: The page size for result iteration.
    """
    _ref: Callable
    _post_ref: Callable
    _query_params: dict
    _length: int
    _cache: List[dict]
    _cached_items: set
    _page_size: int

    def __init__(self, method_ref: Callable, post_ref: Callable, query_params: dict, page_size: int = 15):
        self._ref = method_ref  # type: ignore
        self._post_ref = post_ref  # type: ignore
        self._query_params = query_params
        self._length = 0
        # noinspection PyTypeChecker
        self._cache = [{}] * len(self)
        self._cached_items = set()
        self._page_size = page_size

    def __getitem__(self, arg: Union[int, slice]) -> T_Result:
        if isinstance(arg, int):
            data = self._handle_result_by_index(arg)  # type: ignore
        elif isinstance(arg, slice):
            data = self._handle_result_by_idx_slice(arg)  # type: ignore
        else:
            raise TypeError("QueryResult indices must be integers or slices, not " + type(arg).__name__)
        data = self._post_ref(data)  # type: ignore
        return data  # type: ignore

    def _handle_result_by_index(self, idx: int) -> dict:
        idx = len(self) + idx if idx < 0 else idx
        if idx >= len(self) or idx < 0:
            raise IndexError("index out of range")
        self._update_cache(idx, idx + 1)
        return self._cache[idx]

    def _handle_result_by_idx_slice(self, idx: slice) -> list:
        idx_start = parse_slice(idx.start)
        idx_stop = parse_slice(idx.stop)

        if idx_start is None:
            start = 0
        elif idx_start < 0:
            start = len(self) + idx.start
        else:
            start = idx.start

        if idx_stop is None:
            end = len(self) - 1
        elif idx_stop < 0:
            end = len(self) + idx.stop - 1
        else:
            end = idx.stop

        if end > len(self):
            end = len(self)
        if start >= end:
            return []
        self._update_cache(start, end)
        return self._cache[idx]

    def __len__(self) -> int:
        if not self._length:
            rtn = self._query(1, 1)
            self._length = rtn["totalResult"]
        return self._length

    def flush_cache(self):
        """ Flush caches. Local caches are dropped and data will be fetched from remote. """
        self._length = 0
        # noinspection PyTypeChecker
        self._cache = [None] * len(self)
        self._cached_items = set()

    def _update_cache(self, start: int, end: int):
        fetch_set = set(set(range(start, end)) - self._cached_items)
        while len(fetch_set) != 0:
            fetch_range = next(range_in_set(fetch_set))
            page = int(fetch_range.start / self._page_size) + 1
            self._cached_items.update(range(*self._fetch_range(page, self._page_size)))
            fetch_set = set(set(range(start, end)) - self._cached_items)

    def _fetch_range(self, page: int, count: int) -> Tuple[int, int]:
        rtn = self._query(page, count)["items"]
        for item in zip(range(count * (page - 1), count * (page - 1) + len(rtn)), rtn):
            self._cache[item[0]] = item[1]
        return count * (page - 1), count * (page - 1) + len(rtn)

    def _query(self, page: int, count: int) -> dict:
        new_params = self._query_params
        new_params["queryModel.showCount"] = count
        new_params["queryModel.currentPage"] = page
        new_params["queryModel.sortName"] = ""
        new_params["queryModel.sortOrder"] = "asc"
        new_params["nd"] = int(time.time() * 1000)
        new_params["_search"] = False
        return self._ref(data=new_params).json()

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]


class Results(List[T_Result]):
    """
    Base class for Results

    :param year: year of the :class:`Results` object.
    :param term: term of the :class:`Results` object.
    """
    _schema: Type[Schema]
    _result_model: Type[T_Result]
    _valid_fields: List[str]

    def __init__(self, year: int = 0, term: int = 0):
        super().__init__()
        self._year = year
        self._term = term
        self._valid_fields = list(self._result_model.__annotations__.keys())

    @property
    def year(self) -> int:
        return self._year

    @property
    def term(self) -> int:
        return self._term

    def load(self, data: dict):
        """
        Load a list of dicts into Results, and deserialize dicts to Result objects.

        :param data: a list of dicts.
        """
        schema = self._schema(many=True)
        results = schema.load(data)
        for result in results:
            self.append(result)

    def filter(self, **param) -> List[T_Result]:
        """
        Get Result objects matching specific criteria.

        :param param: query criteria
        :return: Result objects matching given criteria.
        """
        rtn = list(self)
        for (k, v) in param.items():
            if k not in self._valid_fields:
                raise KeyError("Invalid criteria!")
            if k in ("week", "time", "day"):
                rtn = list(filter(lambda x: overlap(getattr(x, k), v), rtn))
            else:
                rtn = list(filter(lambda x: getattr(x, k) == v, rtn))
        return rtn
