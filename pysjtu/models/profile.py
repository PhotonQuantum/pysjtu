from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .base import Gender


@dataclass(frozen=True)
class Profile:
    student_id: int
    name: str
    name_pinyin: Optional[str]
    former_name: Optional[str]
    gender: Gender
    certificate_type: str
    certificate_number: int
    birth_date: datetime
    enrollment_date: datetime
    birthplace: Optional[str]
    ethnicity: Optional[str]
    native_place: Optional[str]
    foreign_status: Optional[str]
    political_status: Optional[str]
    enrollment_province: Optional[str]
    nationality: Optional[str]
    domicile_place: Optional[str]
    cee_candidate_number: Optional[int]
    middle_school: Optional[str]
    religion: Optional[str]
    email: Optional[str]
    cellphone: Optional[int]
    family_address: Optional[str]
    mailing_address: Optional[str]
    landline: Optional[int]
    zip_code: Optional[int]
