iSJTU Interface
===============

Student ID
----------

.. autoattribute:: pysjtu.client.Client.student_id

**Example:**

To get the student id of current user:

.. sourcecode:: python

    client.student_id
    # 519027910001

Term Start Date
---------------

.. autoattribute:: pysjtu.client.Client.term_start_date

**Example:**

To get the start date of current term:

.. sourcecode:: python

    client.term_start_date
    # datetime.date(2019, 9, 9)

Schedule Query
--------------

.. automodule:: pysjtu.client.api.schedule
    :members:

.. automodule:: pysjtu.models.schedule
    :members:

**Example:**

To fetch your schedule of the first term in 2019, filter by criteria, and dig into details:

.. sourcecode:: python

    schedule = client.schedule(2019, 0)
    # [<ScheduleCourse 军事理论 week=[range(9, 17)] day=1 time=range(1, 3)>, ...]
    schedule.filter(time=[1, range(5, 7)], day=[2, range(4, 5)]))
    # [<ScheduleCourse 线性代数 week=[range(1, 7), range(8, 17)] day=2 time=range(1, 3)>,
    # <ScheduleCourse 线性代数 week=[7] day=2 time=range(1, 3)>,
    # <ScheduleCourse 思想道德修养与法律基础 week=[range(1, 17)] day=2 time=range(6, 9)>,
    # <ScheduleCourse 程序设计思想与方法（C++） week=[range(1, 16, 2)] day=4 time=range(1, 3)>]
    schedule[0].name
    # '军事理论'

Exam Query
----------

.. automodule:: pysjtu.client.api.exam
    :members:

.. automodule:: pysjtu.models.exam
    :members:

**Example:**

To get your exams of the first term in 2019, filter by criteria, and dig into details:

.. sourcecode:: python

    exams = client.exam(2019, 0)
    # [<Exam "2019-2020-1数学期中考" location=东上院509 datetime=2019-11-06(13:10-15:10)>, ...]
    exams.filter(date=datetime.date(2019, 12, 31))
    # [<Exam "2019-2020-1一专期末考（2019级）" location=东上院509 datetime=2019-12-31(08:00-10:00)>]
    exams[0].name
    # '2019-2020-1数学期中考'

Score Query
-----------

.. automodule:: pysjtu.models.score
    :members:

.. automodule:: pysjtu.client.api.score
    :members:

**Example:**

To get your exams of the first term in 2019, filter by criteria, and dig into details:

.. sourcecode:: python

    scores = client.score(2019, 0)
    # [<Score 大学化学 score=xx credit=x.x gp=x.x>, ...>
    scores.filter(gp=4)
    # [<Score xxxxx score=91 credit=2.0 gp=4.0>, ...]
    score = scores[0]
    # <Score 大学化学 score=xx credit=x.x gp=x.x>
    score.name
    # '大学化学'
    score_detail = score.detail
    # [<ScoreFactor 平时(40.0%)=xx.x>, <ScoreFactor 期末(60.0%)=xx.x>]
    score_detail[0].percentage
    # 0.4

GPA Query
---------

.. automodule:: pysjtu.models.gpa
    :members:

.. automodule:: pysjtu.client.api.gpa
    :members:

**Example:**

To fetch default GPA query parameters, change statistics scope and query GPA statistics:

.. sourcecode:: python

    query = client.default_gpa_query_params
    # <GPAQueryParams {...}>
    query.course_range = CourseRange.ALL
    gpa = client.gpa(query)
    # <GPA gp=98.9876543210 2/99 gpa=4.3 2/99>
    gpa.gpa
    # 4.3

College-Wide Course Search
--------------------------

.. automodule:: pysjtu.models.course
    :members:

.. automodule:: pysjtu.client.api.course
    :members:

**Example:**

To perform a college-wide course search:

.. sourcecode:: python

    courses = client.query_course(2019, 0, name="高等数学")
    # <pysjtu.model.base.QueryResult object at 0x7fd46439ac50>
    len(courses)
    # 90
    courses[-1]
    # <LibCourse 高等数学I class_name=(2019-2020-1)-MA248-20>
    courses[14:16]
    # [<LibCourse 高等数学III class_name=(2019-2020-1)-MA172-1>, <LibCourse 高等数学IV class_name=(2019-2020-1)-MA173-1>]
    list(courses)
    # [<LibCourse 高等数学A1 class_name=(2019-2020-1)-VV156-1>, <LibCourse 高等数学B1 class_name=(2019-2020-1)-VV186-1>, ...]
    courses[0].credit
    # 4.0

Course Selection
----------------

.. automodule:: pysjtu.models.selection
    :members:

.. automodule:: pysjtu.client.api.selection
    :members:
