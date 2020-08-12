import time
from typing import Union

from pysjtu import consts
from pysjtu import models
from pysjtu import schemas
from pysjtu.client.base import BaseClient
from pysjtu.exceptions import GPACalculationException


class GPAMixin(BaseClient):
    _default_gpa_query_params: models.GPAQueryParams

    def __init__(self):
        super().__init__()
        # noinspection PyTypeChecker
        self._default_gpa_query_params = None

    @property
    async def default_gpa_query_params(self) -> models.GPAQueryParams:
        """ Get default gpa query params defined by the website. """
        if not self._default_gpa_query_params:
            rtn = await self._session.get(consts.GPA_PARAMS_URL,
                                    params={"_": int(time.time() * 1000), "su": await self.student_id})
            self._default_gpa_query_params = schemas.GPAQueryParamsSchema().load(await rtn.json())  # type: ignore

        return self._default_gpa_query_params

    async def gpa(self, query_params: models.GPAQueryParams) -> models.GPA:
        """
        Query your GP & GPA and their rankings of specific year & term.

        :param query_params: parameters for this query.
            A default one can be fetched by reading property `default_gpa_query_params`.
        :param timeout: (optional) How long to wait for the server to send data before giving up.
        :return: A new :class:`GPA` object.
        """
        compiled_params = schemas.GPAQueryParamsSchema().dump(query_params)
        calc_rtn = await self._session.post(f"{consts.GPA_CALC_URL}{await self.student_id}",
                                      data=compiled_params)
        result = await calc_rtn.text()
        if result != "\"统计成功！\"":
            if result == "\"统计失败！\"":
                raise GPACalculationException("Calculation failure.")
            if "无功能权限" in result:
                raise GPACalculationException("Unauthorized.")
        compiled_params.update({"_search": False,
                                "nd": int(time.time() * 1000), "queryModel.showCount": 15,
                                "queryModel.currentPage": 1, "queryModel.sortName": "",
                                "queryModel.sortOrder": "asc", "time": 0})
        raw = await self._session.post(f"{consts.GPA_QUERY_URL}{await self.student_id}",
                                 data=compiled_params)
        return schemas.GPASchema().load((await raw.json())["items"][0])  # type: ignore
