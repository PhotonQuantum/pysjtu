from functools import lru_cache, partial
from typing import List

from pysjtu import consts
from pysjtu.client.base import BaseClient
from pysjtu.exceptions import SelectionClassFetchException
from pysjtu.models.selection import SelectionClass, SelectionSector, SelectionSharedInfo
from pysjtu.parser.selection import parse_sector, parse_sectors, parse_shared_info
from pysjtu.schemas.selection import SelectionClassSchema, SelectionCourseSchema, SelectionSectorSchema, \
    SelectionSharedInfoSchema


class SelectionMixin(BaseClient):
    def __init__(self):
        super().__init__()
        self._fetch_selection_classes = lru_cache(maxsize=1024)(self._fetch_selection_classes)

    def _fetch_selection_classes(self, sector: SelectionSector, internal_course_id: str) -> List[dict]:
        payload = {
            **SelectionSectorSchema().dump(sector),
            **SelectionSharedInfoSchema().dump(sector.shared_info),
            "kch_id": internal_course_id
        }
        classes_query = self._session.post(f"{consts.SELECTION_QUERY_CLASSES}{self.student_id}", data=payload).json()
        return SelectionClassSchema(many=True).load(classes_query)

    def _fetch_selection_class(self, selection_class: SelectionClass):
        class_dicts = self._fetch_selection_classes(selection_class.sector, selection_class.internal_course_id)
        for class_dict in class_dicts:
            if class_dict["class_id"] == selection_class.class_id:
                return class_dict
        raise SelectionClassFetchException("Unable to fetch selection class information.")

    def _get_selection_classes(self, sector: SelectionSector) -> List[SelectionClass]:
        payload = {
            **SelectionSectorSchema().dump(sector),
            **SelectionSharedInfoSchema().dump(sector.shared_info),
            "kspage": 1,
            "jspage": 500
        }
        courses_query = self._session.post(f"{consts.SELECTION_QUERY_COURSES}{self.student_id}", data=payload).json()
        selection_classes: List[SelectionClass] = [SelectionClass(**item) for item in
                                                   SelectionCourseSchema(many=True).load(courses_query["tmpList"])]
        for _class in selection_classes:
            _class.sector = sector
            _class._load_func = partial(self._fetch_selection_class, _class)
        return selection_classes

    @property
    def course_selection_sectors(self) -> List[SelectionSector]:
        """
        In iSJTU, courses are split into different sectors when selecting course.
        This property contains all available course sectors in this round of selection.
        """
        sectors_query = self._session.get(f"{consts.SELECTION_ALL_SECTORS_PARAM_URL}{self.student_id}").text

        raw_shared_info = parse_shared_info(sectors_query)
        shared_info: SelectionSharedInfo = SelectionSharedInfoSchema().load(raw_shared_info)

        raw_sectors = parse_sectors(sectors_query)
        sectors = []
        for kklxdm, xkkz_id, name in raw_sectors:
            sector_query = self._session.post(f"{consts.SELECTION_SECTOR_PARAM_URL}{self.student_id}",
                                              data={"xkkz_id": xkkz_id,
                                                    "xszxzt": shared_info.self_selecting_status,
                                                    "kspage": 0, "jspage": 0}).text
            raw_sector = parse_sector(sector_query)
            sector: SelectionSector = SelectionSectorSchema().load(raw_sector)
            sector.name, sector.course_type_code, sector.xkkz_id, sector.shared_info = \
                name, kklxdm, xkkz_id, shared_info
            sector._func_classes = partial(self._get_selection_classes, sector=sector)
            sectors.append(sector)

        return sectors

    def invalidate_selection_class_cache(self):
        self._fetch_selection_classes.cache_clear()
