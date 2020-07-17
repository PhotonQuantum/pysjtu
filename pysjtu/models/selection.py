from dataclasses import dataclass
from typing import Optional

from pysjtu.models.base import Result


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
    """
    term: str
    selection_year: int
    selection_term: int
    major_id: str
    student_grade: int
    natural_class_id: str
    self_selecting_status: int


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
    :param course_type_code: unknown parameter.
    :type course_type_code: str
    """
    task_type: int
    xkly: int
    pe_op_param: int
    sector_type_id: str
    course_type_code: Optional[str] = None
    name: Optional[str] = None
    shared_info: Optional[SelectionSharedInfo] = None

    def __repr__(self):
        return f"<SelectionSector {self.name}>"
