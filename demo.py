import os
from datetime import datetime, timezone

import arrow
from ics import Calendar, Event

from pysjtu import api, model

lesson_time = (((8, 0), (8, 45)),
               ((8, 55), (9, 40)),
               ((10, 0), (10, 45)),
               ((10, 55), (11, 40)),
               ((12, 0), (12, 45)),
               ((12, 55), (13, 40)),
               ((14, 0), (14, 45)),
               ((14, 55), (15, 40)),
               ((16, 0), (16, 45)),
               ((16, 55), (17, 40)),
               ((18, 0), (18, 45)),
               ((18, 55), (19, 40)),
               ((19, 55), (20, 40)),
               ((20, 55), (21, 40)))

sess = api.Session()
try:
    with open("session", mode="rb") as f:
        sess.load(f)
except (api.SessionException, FileNotFoundError) as e:
    print("session invalid, login")
    sess.login(os.environ["SJTU_USER"], os.environ["SJTU_PASS"])
print(sess.student_id)
schedule = sess.schedule(2019, 1)
print(schedule.all())
print(schedule.filter(name="高等数学II"))
print(list(map(lambda x: x.name, schedule.filter(week=2, day=range(1, 3), time=[range(10, 12), 1]))))

c = Calendar()
local_tz = datetime.now(timezone.utc).astimezone().tzinfo
for lesson in schedule.all():
    e = Event()
    e.name = lesson.name
    e.begin = arrow.get(datetime(2020, 1, 5 + lesson.day, *lesson_time[lesson.time[0] - 1][0], tzinfo=local_tz))
    e.end = arrow.get(datetime(2020, 1, 5 + lesson.day, *lesson_time[lesson.time[-1] - 1][1], tzinfo=local_tz))
    e.location = lesson.location
    c.events.add(e)

with open("test.ics", mode="w") as f:
    f.write(str(c))

score = sess.score(2019, 0)
print(score.all())
print(score.all()[0].detail)

exam = sess.exam(2019, 0)
print(exam.all())

query = sess.query_courses(2019, 0, name="高等数学")
print(query[3:18])
for item in query:
    print(item, end=" ")
print()

print(sess.term_start_date)

query_params = sess.default_gpa_query_params

print(sess.query_gpa(query_params, 10))

query_params.course_range = model.CourseRange.ALL
print(sess.query_gpa(query_params, 10))

with open("session", mode="wb") as f:
    sess.dump(f)
