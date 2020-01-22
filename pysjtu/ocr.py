import pickle
from io import BytesIO

from PIL import Image

from .utils import range_in_set


def row_not_empty(img, row):
    for i in range(img.width):
        if img.getpixel((i, row)) != 1:
            return True
    return False


def col_not_empty(img, col):
    for i in range(img.height):
        if img.getpixel((col, i)) != 1:
            return True
    return False


def h_split(img):
    col_filled = {col if col_not_empty(img, col) else None for col in range(img.width)}
    col_filled.remove(None)

    segments = range_in_set(col_filled)
    rtn = []
    for segment in segments:
        rtn.append(img.crop((segment.start, 0, segment.stop - 1, img.height)))
    return rtn


def v_split(img):
    row_filled = {row if row_not_empty(img, row) else None for row in range(img.height)}
    row_filled.remove(None)
    segments = list(range_in_set(row_filled))
    top = min([segment.start for segment in segments])
    bottom = max([segment.stop for segment in segments])
    return img.crop((0, top, img.width, bottom))


def normalize(img):
    rtn = Image.new("1", (20, 20), color=1)

    rtn.paste(img, (int((20 - img.width) / 2), int((20 - img.height) / 2)))
    return rtn


class Recognizer:
    def __init__(self, model_file: str = "model.pickle"):
        self._classifier = pickle.load(open(model_file, mode="rb"))
        self._table = [0] * 156 + [1] * 100

    def recognize(self, img: bytes):
        img_rec = Image.open(BytesIO(img))
        img_rec = img_rec.convert("L")
        img_rec = img_rec.point(self._table, "1")

        segments = [normalize(v_split(segment)).convert("L").getdata() for segment in h_split(img_rec)]
        return "".join(self._classifier.predict(segments))
