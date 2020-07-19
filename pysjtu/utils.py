import base64
import collections
from math import inf
from pathlib import Path
from typing import BinaryIO, Union

FileTypes = Union[BinaryIO, str, Path]


def elfhash(input_str: str):
    s = base64.b64encode(input_str.encode("utf-8"))
    _hash = 0
    x = 0
    for c in s:
        _hash = (_hash << 4) + c
        x = _hash & 0xF0000000
        if x:
            _hash ^= (x >> 24)
            _hash &= ~x
    return _hash & 0x7FFFFFFF


def parse_course_week(value):
    def _parse(item):
        if item[-2] in ["单", "双"]:
            start, end = map(int, item[:-4].split('-'))
            start += (1 - start % 2) if item[-2] == "单" else (start % 2)
            return range(start, end + 1, 2)
        else:
            x = list(map(int, item[:-1].split('-')))
            return x[0] if len(x) == 1 else range(x[0], x[1] + 1)  # type: ignore

    return [_parse(item) for item in value.split(",")]


def parse_slice(val):
    if isinstance(val, int):
        return val
    if hasattr(val, "__index__") and isinstance(val.__index__, collections.abc.Callable):
        return val.__index__()
    if val is None:
        return val
    raise AttributeError("slice indices must be integers or None or have an __index__ method")


def has_callable(obj, name):
    return callable(getattr(obj, name, None))


def replace_keys(data, pairs):
    for from_key, to_key in pairs:
        if from_key in data:
            data[to_key] = data.pop(from_key)
    return data


def schema_post_loader(schema_ref, data):
    if isinstance(data, list):
        return schema_ref(many=True).load(data)
    if isinstance(data, dict):
        return schema_ref().load(data)
    raise TypeError


def range_list_to_str(range_list):
    return "或".join((str(x) for x in flatten(range_list)))


# skipcq: PYL-R1710
def range_in_set(set_in):
    if len(set_in) == 0:
        return set()
    last_elem = -inf
    start = None
    for elem in set_in:
        if elem != last_elem + 1:
            if start:
                yield range(start, last_elem + 1)
            start = elem
        last_elem = elem
    yield range(start, last_elem + 1)


def overlap(list1, list2):
    if not isinstance(list1, list):
        list1 = [list1]
    if not isinstance(list2, list):
        list2 = [list2]
    flatten1 = flatten(list1)
    flatten2 = flatten(list2)
    set1 = set(flatten1)
    return set1.intersection(flatten2)


def flatten(obj):
    for el in obj:
        if isinstance(el, collections.abc.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el
