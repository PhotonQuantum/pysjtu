from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple, Union

from pysjtu.models.base import Gender, LazyResult, PARTIAL, Result
from pysjtu.utils import elfhash


@dataclass
class LessonTime:
    weekday: int
    week: List[Union[range, int]]
    time: List[range]


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
    :param include_other_grades: include courses from other grades.
    :type include_other_grades: bool
    :param include_other_majors: include courses from other majors.
    :type include_other_majors: bool
    :param sfznkx: unknown parameter.
    :type sfznkx: str
    :param zdkxms: unknown parameter.
    :type zdkxms: int
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
    include_other_grades: bool
    include_other_majors: bool
    sfznkx: bool
    zdkxms: int
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
        """
        Selectable classes in this course sector.
        """
        return self._func_classes()


@dataclass
class SelectionClass(LazyResult):
    """
    A model which describes a selectable class in this round of selection.

    :param name: literal name of the course.
    :type name: str
    :param credit: credits that the course provides.
    :type credit: int
    :param course_id: course id.
    :type course_id: str
    :param course_id: internal course id.
    :type course_id: str
    :param class_name: class name (constant between years).
    :type class_name: str
    :param class_id: class id (variable between years).
    :type class_id: str
    :param students_elected: number of students registered for this course.
    :type students_elected: int
    :param students_planned: number of students planned when setting this course.
    :type students_planned: int
    :param register_id: dynamic id used when (de)registering for this class.
    :param teacher: the teachers who offer this course.
    :type teacher: List[Tuple[str]]
    :param locations: the places where classes are given.
    :type locations: List[str]
    :param time: the time when the class is given.
    :type time: LessonTime
    :param course_type: course type. (eg. general, required, optional, ...)
    :type course_type: str
    :param remark: remarks of this class.
    :type remark: str
    :param sector: the sector which this course lies in.
    """
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

    def is_registered(self, timeout=10) -> bool:
        """
        Check whether the student has registered for this class.

        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A boolean value indicates the registration status.
        :rtype: bool
        """
        raise NotImplementedError  # pragma: no cover

    def register(self, timeout=10):
        """
        Register for this class.

        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: None
        :raises: :exc:`pysjtu.exceptions.RegistrationException`
        :raises: :exc:`pysjtu.exceptions.FullCapacityException`
        :raises: :exc:`pysjtu.exceptions.TimeConflictException`
        :raises: :exc:`pysjtu.exceptions.SelectionNotAvailableException`
        """
        raise NotImplementedError  # pragma: no cover

    def deregister(self, timeout=10):
        """
        Drop this class.

        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: None
        :raises: :exc:`pysjtu.exceptions.DeregistrationException`
        :raises: :exc:`pysjtu.exceptions.SelectionNotAvailableException`
        """
        raise NotImplementedError  # pragma: no cover
