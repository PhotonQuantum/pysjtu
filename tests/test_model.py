import pytest

from pysjtu.model import QueryResult
from functools import partial
from math import ceil


@pytest.fixture
def dummy_req():
    class DummyResp:
        def __init__(self, resp):
            self._resp = resp

        def json(self):
            return self._resp

    class DummyReq:
        def __init__(self):
            self._is_called = False

        def __call__(self, total, data):
            assert data["validate"] == "Lorem Ipsum"
            count = data["queryModel.showCount"]
            page = data["queryModel.currentPage"]
            assert page <= ceil(total / count)

            self._is_called = True
            resp = {"totalResult": total, "items": range(count * (page - 1) + 1, count * page + 1)}
            return DummyResp(resp)

        @property
        def is_called(self):
            _tmp = self._is_called
            self._is_called = False
            return _tmp

    return DummyReq()


def test_query_result(dummy_req):
    post_ref = lambda x: {"post": x}

    result = QueryResult(partial(dummy_req, 200), post_ref, {"validate": "Lorem Ipsum"}, page_size=10)

    assert len(result) == 200

    assert result[50] == {"post": 51}
    assert result[-2] == {"post": 199}
    assert result[-200] == {"post": 1}
    with pytest.raises(IndexError):
        overflow = result[200]
    with pytest.raises(IndexError):
        overflow = result[-201]
    with pytest.raises(TypeError):
        fail = result[1.5]

    assert result[:10] == {"post": list(range(1, 11))}
    assert result[:15] == {"post": list(range(1, 16))}
    assert result[185:] == {"post": list(range(186, 201))}
    assert result[:] == {"post": list(range(1, 201))}
    assert result[180:-100] == {"post": []}
    assert result[185:999] == result[185:]
    assert result[204:209] == {"post": []}
    assert result[-1:999] == {"post": [200]}
    assert list(result) == [{"post": item} for item in range(1, 201)]
    with pytest.raises(AttributeError):
        fail = result[1.5:]
    with pytest.raises(AttributeError):
        fail = result[:1.5]

    dummy_obj = dummy_req
    result = QueryResult(partial(dummy_obj, 200), post_ref, {"validate": "Lorem Ipsum"}, page_size=10)
    rtn = result[5:25]
    assert dummy_obj.is_called
    rtn = result[4:24]
    assert not dummy_obj.is_called
    result.flush_cache()
    rtn = result[4:24]
    assert dummy_obj.is_called
