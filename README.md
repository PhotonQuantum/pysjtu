<p align="center"><strong>PYSJTU</strong> <em>- The Python iSJTU client for Humans.</em></p>

<p align="center">
<a href="https://circleci.com/gh/PhotonQuantum/pysjtu">
    <img src="https://circleci.com/gh/PhotonQuantum/pysjtu.svg?style=shield" alt="CircleCI">
</a>
<a href="https://coveralls.io/github/PhotonQuantum/pysjtu?branch=master">
    <img src="https://coveralls.io/repos/github/PhotonQuantum/pysjtu/badge.svg?branch=master" alt="Coverage Status">
</a>
</p>

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
'519027910001'
```

## Features

PYSJTU allows you to manipulate [iSJTU](https://i.sjtu.edu.cn) APIs easily.

You don't need to construct queries on your own, or guessing the meaning of poorly named variables (to name a few, `kch_id`, `rwzxs`) any more. 
Now `course.name` `course.hour_total` is enough!

<p align="center">&mdash;💖&mdash;</p>
<p align="center"><i>Built with love by LightQuantum</i></p>
