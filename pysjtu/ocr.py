import pickle
from io import BytesIO

from PIL import Image

from .utils import range_in_set


class Recognizer:
    """ Base class for Recognizers """
    pass


class SVMRecognizer(Recognizer):
    """
    An SVM-based captcha recognizer.

    It first applies projection-based algorithm to the input image, then use a pre-trained SVM model
    to predict the answer.

    It's memory and cpu efficient. The accuracy is around 90%.

    This recognizer requires sklearn to work. It's currently the default recognizer.

    Usage::

        >>> import pysjtu
        >>> s = pysjtu.Session(ocr=SVMRecognizer("model.pickle"))
        >>> s.login('user@sjtu.edu.cn', 'something_secret')
    """

    def __init__(self, model_file: str = "model.pickle"):
        self._classifier = pickle.load(open(model_file, mode="rb"))
        self._table = [0] * 156 + [1] * 100

    @staticmethod
    def row_not_empty(img, row):
        """
        A helper function to detect whether there's any black block in the specific row in a binary image.

        :param img: input image.
        :param row: specify a row to detect.

        :return a bool indicating the result.
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

        :return a bool indicating the result.
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

        :return segmented images.
        """
        col_filled = {col if SVMRecognizer.col_not_empty(img, col) else None for col in range(img.width)}
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

        :return cropped images.
        """
        row_filled = {row if SVMRecognizer.row_not_empty(img, row) else None for row in range(img.height)}
        row_filled.remove(None)
        segments = list(range_in_set(row_filled))
        top = min([segment.start for segment in segments])
        bottom = max([segment.stop for segment in segments])
        return img.crop((0, top, img.width, bottom))

    @staticmethod
    def normalize(img):
        """
        A helper function to normalize segmented & cropped image.

        :param img: input image.

        :return normalized image.
        """
        rtn = Image.new("1", (20, 20), color=1)

        rtn.paste(img, (int((20 - img.width) / 2), int((20 - img.height) / 2)))
        return rtn

    def recognize(self, img: bytes):
        """
        Predict the captcha.

        :param img: An PIL Image containing the captcha.
        :return: captcha in plain text.
        """
        img_rec = Image.open(BytesIO(img))
        img_rec = img_rec.convert("L")
        img_rec = img_rec.point(self._table, "1")

        segments = [SVMRecognizer.normalize(SVMRecognizer.v_split(segment)).convert("L").getdata() for segment in
                    SVMRecognizer.h_split(img_rec)]
        return "".join(self._classifier.predict(segments))


class NNRecognizer(Recognizer):
    """
    A ResNet-20 based captcha recognizer.

    It feeds the image directly into a pre-trained ResNet-20 model to predict the answer.

    It consumes more memory and computing power than :class:`SVMRecognizer`. The accuracy is around 98%.

    This recognizer requires pytorch and torchvision to work.

    Usage::

        >>> import pysjtu
        >>> s = pysjtu.Session(ocr=NNRecognizer("ckpt.pth"))
        >>> s.login('user@sjtu.edu.cn', 'something_secret')

    .. note::

        You may set the flag `use_cuda` to speed up predicting, but be aware that it takes time to load the model
        into your GPU and there won't be significant speed-up unless you have a weak CPU.
    """

    def __init__(self, model_file: str = "ckpt.pth", use_cuda=False):
        import torch
        from torchvision import transforms
        from .nn_models import resnet20
        self._table = [0] * 156 + [1] * 100
        self._use_cuda = use_cuda
        if self._use_cuda:
            self._model = resnet20().cuda()
            checkpoint = torch.load(model_file)
        else:
            self._model = resnet20().cpu()
            cpu_device = torch.device("cpu")
            checkpoint = torch.load(model_file, map_location=cpu_device)
        self._model.load_state_dict(checkpoint["net"])
        self._model.eval()
        self._loader = transforms.ToTensor()

    @staticmethod
    def tensor_to_captcha(tensors):
        """
        A helper function to translate Tensor prediction to str.

        :param tensors: prediction in Tensor.
        :return: prediction in str.
        """
        rtn = ""
        for tensor in tensors:
            if int(tensor) != 26:
                rtn += chr(ord("a") + int(tensor))

        return rtn

    def recognize(self, img: bytes):
        """
        Predict the captcha.

        :param img: An PIL Image containing the captcha.
        :return: captcha in plain text.
        """
        from torch.autograd import Variable
        img_rec = Image.open(BytesIO(img))
        img_rec = img_rec.convert("L")
        img_rec = img_rec.point(self._table, "1")
        img_tensor = self._loader(img_rec).float().unsqueeze(0)
        if self._use_cuda:
            img_tensor = Variable(img_tensor).cuda()
        else:
            img_tensor = Variable(img_tensor).cpu()

        output = self._model(img_tensor)
        predicted_tensor = [tensor.max(1)[1] for tensor in output]
        predicted = NNRecognizer.tensor_to_captcha(predicted_tensor)
        return predicted
