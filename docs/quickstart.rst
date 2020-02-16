QuickStart
==========

PySJTU supports Python 3.6+, and there's no plan to support Python 2. So you need to have Python 3.6 or higher installed.

Installation
------------

To install PySJTU, simply use pip:

.. sourcecode:: sh

    $ pip install pysjtu

And you may want to add this package into your requirements.txt:

.. sourcecode:: sh

    git+https://github.com/PhotonQuantum/pysjtu.git

Making Queries
--------------

Begin by importing PySJTU:

.. sourcecode:: python

    >>> import pysjtu

Then, login JAccount and create a client:

.. sourcecode:: python

    >>> c = pysjtu.create_client(username="<username>", password="<password>")
    >>> c.student_id
    519027910001

There's no need to input captcha manually. A built-in captcha recognizer will handle this for you.
To customize captcha recognizer, see :ref:`OCR`.

Next, try to get your schedule of the first term in 2019, and print all of your courses:

.. sourcecode:: python

    >>> sched = c.schedule(2019, 0)
    >>> sched
    [<ScheduleCourse 军事理论 week=[range(9, 17)] day=1 time=range(1, 3)>, ...]

You can fetch your scores, and exam schedule in the same way.

.. sourcecode:: python

    >>> scores = c.score(2019, 0)
    >>> exams = c.exam(2019, 0)

Be aware that GPA query and college-wide course search don't follow this query style:

GPA query accepts special query parameters encapsulated in :class:`GPAQueryParams`.
Default parameters can be fetched by reading `default_gpa_query_params`.

.. sourcecode:: python

    >>> gpa = c.gpa(c.default_gpa_query_params)

While college-wide course searches accepts a bunch of criteria, for example:

.. sourcecode:: python

    >>> courses = c.query_courses(2019, 0, name="高等数学", day_of_week=1, ...)

For detailed usages, see :ref:`iSJTU Interface`.

Result Content
--------------

PySJTU will deserialize HTTP responses into :class:`Result` objects.

Basically you will get a list(-like object) containing :class:`Result` objects, for example:

.. sourcecode:: python

    >>> sched[0]
    <ScheduleCourse 军事理论 week=[range(9, 17)] day=1 time=range(1, 3)>

And for most queries (except college-wide course searches), there's an additional `filter` method:

.. sourcecode:: python

    >>> sched.filter(time=range(3,5), day=range(2, 4))
    [<ScheduleCourse 程序设计思想与方法（C++） week=[range(1, 10), range(11, 17)] day=2 time=range(3, 5)>,
    <ScheduleCourse 大学英语（4） week=[range(1, 17)] day=3 time=range(3, 5)>]

These :class:`Result` objects offer a developer-friendly interface to query results:

.. sourcecode:: python

    >>> sched[0].name
    '军事理论'
    >>> sched[0].credit
    0.5

For detailed usages, see :ref:`iSJTU Interface` and :ref:`Developer Interface`.

Timeout
-------

By using HTTPX, PySJTU shares the same strict timeout rules with HTTPX. If a connection is not properly established,
an exception will be raised.

The default timeout is 5 seconds. This value can be modified:

.. sourcecode:: python

    >>> c.schedule(2019, 0, timeout=1)

And it can completely be disabled:

.. sourcecode:: python

    >>> c.schedule(2019, 0, timeout=None)

For advanced timeout management, see :ref:`Timeout Configuration`.

Exceptions
----------

.. autoexception:: pysjtu.exceptions.SessionException

.. autoexception:: pysjtu.exceptions.LoginException

.. autoexception:: pysjtu.exceptions.GPACalculationException

.. autoexception:: pysjtu.exceptions.ServiceUnavailable
