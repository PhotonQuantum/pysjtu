from pysjtu.session import Session


class BaseClient:
    _session: Session

    @property
    def student_id(self) -> int: ...
