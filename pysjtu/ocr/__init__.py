from contextlib import ExitStack
from io import BytesIO
from typing import Optional

import httpx

from pysjtu.exceptions import OCRException
from pysjtu.utils import range_in_set

try:
    import importlib_resources as resources
except ImportError:
    from importlib import resources

try:
    import onnxruntime as rt  # type: ignore

    has_onnx = True
except ModuleNotFoundError:
    has_onnx = False


class Recognizer:
    """ Base class for Recognizers """

    def recognize(self, img: bytes):
        raise NotImplementedError  # pragma: no cover


class JCSSRecognizer(Recognizer):
    """
    An online recognizer using JCSS (JAccount Captcha Solver Service).
    This is the default recognizer for :class:`pysjtu.session.Session`. You don't need to install any extra packages to use it.

    It shares the same backend implementation with :class:`NNRecognizer`, but is deployed on a remote server.

    By default, it uses the public instance of JCSS, but you can also deploy your own.
    See https://github.com/PhotonQuantum/jcss-rs.

    For additional keyword arguments, see https://www.python-httpx.org/api.

    :param url: The URL of the JCSS instance.
    """

    def __init__(self, url: str = "https://jcss.lightquantum.me", **kwargs):
        self.url = url
        self.client = httpx.Client(**kwargs)

    def recognize(self, img: bytes):
        try:
            r = self.client.post(self.url, files={"image": BytesIO(img)})
            resp = r.json()
            return resp["data"]["prediction"]
        except Exception as e:  # pragma: no cover
            raise OCRException from e  # pragma: no cover


class NNRecognizer(Recognizer):
    """
    A Neural Network based captcha recognizer.

    It feeds the image directly into a pre-trained deep model to predict the answer.

    It consumes more memory and computing power than :class:`LegacyRecognizer`. By using the provided model,
    the accuracy is around 99%.

    It's currently the default recognizer.

    Usage::

        >>> import pysjtu
        >>> s = pysjtu.Session(ocr=NNRecognizer("nn_model.onnx"))
        >>> s.login('user@sjtu.edu.cn', 'something_secret')

    :param model_file: Pretrained ONNX model file (use built-in model if not specified).
    """

    def __init__(self, model_file: Optional[str] = None):
        if not has_onnx:
            raise RuntimeError("Missing dependency: ONNXRuntime")
        if not model_file:
            self._model_ctx = ExitStack()
            res_ref = resources.files("pysjtu.ocr") / "nn_model.onnx"
            model_file = str(self._model_ctx.enter_context(resources.as_file(res_ref)))
        self._table = [0] * 156 + [1] * 100
        self._sess = rt.InferenceSession(model_file)

    def __del__(self):
        if hasattr(self, "_model_ctx"):
            self._model_ctx.close()

    @staticmethod
    def _tensor_to_captcha(tensors):
        import numpy as np

        captcha = ""
        for tensor in tensors:
            asc = int(np.argmax(tensor, 1))
            if asc < 26:
                captcha += chr(ord("a") + asc)
        return captcha

    def recognize(self, img: bytes):
        """
        Predict the captcha.

        :param img: A bytes array containing the captcha image.
        :return: captcha in plain text.
        """
        import numpy as np
        from PIL import Image

        img_rec = Image.open(BytesIO(img))
        img_rec = img_rec.convert("L")
        img_rec = img_rec.point(self._table, "1")
        img_np = np.array(img_rec, dtype=np.float32)
        img_np = np.expand_dims(img_np, 0)
        img_np = np.expand_dims(img_np, 0)

        out_tensor = self._sess.run(None, {self._sess.get_inputs()[0].name: img_np})
        output = NNRecognizer._tensor_to_captcha(out_tensor)
        return output


class LegacyRecognizer(Recognizer):
    """
    A legacy captcha recognizer. **DEPRECATED**.

    It first applies projection-based algorithm to the input image, then use a pre-trained SVM model
    to predict the answer.

    It's memory and cpu efficient, but has a low accuracy. It's recommended to use :class:`NNRecognizer` instead.

    Usage::

        >>> import pysjtu
        >>> s = pysjtu.Session(ocr=LegacyRecognizer("svm_model.onnx"))
        >>> s.login('user@sjtu.edu.cn', 'something_secret')

    :param model_file: Pretrained ONNX model file (use built-in model if not specified).
    """

    def __init__(self, model_file: Optional[str] = None):
        if not has_onnx:
            raise RuntimeError("Missing dependency: ONNXRuntime")
        if not model_file:
            self._model_ctx = ExitStack()
            res_ref = resources.files("pysjtu.ocr") / "svm_model.onnx"
            model_file = str(self._model_ctx.enter_context(resources.as_file(res_ref)))
        self._clr = rt.InferenceSession(model_file)
        self._table = [0] * 156 + [1] * 100

    def __del__(self):
        if hasattr(self, "_model_ctx"):
            self._model_ctx.close()

    @staticmethod
    def row_not_empty(img, row):
        """
        A helper function to detect whether there's any black block in the specific row in a binary image.

        :param img: input image.
        :param row: specify a row to detect.

        :return: a bool indicating the result.
        :meta private:
        """
        for i in range(img.width):
            if img.getpixel((i, row)) != 1:
                return True
        return False

    @staticmethod
    def col_not_empty(img, col):
        """
        A helper function to detect whether there's any black block in the specific col in a binary image.

        :param img: input image.
        :param col: specify a col to detect.

        :return: a bool indicating the result.
        :meta private:
        """
        for i in range(img.height):
            if img.getpixel((col, i)) != 1:
                return True
        return False

    @staticmethod
    def h_split(img):
        """
        A helper function to split captcha into segments horizontally using projection.

        :param img: input image.

        :return: segmented images.
        :meta private:
        """
        col_filled = {col if LegacyRecognizer.col_not_empty(img, col) else None for col in range(img.width)}
        col_filled.remove(None)

        segments = range_in_set(col_filled)
        rtn = []
        for segment in segments:
            rtn.append(img.crop((segment.start, 0, segment.stop - 1, img.height)))
        return rtn

    @staticmethod
    def v_split(img):
        """
        A helper function to crop images vertically.

        :param img: input image.

        :return: cropped images.
        :meta private:
        """
        row_filled = {row if LegacyRecognizer.row_not_empty(img, row) else None for row in range(img.height)}
        row_filled.remove(None)
        segments = list(range_in_set(row_filled))
        top = min(segment.start for segment in segments)
        bottom = max(segment.stop for segment in segments)
        return img.crop((0, top, img.width, bottom))

    @staticmethod
    def normalize(img):
        """
        A helper function to normalize segmented & cropped image.

        :param img: input image.

        :return: normalized image.
        :meta private:
        """
        from PIL import Image

        rtn = Image.new("1", (20, 20), color=1)

        rtn.paste(img, (int((20 - img.width) / 2), int((20 - img.height) / 2)))
        return rtn

    def recognize(self, img: bytes):
        """
        Predict the captcha.

        :param img: A bytes array containing the captcha image.
        :return: captcha in plain text.
        """
        import numpy as np
        from PIL import Image

        img_rec = Image.open(BytesIO(img))
        img_rec = img_rec.convert("L")
        img_rec = img_rec.point(self._table, "1")

        segments = [self.normalize(self.v_split(segment)).convert("L").getdata() for segment in
                    self.h_split(img_rec)]

        np_segments = [np.array(segment, dtype=np.float32) for segment in segments]
        predicts = [self._clr.run(None, {self._clr.get_inputs()[0].name: np_segment}) for np_segment in np_segments]
        return "".join(str(predict[0][0]) for predict in predicts)
