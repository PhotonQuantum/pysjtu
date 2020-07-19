from os import path

import pytest

from pysjtu.parser.selection import parse_fields, parse_sectors


@pytest.fixture()
def website_loader():
    RESP_DIR = path.join(path.dirname(path.abspath(__file__)), 'resources/website')

    def _resp_loader(name):
        with open(path.join(RESP_DIR, name + ".html"), encoding="utf-8") as f:
            return f.read()

    return _resp_loader


def test_parse_sectors(website_loader):
    raw_src = website_loader("zzxkyzb_cxZzxkYzbIndex")
    assert parse_sectors(raw_src) == [
        ("01", "A000000000000B76E055F8163ED16360", "主修课程"),
        ("71", "A000000000000A7FE055F8163ED16360", "民族生课程"),
        ("72", "A000000000000881E055F8163ED16360", "留学生课程"),
        ("06", "A000000000000F12E055F8163ED16360", "板块课(体育（3）)"),
        ("10", "A000000000000455E055F8163ED16360", "通识课"),
        ("11", "A000000000000B28E055F8163ED16360", "通选课")
    ]


def test_parse_fields(website_loader):
    raw_src = website_loader("zzxkyzb_cxZzxkYzbIndex")
    assert parse_fields(raw_src, ["xqh_id", "zyh_id", "njdm_id"]) == \
           {"xqh_id": "02", "zyh_id": "000000", "njdm_id": "2019"}
    with pytest.raises(StopIteration):
        parse_fields(raw_src, ["xqh_id", "invalid_field"])
