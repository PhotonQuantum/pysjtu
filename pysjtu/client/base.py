from pysjtu.session import Session


class BaseClient:
    _session: Session
    student_id: int
