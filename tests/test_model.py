from datetime import date, time
from functools import partial
from math import ceil

import pytest

from pysjtu.models import QueryResult, GPAQueryParams, GPA, LibCourse, Exam, ScoreFactor, Score, ScheduleCourse, \
    Exams, Scores, Schedule, LazyResult, PARTIAL, SelectionClass, SelectionSector
from pysjtu.schemas import ExamSchema, ScoreSchema, ScheduleCourseSchema


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


def test_lazy_model(mocker):
    class DummyModel(LazyResult):
        normal_field: int = 0
        lazy_field_1: int = PARTIAL
        lazy_field_2: str = PARTIAL

    fake_load_func = mocker.Mock(return_value={"lazy_field_1": 1, "lazy_field_2": "2"})
    model = DummyModel()
    model._load_func = fake_load_func

    assert model.normal_field == 0
    fake_load_func.assert_not_called()
    fake_load_func.reset_mock()

    assert model.lazy_field_1 == 1
    fake_load_func.assert_called_once()
    fake_load_func.reset_mock()

    assert model.lazy_field_2 == "2"
    fake_load_func.assert_not_called()


@pytest.mark.parametrize("model, members, repr_pair", [
    (SelectionClass,
     ["name", "credit", "course_id", "internal_course_id", "class_name", "class_id", "students_registered",
      "register_id", "teachers", "locations", "time", "course_type", "remark", "students_planned", "sector"],
     ({"class_name": "Calculus", "name": "AA000-0"},
      "<SelectionClass Calculus AA000-0>")),

    (SelectionSector,
     ["task_type", "xkly", "pe_op_param", "sector_type_id", "txbsfrl", "kkbk", "course_type_code", "name", "xkkz_id",
      "include_other_grades", "include_other_majors", "sfznkx", "zdkxms", "shared_info"],
     ({"name": "major"},
      "<SelectionSector major>")),

    (GPAQueryParams,
     ["start_term", "end_term", "condition_logic", "makeup_as_60", "rebuild_as_60", "gp_round", "gpa_round",
      "exclude_gp", "exclude_gpa", "course_whole", "course_range", "ranking", "has_roll", "registered", "attending"],
     ({"start_term": 0},
      "<GPAQueryParams {'start_term': 0, 'end_term': None, 'condition_logic': None, 'makeup_as_60': None, "
      "'rebuild_as_60': None, 'gp_round': None, 'gpa_round': None, 'exclude_gp': None, 'exclude_gpa': None, "
      "'course_whole': None, 'course_range': None, 'ranking': None, 'has_roll': None, 'registered': None, "
      "'attending': None}>")),

    (GPA,
     ["total_score", "course_count", "fail_count", "total_credit", "acquired_credit", "failed_credit", "pass_rate",
      "gp",
      "gp_ranking", "gpa", "gpa_ranking", "total_students"],
     ({"gp": 80, "gp_ranking": 50, "gpa": 3.8, "gpa_ranking": 40, "total_students": 200},
      "<GPA gp=80 50/200 gpa=3.8 40/200>")),

    (LibCourse,
     ["name", "day", "week", "time", "location", "locations", "faculty", "credit", "teacher", "course_id", "class_name",
      "class_id", "class_composition", "hour_total", "hour_remark", "seats", "students_elected", "students_planned"],
     ({"name": "Calculus", "class_name": "AA001"}, "<LibCourse Calculus class_name=AA001>")),

    (Exam,
     ["name", "location", "course_id", "course_name", "class_name", "rebuild", "credit", "self_study", "date", "time"],
     ({"name": "Calculus Final", "course_name": "Calculus",
       "location": "LocDummy", "date": date(2012, 12, 21), "time": [time(13, 0), time(15, 0)]},
      "<Exam \"Calculus Final\" course_name=Calculus location=LocDummy datetime=2012-12-21(13:00-15:00)>")),

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

    with pytest.raises(TypeError):
        model(fake_arg=0)

    repr_kwargs = repr_pair[0]
    repr_kwargs.update({member: None for member in members if member not in repr_kwargs})
    assert repr(model(**repr_kwargs)) == repr_pair[1]


def test_selection_sector(mocker):
    hash_func = mocker.patch("pysjtu.models.selection.elfhash", return_value=919293949)
    class_func = mocker.Mock(return_value=["1"])

    members = ["task_type", "xkly", "pe_op_param", "sector_type_id", "txbsfrl", "kkbk", "course_type_code", "name",
               "xkkz_id", "shared_info", "include_other_grades", "include_other_majors", "sfznkx", "zdkxms"]
    kwargs = {member: idx for idx, member in zip(range(len(members)), members) if member != "name"}
    model_1 = SelectionSector(name="dummy", _func_classes=class_func, **kwargs)

    assert hash(model_1) == 919293949
    hash_func.assert_called_once()
    hash_func.reset_mock()
    assert hash(model_1) == 919293949
    hash_func.assert_not_called()

    assert model_1.classes == ["1"]
    class_func.assert_called_once()


def test_score_detail(mocker):
    members = ["name", "teacher", "score", "credit", "gp", "invalid", "course_type", "category", "score_type", "method",
               "course_id", "class_name", "class_id"]
    kwargs = {member: idx for idx, member in zip(range(len(members)), members) if member != "class_id"}
    model_1 = Score(**kwargs)
    model_1.year = 2012
    model_1.term = 1
    model_1.class_id = "dummy"
    fake_detail_func = mocker.Mock(return_value="fake detail")
    model_1._func_detail = fake_detail_func
    for _ in range(2):
        assert model_1.detail == "fake detail"
        fake_detail_func.assert_called_once_with(2012, 1, "dummy")


@pytest.fixture
def fake_model():
    class FakeModel:
        def __init__(self, **kwargs):
            self.__dict__.update(**kwargs)

        def __eq__(self, other):
            return self.__dict__ == other.__dict__

        def __repr__(self):
            return f"<FakeModel {self.__dict__}>"

    return FakeModel


@pytest.mark.parametrize("model, mock_schema, test_score",
                         [(Exams, ExamSchema, False), (Schedule, ScheduleCourseSchema, False),
                          (Scores, ScoreSchema, True)])
def test_loader_model(mocker, fake_model, model, mock_schema, test_score):
    rtn_var = [
        fake_model(name="Calculus", credit=6.0),
        fake_model(name="Calculus", credit=4.0),
        fake_model(name="Chemistry", credit=4.0)
    ]
    if test_score:
        loaded_var = rtn_var.copy()
        for item in loaded_var:
            item.__dict__.update({"year": 2012, "term": 1, "_func_detail": None})
    else:
        loaded_var = rtn_var
    mocker.patch.object(mock_schema, "load", return_value=rtn_var)
    if test_score:
        model_1 = model(year=2012, term=1, func_detail=None)
    else:
        model_1 = model(year=2012, term=1)
    assert model_1.year == 2012
    assert model_1.term == 1
    model_1.load(None)
    assert len(model_1) == 3
    assert model_1 == rtn_var
    assert model_1.filter(name="Calculus") == loaded_var[:2]
    assert model_1.filter(name="Calculus", credit=4.0) == [loaded_var[1]]
    with pytest.raises(KeyError):
        model_1.filter(dummy="Lorem")


def test_schedule_filter(mocker, fake_model):
    rtn_var = [
        fake_model(name="Calculus", day=1, week=[range(1, 17)], time=range(1, 3)),
        fake_model(name="Chemistry", day=3, week=[range(1, 14, 2)], time=range(1, 3)),
        fake_model(name="Millitary", day=2, week=[5, 10, range(14, 16)], time=range(5, 7))
    ]
    mocker.patch.object(ScheduleCourseSchema, "load", return_value=rtn_var)
    model_1 = Schedule()
    model_1.load(None)
    assert model_1.filter(week=3) == rtn_var[:2]
    assert model_1.filter(week=17) == []
    assert model_1.filter(week=[5]) == rtn_var
    assert model_1.filter(week=range(15, 17)) == [rtn_var[0], rtn_var[2]]
    assert model_1.filter(week=[3, range(16, 17)]) == rtn_var[:2]
    assert model_1.filter(week=[5, range(16, 17)]) == rtn_var

    assert model_1.filter(day=2) == [rtn_var[-1]]
    assert model_1.filter(day=range(1, 5, 2)) == rtn_var[:2]
    assert model_1.filter(day=[2, range(1, 5, 2)]) == rtn_var

    assert model_1.filter(time=2) == rtn_var[:2]
    assert model_1.filter(time=3) == []
    assert model_1.filter(time=[6]) == [rtn_var[-1]]
    assert model_1.filter(time=range(4, 7)) == [rtn_var[-1]]
    assert model_1.filter(time=[1, range(4, 7)]) == rtn_var
