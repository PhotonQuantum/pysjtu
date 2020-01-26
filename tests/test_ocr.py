from os import path

import pytest

from pysjtu.ocr import SVMRecognizer, NNRecognizer

CAPTCHA_DIR = path.join(path.dirname(path.abspath(__file__)), 'resources/captcha')
MODEL_FILE = path.join(path.abspath("."), 'model.pickle')
NN_MODEL_FILE = path.join(path.abspath("."), 'ckpt.pth')


@pytest.mark.xfail(reason="SVM-based and ResNet-based recognizer doesn't recognize captcha correctly sometime.")
@pytest.mark.parametrize("predictor", [SVMRecognizer(MODEL_FILE), NNRecognizer(NN_MODEL_FILE)])
@pytest.mark.parametrize("captcha", [
    "mwgi", "qkxvx", "qrdxb", "rysv", "zwtco"
])
def test_svm_recognizer(predictor, captcha):
    assert predictor.recognize(open(path.join(CAPTCHA_DIR, captcha + ".jpg"), mode="rb").read()) == captcha


@pytest.mark.cuda
@pytest.mark.xfail(reason="ResNet-based recognizer doesn't recognize captcha correctly sometime.")
@pytest.mark.parametrize("captcha", [
    "mwgi", "qkxvx", "qrdxb", "rysv", "zwtco"
])
def test_resnet_recognizer_cuda(captcha):
    predictor = NNRecognizer(NN_MODEL_FILE, use_cuda=True)
    assert predictor.recognize(open(path.join(CAPTCHA_DIR, captcha + ".jpg"), mode="rb").read()) == captcha
