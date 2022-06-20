import importlib.metadata

from pysjtu.ocr import LegacyRecognizer, NNRecognizer, JCSSRecognizer
from .client import Client, create_client
from .models import CourseRange, LogicEnum, Ranking
from .session import Session

__version__ = importlib.metadata.version("pysjtu")  # broken in local env due to bug in poetry 1.1
