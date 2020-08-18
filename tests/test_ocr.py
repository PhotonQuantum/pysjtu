from os import path

import pytest
import respx

from pysjtu.ocr import LegacyRecognizer, NNRecognizer, JCSSRecognizer

CAPTCHA_DIR = path.join(path.dirname(path.abspath(__file__)), 'resources/captcha')
MODEL_FILE = path.join(path.abspath("."), 'svm_model.onnx')
NN_MODEL_FILE = path.join(path.abspath("."), 'nn_model.onnx')


@pytest.mark.xfail(reason="SVM-based and ResNet-based recognizer doesn't recognize captcha correctly sometime.")
@pytest.mark.parametrize("predictor", [LegacyRecognizer(), NNRecognizer()])
@pytest.mark.parametrize("captcha", [
    "mwgi", "qkxvx", "qrdxb", "rysv", "zwtco"
])
def test_recognizer(predictor, captcha):
    assert predictor.recognize(open(path.join(CAPTCHA_DIR, captcha + ".jpg"), mode="rb").read()) == captcha

@respx.mock
def test_jcss_recognizer():
    respx.post("https://jcss.lightquantum.me", content='{"status":"success","data":{"prediction":"gbmke","elapsed_time":2}}')
    predictor = JCSSRecognizer()
    assert predictor.recognize(b'fbkfbkfbk') == "gbmke"