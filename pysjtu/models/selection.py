from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from pysjtu.models.base import LazyResult, PARTIAL, Result
from pysjtu.utils import elfhash


# noinspection PyAbstractClass
@dataclass
class SelectionSharedInfo:
    """
    A model which contains shared information in this round of selection.

    :param term: current term when querying.
    :type term: str
    :param selection_year: year of selected courses.
    :type selection_year: int
    :param selection_term: term of selected courses.
    :type selection_term: int
    :param major_id: internal major id.
    :type major_id: str
    :param student_grade: year of enrollment.
    :type student_grade: str
    :param natural_class_id: class id of the administrative class of the student.
    :type natural_class_id: str
    :param self_selecting_status: unknown parameter.
    :type self_selecting_status: int
    :param ccdm: unknown parameter.
    :type ccdm: str
    :param student_type_code: unknown parameter.
    :type student_type_code: int
    :param gender: student's gender.
    :type gender: Gender
    :param field_id: student's professional field.
    :type field_id: str
    :param student_background: unknown parameter.
    :type student_background: int
    """
    term: str
    selection_year: int
    selection_term: int
    major_id: str
    student_grade: int
    natural_class_id: str
    self_selecting_status: int
    ccdm: str
    student_type_code: int
    gender: Gender
    field_id: str
    student_background: int


# noinspection PyAbstractClass
@dataclass
class SelectionSector(Result):
    """
    A model which describes a course sector in this round of selection.

    :param name: sector name.
    :type name: str
    :param shared_info: shared information in this round of selection.
    :type shared_info: SelectionSharedInfo
    :param task_type: unknown parameter.
    :type task_type: int
    :param xkly: unknown parameter.
    :type xkly: int
    :param pe_op_param: unknown parameter. (translation: the parameters updated in operations related to PE lessons.)
    :type pe_op_param: int
    :param sector_type_id: unknown parameter.
    :type sector_type_id: str
    :param txbsfrl: unknown parameter. (used when deregistering courses.)
    :type txbsfrl: int
    :param kkbk: unknown parameter.
    :type kkbk: int
    :param course_type_code: unknown parameter.
    :type course_type_code: str
    :param xkkz_id: unknown parameter.
    :type xkkz_id: str
    """
    task_type: int
    xkly: int
    pe_op_param: int
    sector_type_id: str
    txbsfrl: int
    kkbk: int
    course_type_code: Optional[str] = None
    name: Optional[str] = None
    xkkz_id: Optional[str] = None
    shared_info: Optional[SelectionSharedInfo] = None
    _func_classes: Callable = None
    _hash: Optional[int] = None

    def __hash__(self):
        if not self._hash:
            self._hash = elfhash(self.name)
        return self._hash

    def __repr__(self):
        return f"<SelectionSector {self.name}>"

    @property
    def classes(self) -> List[SelectionClass]:
        return self._func_classes()


from pysjtu.schemas.selection import LessonTime, Gender


@dataclass
class SelectionClass(LazyResult):
    name: str
    credit: float
    course_id: str
    internal_course_id: str
    class_name: str
    class_id: str
    students_registered: int
    register_id: str = PARTIAL
    teachers: List[Tuple[str]] = PARTIAL
    locations: List[str] = PARTIAL
    time: LessonTime = PARTIAL
    course_type: List[str] = PARTIAL
    remark: Optional[str] = PARTIAL
    students_planned: int = PARTIAL
    sector: SelectionSector = None
    _load_func: Callable = None

    def __repr__(self):
        return f"<SelectionClass {self.class_name} {self.name}>"
