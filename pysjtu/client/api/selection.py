from pysjtu import consts
from pysjtu.client.base import BaseClient
from pysjtu.models.selection import SelectionSector, SelectionSharedInfo
from pysjtu.parser.selection import parse_sector, parse_sectors, parse_shared_info
from pysjtu.schemas.selection import SelectionSectorSchema, SelectionSharedInfoSchema


class SelectionMixin(BaseClient):
    @property
    def course_selection_sectors(self):
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
            sector.name, sector.course_type_code, sector.shared_info = name, kklxdm, shared_info
            sectors.append(sector)

        return sectors
