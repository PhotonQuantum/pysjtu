from datetime import date
from os import path

import pytest
from lxml import html

from pysjtu.models.base import Gender
from pysjtu.parser.profile import ProfileField, parse
from pysjtu.parser.selection import parse_fields, parse_sectors
from pysjtu.schemas.profile import profile_fields


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


def test_parse_profile_single():
    el = html.fromstring(
        '<!doctype html> <html> <head> <title>LightQuantum</title> </head> <body> '
        '<p>test<a href="TEST">TEST FIELD</a>.</p> </body> </html>')
    el2 = html.fromstring(
        '<!doctype html> <html> <head> <title>LightQuantum</title> </head> <body> '
        '<p>test<a href="TEST"></a>.</p> </body> </html>')
    el3 = html.fromstring(
        '<!doctype html> <html> <head> <title>LightQuantum</title> </head> <body> '
        '<p>test.</p> </body> </html>')
    field = ProfileField("test_field", "/html/body/p/a", lambda x: x.replace("FIELD", "field"))
    assert field.parse(el) == "TEST field"
    assert field.parse(el2) is None
    assert field.parse(el3) is None


def test_parse_profile(website_loader):
    raw_src = website_loader("xsgrxxwh_cxXsgrxx")
    profile = parse(profile_fields, raw_src)
    assert profile == {'student_id': 519027910001, 'name': '林芳', 'name_pinyin': None, 'former_name': None,
                       'gender': Gender.female, 'certificate_type': '居民身份证', 'certificate_number': 300000000000000000,
                       'birth_date': date(2000, 11, 1), 'enrollment_date': date(2019, 9, 7), 'birthplace': None,
                       'ethnicity': '人族', 'native_place': 'OPUS_H', 'foreign_status': None, 'political_status': '地球教女巫',
                       'enrollment_province': 'OPUS_O', 'nationality': 'OPUS_N', 'domicile_place': None,
                       'cee_candidate_number': 19300000000000, 'middle_school': '地球教教会学校', 'religion': None,
                       'email': 'linfei@sjtu.edu.cn', 'cellphone': 17000000000, 'family_address': '奥伯斯火箭工厂_H',
                       'mailing_address': '奥伯斯火箭工厂_M', 'landline': 10000000, 'zip_code': 200000}
