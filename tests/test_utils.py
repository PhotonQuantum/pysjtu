from collections.abc import Generator
from os import path

import pytest

from pysjtu.utils import elfhash, flatten, has_callable, overlap, parse_slice, range_in_set, range_list_to_str, \
    replace_keys, schema_post_loader

DATA_DIR = path.join(path.dirname(path.abspath(__file__)), 'data')


def test_elfhash():
    assert elfhash("hello world") == 224648685
    assert elfhash("生活就像海洋，只有意志坚强的人才能到达彼岸。"
                   "This is an apple. I like apples. Apples are good for our health.") == 238480205


def test_parse_slice():
    class DummyObj1:
        __index__ = 0

    class DummyObj2:
        def __index__(self):
            return 0

    assert parse_slice(3) == 3
    assert parse_slice(DummyObj2()) == 0
    assert parse_slice(None) is None
    with pytest.raises(AttributeError):
        parse_slice(1.5)
    with pytest.raises(AttributeError):
        parse_slice(DummyObj1())


def test_has_callable():
    class Test:
        test_var1 = 0

        def __init__(self):
            self.test_var2 = 0

        def test_func(self):
            return 0

    not_a_class = 0
    assert has_callable(Test, "test_func")
    assert not has_callable(Test, "test_var1")
    assert not has_callable(Test, "test_var2")
    assert not has_callable(not_a_class, "wrong_func")


@pytest.mark.parametrize("base_dict", [{"key_1": "value_1", "key_2": "value_2", "key_3": "value_3"}])
@pytest.mark.parametrize("pairs, expected", [
    ([("key_1", "key_4")], {"key_4": "value_1", "key_2": "value_2", "key_3": "value_3"}),
    ([("key_1", "key_4"), ("key_2", "key_5")], {"key_4": "value_1", "key_5": "value_2", "key_3": "value_3"}),
    ([("key_2", "key_3"), ("key_3", "key_1")], {"key_1": "value_2"})
])
def test_replace_keys(base_dict, pairs, expected):
    test_dict = base_dict.copy()
    rtn_dict = replace_keys(test_dict, pairs)
    assert test_dict == rtn_dict == expected


def test_schema_post_loader():
    class DummySchema:
        def __init__(self, **kwargs):
            self.many = kwargs["many"] if "many" in kwargs.keys() else False

        def load(self, data):
            return self.many, data

    assert schema_post_loader(DummySchema, [1, 2]) == (True, [1, 2])
    assert schema_post_loader(DummySchema, {"k": "v"}) == (False, {"k": "v"})
    with pytest.raises(TypeError):
        schema_post_loader(DummySchema, 0)


def test_range_list_to_str():
    assert range_list_to_str([1]) == "1"
    assert range_list_to_str([1, range(3, 5)]) == "1或3或4"
    with pytest.raises(TypeError):
        range_list_to_str(1)


def test_range_in_set():
    assert len(list(range_in_set({}))) == 0

    ranges = range_in_set({1, 3, 4, 5, 7, 8, 9, 10})
    assert isinstance(ranges, Generator)
    assert list(ranges) == [range(1, 2), range(3, 6), range(7, 11)]


@pytest.mark.parametrize("objs, intersection", [
    ((2, range(1, 4)), {2}),
    (([1, 3, 4, 7, range(9, 11)], [range(2, 6), 10]), {3, 4, 10})
])
def test_overlap(objs, intersection):
    assert overlap(*objs) == intersection


@pytest.mark.parametrize("obj, flattened", [
    ([1, 3, range(5, 7)], [1, 3, 5, 6]),
    ([range(1, 7, 2)], [1, 3, 5])
])
def test_flatten(obj, flattened):
    assert isinstance(flatten(obj), Generator)
    assert list(flatten(obj)) == flattened
