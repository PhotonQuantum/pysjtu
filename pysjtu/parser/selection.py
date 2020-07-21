import re
from functools import partial
from typing import Dict, List, Tuple

field_pattern = re.compile('id="(?P<k>.*?)" value="(?P<v>.*?)"/>')
sectors_pattern = re.compile("queryCourse\\(this,'(?P<kklxdm>\\d*)','(?P<xkkz_id>.*?)'.*>(?P<name>.*)</a>")


def parse_fields(html: str, fields: list) -> Dict[str, str]:
    """
    A helper function to extract args from hidden fields in html.

    :param html: Input html src.
    :param fields: Fields in need.
    :return: A dict contains specific args.

    :raises StopIteration: if fields are missing in the given html src.
    """
    result = {}
    _fields = fields.copy()

    param_iter = field_pattern.finditer(html)
    while _fields:
        k, v = next(param_iter).groups()
        if k in _fields:
            result[k] = v
            _fields.remove(k)
    return result


def parse_sectors(html: str) -> List[Tuple[str]]:
    """
    Extract available sectors from html.

    :param html: Input html src.
    :return: A list of tuples contains query parameters of all available sectors
    """
    return sectors_pattern.findall(html)


parse_shared_info = partial(parse_fields,
                            fields=["xqh_id", "zyh_id", "njdm_id", "bh_id", "xkxnm", "xkxqm", "xszxzt", "ccdm",
                                    "xslbdm", "xbm", "zyfx_id", "xsbj"])
parse_sector = partial(parse_fields, fields=["rwlx", "xkly", "tykczgxdcs", "bklx_id", "txbsfrl", "kkbk", "sfkknj",
                                             "sfkkzy", "sfznkx", "zdkxms"])
