from __future__ import annotations

import re
from typing import List, Optional, Tuple, Union, ClassVar, Type, Any, Mapping, Callable

from marshmallow import fields, EXCLUDE, Schema
from marshmallow_dataclass import dataclass

from pysjtu.consts import CHINESE_WEEK
from pysjtu.fields import StrBool, SplitField
from pysjtu.models.base import LazyResult, _PARTIAL, Result
from pysjtu.models.common import Gender
from pysjtu.schema import mfield, WithField, FinalizeHook, LoadDumpSchema
from pysjtu.utils import elfhash, parse_course_week


class _Gender(fields.Field):
    def _deserialize(
            self,
            value: Any,
            attr: Optional[str],
            data: Optional[Mapping[str, Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return Gender(int(value))  # need to cast string to int

    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs):
        return value.value


class _Time(fields.Field):
    regex = re.compile("星期(?P<weekday>.)第(?P<time>.*?)节{(?P<week>.*?)}")

    def _deserialize(
            self,
            value: Any,
            attr: Optional[str],
            data: Optional[Mapping[str, Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover

        def _parse_time(input_str: str) -> List[range]:
            return [range(int(time[0]), int(time[1]) + 1)
                    for time in [times.split('-') for times in input_str.split(",")]]

        def _dict_to_time(input_dict: dict) -> LessonTime:
            return LessonTime(
                weekday=CHINESE_WEEK[input_dict["weekday"]],
                week=parse_course_week(input_dict["week"]),
                time=_parse_time(input_dict["time"])
            )

        return [_dict_to_time(match.groupdict()) for match in self.regex.finditer(value)]


class _Teacher(fields.Field):
    def _deserialize(
            self,
            value: Any,
            attr: Optional[str],
            data: Optional[Mapping[str, Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return [tuple(teacher.split("/")[1:]) for teacher in value.split(";")]


@dataclass
class LessonTime:
    weekday: int
    week: List[Union[range, int]]
    time: List[range]


# noinspection PyAbstractClass
@dataclass(base_schema=FinalizeHook(LoadDumpSchema))
class SelectionSharedInfo:
    """
    A model which contains shared information in this round of selection.

    :param term: current term when querying.
    :param selection_year: year of selected courses.
    :param selection_term: term of selected courses.
    :param major_id: internal major id.
    :param student_grade: year of enrollment.
    :param natural_class_id: class id of the administrative class of the student.
    :param self_selecting_status: unknown parameter.
    :param ccdm: unknown parameter.
    :param student_type_code: unknown parameter.
    :param gender: student's gender.
    :param field_id: student's professional field.
    :param student_background: unknown parameter.
    """
    term: str = mfield(required=True, data_key="xqh_id")
    selection_year: int = mfield(required=True, data_key="xkxnm")
    selection_term: int = mfield(required=True, data_key="xkxqm")
    major_id: str = mfield(required=True, data_key="zyh_id")
    student_grade: int = mfield(required=True, data_key="njdm_id")
    natural_class_id: str = mfield(required=True, data_key="bh_id")
    self_selecting_status: int = mfield(required=True, data_key="xszxzt")
    ccdm: str = mfield(required=True)
    student_type_code: int = mfield(required=True, data_key="xslbdm")
    gender: WithField(Gender, field=_Gender) = mfield(required=True, data_key="xbm")
    field_id: str = mfield(required=True, data_key="zyfx_id")
    student_background: int = mfield(required=True, data_key="xsbj")

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


# noinspection PyAbstractClass
@dataclass(base_schema=FinalizeHook(LoadDumpSchema))
class SelectionSector(Result):
    """
    A model which describes a course sector in this round of selection.

    :param name: sector name.
    :param shared_info: shared information in this round of selection.
    :param task_type: unknown parameter.
    :param xkly: unknown parameter.
    :param pe_op_param: unknown parameter. (translation: the parameters updated in operations related to PE lessons.)
    :param sector_type_id: unknown parameter.
    :param include_other_grades: include courses from other grades.
    :param include_other_majors: include courses from other majors.
    :param sfznkx: unknown parameter.
    :param zdkxms: unknown parameter.
    :param txbsfrl: unknown parameter. (used when dropping courses.)
    :param kkbk: unknown parameter.
    :param course_type_code: unknown parameter.
    :param xkkz_id: unknown parameter.
    """
    task_type: int = mfield(required=True, data_key="rwlx")
    xkly: int = mfield(required=True)
    pe_op_param: int = mfield(required=True, data_key="tykczgxdcs")
    sector_type_id: str = mfield(required=True, data_key="bklx_id")
    include_other_grades: WithField(bool, field=StrBool) = mfield(required=True, data_key="sfkknj")
    include_other_majors: WithField(bool, field=StrBool) = mfield(required=True, data_key="sfkkzy")
    sfznkx: WithField(bool, field=StrBool) = mfield(required=True)
    zdkxms: int = mfield(required=True)
    txbsfrl: int = mfield(required=True)
    kkbk: int = mfield(required=True)
    xkkz_id: Optional[str] = mfield(None, dump_only=True)
    course_type_code: Optional[str] = mfield(None, required=True, dump_only=True, data_key="kklxdm")
    name: Optional[str] = mfield(None, raw=True)
    shared_info: Optional[SelectionSharedInfo] = mfield(None, raw=True)
    _func_classes: Callable = mfield(None, raw=True)
    _hash: Optional[int] = mfield(None, raw=True)

    class Meta:
        unknown = EXCLUDE
        exclude = ["name", "shared_info", "_func_classes", "_hash"]

    def __hash__(self):
        if not self._hash:
            self._hash = elfhash(self.name)
        return self._hash

    def __repr__(self):
        return f"<SelectionSector {self.name}>"

    @property
    def classes(self) -> List[SelectionClass]:
        """
        Selectable classes in this course sector.
        """
        return self._func_classes()


class SelectionClassLazySchema(Schema):
    """ :meta private:"""

    class Meta:
        unknown = EXCLUDE

    class_id = fields.Str(required=True, data_key="jxb_id")
    register_id = fields.Str(required=True, data_key="do_jxb_id")
    teachers = _Teacher(required=True, data_key="jsxx")
    locations = SplitField(required=True, data_key="jxdd", sep="<br/>")
    time = _Time(required=True, data_key="sksj")
    course_type = SplitField(required=True, data_key="kcxzmc", sep=",")
    remark = fields.Str(data_key="xkbz", load_default=None)
    students_planned = fields.Int(required=True, data_key="jxbrl")


@dataclass(base_schema=FinalizeHook(LoadDumpSchema))
class SelectionClass(LazyResult):
    """
    A model which describes a selectable class in this round of selection.

    The data is not fetched until it is accessed for the first time.

    :param name: literal name of the course.
    :param credit: credits that the course provides.
    :param course_id: course id.
    :param course_id: internal course id.
    :param class_name: class name (constant between years).
    :param class_id: class id (variable between years).
    :param students_registered: number of students registered for this course.
    :param students_planned: number of students planned when setting this course.
    :param register_id: dynamic id used when (de)registering for this class.
    :param teachers: the teachers who offer this course.
    :param locations: the places where classes are given.
    :param time: the time when the class is given.
    :param course_type: course type. (eg. general, required, optional, ...)
    :param remark: remarks of this class.
    :param sector: the sector which this course lies in.
    """
    name: str = mfield(required=True, data_key="kcmc")
    credit: float = mfield(required=True, data_key="xf")
    course_id: str = mfield(required=True, data_key="kch")
    internal_course_id: str = mfield(required=True, data_key="kch_id")
    class_name: str = mfield(required=True, data_key="jxbmc")
    class_id: str = mfield(required=True, data_key="jxb_id")
    students_registered: int = mfield(required=True, data_key="yxzrs")
    register_id: str = mfield(_PARTIAL, raw=True)
    teachers: List[Tuple[str]] = mfield(_PARTIAL, raw=True)
    locations: List[str] = mfield(_PARTIAL, raw=True)
    time: LessonTime = mfield(_PARTIAL, raw=True)
    course_type: List[str] = mfield(_PARTIAL, raw=True)
    remark: Optional[str] = mfield(_PARTIAL, raw=True)
    students_planned: int = mfield(_PARTIAL, raw=True)
    sector: SelectionSector = mfield(None, raw=True)
    _load_func: Callable = mfield(None, raw=True)

    class Meta:
        unknown = EXCLUDE
        exclude = ["register_id", "teachers", "locations", "time", "course_type", "remark", "students_planned",
                   "sector", "_load_func"]

    def __repr__(self):
        return f"<SelectionClass {self.class_name} {self.name}>"

    def is_registered(self, timeout=10) -> bool:
        """
        Check whether the student has registered for this class.

        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A boolean value indicates the registration status.
        """
        raise NotImplementedError  # pragma: no cover

    def register(self, timeout=10):
        """
        Register for this class.

        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :raises: :exc:`pysjtu.exceptions.RegistrationException`
        :raises: :exc:`pysjtu.exceptions.FullCapacityException`
        :raises: :exc:`pysjtu.exceptions.TimeConflictException`
        :raises: :exc:`pysjtu.exceptions.SelectionNotAvailableException`
        """
        raise NotImplementedError  # pragma: no cover

    def drop(self, timeout=10):
        """
        Drop this class.

        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :raises: :exc:`pysjtu.exceptions.DropException`
        :raises: :exc:`pysjtu.exceptions.SelectionNotAvailableException`
        """
        raise NotImplementedError  # pragma: no cover

