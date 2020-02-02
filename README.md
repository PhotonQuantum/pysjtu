<p align="center"><strong>PySJTU</strong> <em>- The Python iSJTU client for Humans.</em></p>

<p align="center">
<a href="https://circleci.com/gh/PhotonQuantum/pysjtu">
    <img src="https://circleci.com/gh/PhotonQuantum/pysjtu.svg?style=shield" alt="CircleCI">
</a>
<a href='https://pysjtu.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/pysjtu/badge/?version=latest' alt='Documentation Status' />
</a>
<a href="https://coveralls.io/github/PhotonQuantum/pysjtu?branch=master">
    <img src="https://coveralls.io/repos/github/PhotonQuantum/pysjtu/badge.svg?branch=master" alt="Coverage Status">
</a>
</p>

![screenshot](docs/images/pysjtu.png)

---

```python
>>> import pysjtu
>>> session = pysjtu.Session(username="FeiLin", password="WHISPERS")
>>> client = pysjtu.Client(session)
>>> chemistry = client.schedule(year=2019, term=0).filter("大学化学")
>>> chemistry[0].teacher_name
['麦亦勇']
>>> calculus_exam = client.exam(year=2019, term=0).filter(course_id="MA248")
>>> calculus_exam[0].date
datetime.date(2019, 11, 6)
```

And, to persist your session...

```python
>>> import pysjtu
>>> session = pysjtu.Session()
>>> session.login("FeiLin", "WHISPERS")
>>> session.dump("lin_fei.session")

>>> session = pysjtu.Session()
>>> session.load("lin_fei.session")
>>> pysjtu.Client(session).student_id
519027910001
```

## Features

PySJTU allows you to manipulate [iSJTU](https://i.sjtu.edu.cn) APIs easily.

You don't need to construct queries on your own, or guessing the meaning of poorly named variables (to name a few, `kch_id`, `rwzxs`) any more. 
Now `course.name` `course.hour_total` is enough!

Main features of PySJTU:

- A friendly API with understandable attribute names.
- Easy session persistence.
- Robust captcha recognition using ResNet.
- 80% iSJTU APIs covered. (Course selection APIs will be implemented soon.)
- Fully type annotated.
- 99% test coverage.

## Installation

Install with pip from git:

```shell script
$ pip install git+https://github.com/PhotonQuantum/pysjtu.git
```

PySJTU requires Python 3.6+. This package will soon be available in PyPI.

## Built With

- [HTTPX](https://www.python-httpx.org/) - A next generation HTTP client for Python.
- [marshmallow](https://github.com/marshmallow-code/marshmallow) - An ORM/ODM/framework-agnostic library for converting complex datatypes, such as objects, to and from native Python datatypes.
- [ONNX Runtime](https://github.com/microsoft/onnxruntime) - A performance-focused complete scoring engine for Open Neural Network Exchange (ONNX) models.
- [NumPy](https://numpy.org/) - The fundamental package for scientific computing with Python.
- [Pillow](https://python-pillow.org/) - The friendly PIL fork.

## License

This project is licensed under GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

<p align="center">&mdash;💖&mdash;</p>
<p align="center"><i>Built with love by LightQuantum</i></p>
