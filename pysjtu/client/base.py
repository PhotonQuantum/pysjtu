from async_property import async_property
from pysjtu.session import BaseSession


class BaseClient:
    """ Base class for ClientMixin """
    _session: BaseSession

    @async_property
    async def student_id(self) -> int: ...
