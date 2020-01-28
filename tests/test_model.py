from datetime import date, time
from functools import partial
from math import ceil
from unittest.mock import patch

import pytest

from pysjtu.model import QueryResult, GPAQueryParams, GPA, LibCourse, Exam, ScoreFactor, Score, ScheduleCourse, Exams, \
    Scores, Schedule
from pysjtu.schema import ExamSchema, ScoreSchema, ScheduleCourseSchema


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


# noinspection PyStatementEffect
def test_query_result(dummy_req):
    def dummy_post_func(x):
        return {"post": x}

    result = QueryResult(partial(dummy_req, 200), dummy_post_func, {"validate": "Lorem Ipsum"}, page_size=10)

    assert len(result) == 200

    assert result[50] == {"post": 51}
    assert result[-2] == {"post": 199}
    assert result[-200] == {"post": 1}
    with pytest.raises(IndexError):
        result[200]
    with pytest.raises(IndexError):
        result[-201]
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        result[1.5]

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
        result[1.5:]
    with pytest.raises(AttributeError):
        result[:1.5]

    dummy_obj = dummy_req
    result = QueryResult(partial(dummy_obj, 200), dummy_post_func, {"validate": "Lorem Ipsum"}, page_size=10)
    result[5:25]
    assert dummy_obj.is_called
    result[4:24]
    assert not dummy_obj.is_called
    result.flush_cache()
    result[4:24]
    assert dummy_obj.is_called


@pytest.mark.parametrize("model, members, repr_pair", [
    (GPAQueryParams,
     ["start_term", "end_term", "condition_logic", "makeup_as_60", "rebuild_as_60", "gp_round", "gpa_round",
      "exclude_gp", "exclude_gpa", "course_whole", "course_range", "ranking", "has_roll", "registered", "attending"],
     ({"start_term": 0},
      "<GPAQueryParams {'start_term': 0, 'end_term': None, 'condition_logic': None, 'makeup_as_60': None, "
      "'rebuild_as_60': None, 'gp_round': None, 'gpa_round': None, 'exclude_gp': None, 'exclude_gpa': None, "
      "'course_whole': None, 'course_range': None, 'ranking': None, 'has_roll': None, 'registered': None, "
      "'attending': None}>")),

    (GPA,
     ["total_score", "course_count", "fail_count", "total_gp", "acquired_gp", "failed_gp", "pass_rate", "gp",
      "gp_ranking", "gpa", "gpa_ranking", "total_students"],
     ({"gp": 80, "gp_ranking": 50, "gpa": 3.8, "gpa_ranking": 40, "total_students": 200},
      "<GPA gp=80 50/200 gpa=3.8 40/200>")),

    (LibCourse,
     ["name", "day", "week", "time", "location", "locations", "faculty", "credit", "teacher", "course_id", "class_name",
      "class_id", "class_composition", "hour_total", "hour_remark", "seats", "students_elected", "students_planned"],
     ({"name": "Calculus", "class_name": "AA001"}, "<LibCourse Calculus class_name=AA001>")),

    (Exam,
     ["name", "location", "course_id", "course_name", "class_name", "rebuild", "credit", "self_study", "date", "time"],
     ({"name": "Calculus", "location": "LocDummy", "date": date(2012, 12, 21), "time": [time(13, 0), time(15, 0)]},
      "<Exam \"Calculus\" location=LocDummy datetime=2012-12-21(13:00-15:00)>")),

    (ScoreFactor,
     ["name", "percentage", "score"],
     ({"name": "Exam", "percentage": 0.6, "score": 92}, "<ScoreFactor Exam(60.0%)=92>")),

    (Score,
     ["name", "teacher", "score", "credit", "gp", "invalid", "course_type", "category", "score_type", "method",
      "course_id", "class_name", "class_id"],
     ({"name": "Calculus", "score": 87, "credit": 6.0, "gp": 3.7}, "<Score Calculus score=87 credit=6.0 gp=3.7>")),

    (ScheduleCourse,
     ["name", "day", "week", "time", "location", "credit", "assessment", "remark", "teacher_name", "teacher_title",
      "course_id", "class_name", "class_id", "hour_total", "hour_remark", "hour_week", "field"],
     ({"name": "Calculus", "week": [range(1, 17)], "day": 1, "time": range(1, 3)},
      "<ScheduleCourse Calculus week=[range(1, 17)] day=1 time=range(1, 3)>"))
])
def test_dict_model(model, members, repr_pair):
    kwargs = {member: idx for idx, member in zip(range(len(members)), members)}
    model_1 = model(**kwargs)
    for idx, member in zip(range(len(members)), members):
        assert getattr(model_1, member) == idx

    model_2 = model()
    for member in members:
        assert getattr(model_2, member) is None

    with pytest.raises(TypeError):
        model(fake_arg=0)

    assert repr(model(**repr_pair[0])) == repr_pair[1]


@pytest.fixture
def fake_model():
    class FakeModel:
        def __init__(self, **kwargs):
            self.__dict__.update(**kwargs)

        def __eq__(self, other):
            return self.__dict__ == other.__dict__

    return FakeModel


@pytest.mark.parametrize("model, mock_schema", [(Exams, ExamSchema), (Schedule, ScheduleCourseSchema)])
def test_loader_model(mocker, fake_model, model, mock_schema):
    rtn_var = [
        fake_model(name="Calculus", credit=6.0),
        fake_model(name="Chemistry", credit=3.0)
    ]
    mocker.patch.object(mock_schema, "load", return_value=rtn_var)
    model_1 = model(year=2012, term=1)
    assert model_1.year == 2012
    assert model_1.term == 1
    model_1.load(None)
    assert model_1.all() == rtn_var
    assert model_1.filter(name="Calculus") == [rtn_var[0]]
    with pytest.raises(KeyError):
        model_1.filter(dummy="Lorem")


def test_score_loader_model(mocker, fake_model):
    rtn_var = [
        fake_model(name="Calculus", credit=6.0),
        fake_model(name="Chemistry", credit=3.0)
    ]
    loaded_var = [
        fake_model(name="Calculus", credit=6.0, year=2012, term=1, _func_detail=None),
        fake_model(name="Chemistry", credit=3.0, year=2012, term=1, _func_detail=None)
    ]
    mocker.patch.object(ScoreSchema, "load", return_value=rtn_var)
    model_1 = Scores(year=2012, term=1, func_detail=None)
    assert model_1.year == 2012
    assert model_1.term == 1
    model_1.load(None)
    assert model_1.all() == loaded_var
    assert model_1.filter(name="Calculus") == [loaded_var[0]]
    with pytest.raises(KeyError):
        model_1.filter(dummy="Lorem")
