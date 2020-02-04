from pysjtu.session import Session


class BaseClient:
    """ Base class for ClientMixin """
    _session: Session

    @property
    def student_id(self) -> int: ...
