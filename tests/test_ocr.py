from pysjtu.ocr import Recognizer
import pytest
from os import path
DATA_DIR = path.join(path.dirname(path.abspath(__file__)), 'data')
MODEL_FILE = path.join(path.dirname(path.abspath(".")), 'model.pickle')


@pytest.mark.xfail(reason="my classifier doesn't recognize captcha correctly sometime.")
@pytest.mark.parametrize("predictor", [Recognizer(MODEL_FILE)])
@pytest.mark.parametrize("captcha", [
    "mwgi", "qkxvx", "qrdxb", "rysv", "zwtco"
])
def test_recognize_captcha(predictor, captcha):
    assert predictor.recognize(open(path.join(DATA_DIR, captcha + ".jpg"), mode="rb").read()) == captcha
