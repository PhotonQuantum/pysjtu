import os
import sys
from os import path

import pytest
import respx

from pysjtu.ocr import LegacyRecognizer, NNRecognizer, JCSSRecognizer

CAPTCHA_DIR = path.join(path.dirname(path.abspath(__file__)), 'resources/captcha')


@pytest.fixture(params=[
    pytest.param(LegacyRecognizer,
                 marks=pytest.mark.xfail(reason="SVM-based recognizer doesn't recognize captcha correctly sometime.")),
    NNRecognizer])
def recognizer(request):
    return request.param()


def captcha_files():
    def f_read(f):
        return open(path.join(CAPTCHA_DIR, f), mode="rb").read()

    def f_expected(f):
        return path.splitext(path.basename(f))[0]

    return [
        (f_expected(f), f_read(f))
        for f in os.listdir(CAPTCHA_DIR)
    ]


@pytest.mark.skipif(sys.version_info > (3, 10), reason="Python 3.11 doesn't have ONNXRuntime, yet.")
@pytest.mark.parametrize("captcha", captcha_files())
def test_recognizer(captcha, recognizer):
    expected, file = captcha
    assert recognizer.recognize(file) == expected


@respx.mock
def test_jcss_recognizer():
    respx.post("https://jcss.lightquantum.me",
               content='{"status":"success","data":{"prediction":"gbmke","elapsed_time":2}}')
    predictor = JCSSRecognizer(proxies={"all://": None})
    assert predictor.recognize(b'fbkfbkfbk') == "gbmke"
