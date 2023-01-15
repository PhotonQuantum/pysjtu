from functools import lru_cache, partial
from typing import List

from pysjtu import consts
from pysjtu.client.base import BaseClient
from pysjtu.exceptions import DropException, FullCapacityException, RegistrationException, \
    SelectionClassFetchException, SelectionNotAvailableException, TimeConflictException
from pysjtu.models.selection import SelectionClass, SelectionSector, SelectionSharedInfo, SelectionClassLazySchema
from pysjtu.parser.selection import parse_sector, parse_sectors, parse_shared_info


class SelectionMixin(BaseClient):
    def __init__(self):
        super().__init__()
        self._fetch_selection_classes = lru_cache(maxsize=1024)(self._fetch_selection_classes)
        self._get_selection_classes = lru_cache(maxsize=16)(self._get_selection_classes)

    def _class_is_registered(self, _class: SelectionClass, **kwargs) -> bool:
        payload = {
            "jxb_id": _class.register_id,
            "xkkz_id": _class.sector.xkkz_id,
            "xnm": _class.sector.shared_info.selection_year,
            "xqm": _class.sector.shared_info.selection_term
        }
        is_registered = self._session.post(f"{consts.SELECTION_IS_REGISTERED}{self.student_id}", data=payload,
                                           **kwargs).json()
        return is_registered == "1"

    def _class_register(self, _class: SelectionClass, **kwargs):
        payload = {
            "jxb_ids": _class.register_id,
            "kch_id": _class.internal_course_id,
            "qz": 0
        }
        register = self._session.post(f"{consts.SELECTION_REGISTER}{self.student_id}", data=payload, **kwargs).json()
        if not register or "flag" not in register:
            raise RegistrationException("Bad request.")  # pragma: no cover
        if register["flag"] == "0":
            if "msg" in register:
                if register["msg"] == "所选教学班的上课时间与其他教学班有冲突！":
                    raise TimeConflictException
                else:  # pragma: no cover
                    raise RegistrationException(register["msg"])  # pragma: no cover
            else:
                raise RegistrationException("Unknown error.")  # pragma: no cover
        elif register["flag"] == "-1":
            raise FullCapacityException
        elif register["flag"] == "1":
            return
        else:
            raise RegistrationException(f"Unexpected response: {register}")  # pragma: no cover

    def _class_drop(self, _class: SelectionClass, **kwargs):
        payload = {
            "kch_id": _class.internal_course_id,
            "jxb_ids": _class.register_id
        }
        drop = self._session.post(f"{consts.SELECTION_DROP}{self.student_id}", data=payload, **kwargs).json()
        if drop == "1":
            return
        elif drop == "2":  # pragma: no cover
            raise DropException("Server busy.")  # pragma: no cover
        elif drop == "3":  # pragma: no cover
            raise DropException("Unknown error.")  # pragma: no cover
        elif drop == "4":  # pragma: no cover
            raise DropException("Illegal access.")  # pragma: no cover
        elif drop == "5":  # pragma: no cover
            raise DropException("Validation failure.")  # pragma: no cover
        else:
            raise DropException(f"Unexpected response: {drop}")  # pragma: no cover

    def _fetch_selection_classes(self, sector: SelectionSector, internal_course_id: str) -> List[dict]:
        payload = {
            **SelectionSector.Schema().dump(sector),
            **SelectionSharedInfo.Schema().dump(sector.shared_info),
            "kch_id": internal_course_id
        }
        classes_query = self._session.post(f"{consts.SELECTION_QUERY_CLASSES}{self.student_id}", data=payload).json()
        return SelectionClassLazySchema(many=True).load(classes_query)

    def _fetch_selection_class(self, selection_class: SelectionClass):
        class_dicts = self._fetch_selection_classes(selection_class.sector, selection_class.internal_course_id)
        for class_dict in class_dicts:
            if class_dict["class_id"] == selection_class.class_id:
                return class_dict
        raise SelectionClassFetchException("Unable to fetch selection class information.")  # pragma: no cover

    def _get_selection_classes(self, sector: SelectionSector) -> List[SelectionClass]:
        payload = {
            **SelectionSector.Schema().dump(sector),
            **SelectionSharedInfo.Schema().dump(sector.shared_info),
            "kspage": 1,
            "jspage": 5000
        }
        courses_query = self._session.post(f"{consts.SELECTION_QUERY_COURSES}{self.student_id}", data=payload).json()
        selection_classes: List[SelectionClass] = [item for item in
                                                   SelectionClass.Schema(many=True).load(courses_query["tmpList"])]
        for _class in selection_classes:
            _class.sector = sector
            _class._load_func = partial(self._fetch_selection_class, _class)
            _class.is_registered = partial(self._class_is_registered, _class)
            _class.register = partial(self._class_register, _class)
            _class.drop = partial(self._class_drop, _class)
        return selection_classes

    @property
    def course_selection_sectors(self) -> List[SelectionSector]:
        """
        In iSJTU, courses are split into different sectors when selecting course.
        This property contains all available course sectors in this round of selection.
        """
        sectors_query = self._session.get(f"{consts.SELECTION_ALL_SECTORS_PARAM_URL}{self.student_id}").text
        if "对不起，当前不属于选课阶段" in sectors_query:
            raise SelectionNotAvailableException

        raw_shared_info = parse_shared_info(sectors_query)
        shared_info: SelectionSharedInfo = SelectionSharedInfo.Schema().load(raw_shared_info)

        raw_sectors = parse_sectors(sectors_query)
        sectors = []
        for kklxdm, xkkz_id, name in raw_sectors:
            sector_query = self._session.post(f"{consts.SELECTION_SECTOR_PARAM_URL}{self.student_id}",
                                              data={"xkkz_id": xkkz_id,
                                                    "xszxzt": shared_info.self_selecting_status,
                                                    "kspage": 0, "jspage": 0}).text
            raw_sector = parse_sector(sector_query)
            sector: SelectionSector = SelectionSector.Schema().load(raw_sector)
            sector.name, sector.course_type_code, sector.xkkz_id, sector.shared_info = \
                name, kklxdm, xkkz_id, shared_info
            sector._func_classes = partial(self._get_selection_classes, sector=sector)
            sectors.append(sector)

        return sectors

    def flush_selection_class_cache(self):
        self._fetch_selection_classes.cache_clear()
