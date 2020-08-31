from pysjtu import consts
from pysjtu.client.base import BaseClient
from pysjtu.models.profile import Profile
from pysjtu.parser.profile import parse
from pysjtu.schemas.profile import profile_fields


class ProfileMixin(BaseClient):
    def __init__(self):
        super().__init__()

    @property
    def profile(self) -> Profile:
        """ Get the user profile of the current session. """
        if "profile" not in self._session._cache_store:
            rtn = self._session.get(f"{consts.PROFILE_URL}{self.student_id}")
            self._session._cache_store["profile"] = parse(profile_fields, rtn.text)
        return Profile(**self._session._cache_store["profile"])
