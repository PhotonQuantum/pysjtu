from pysjtu import Session, Client
import arrow
from ics import Calendar, Event
from datetime import datetime, timezone, timedelta, time, date
import collections
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

def flatten(obj):
    for el in obj:
        if isinstance(el, collections.abc.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

client = Client(Session(username="LightQuantum", password="4qi6FeAWg2NDtRoo", base_url="http://kbcx.sjtu.edu.cn"))
schedule = client.schedule(2019, 1)
term_start = client.term_start_date

c = Calendar()
local_tz = datetime.now(timezone.utc).astimezone().tzinfo
for lesson in schedule:
    if "暂不开课" not in lesson.remark:
        for week in [0] + list(flatten(lesson.week)):
            lesson_day = term_start + timedelta(days=lesson.day + (week - 1) * 7-1)
            begin_time = time(*lesson_time[lesson.time[0]-1][0])
            end_time = time(*lesson_time[lesson.time[-1]-1][1])
            e = Event()
            e.name = lesson.name
            e.begin = arrow.get(datetime.combine(lesson_day, begin_time, local_tz))
            e.end = arrow.get(datetime.combine(lesson_day, end_time, local_tz))
            e.location = lesson.remark
            c.events.add(e)

fn = input("Output file[*.ics]:")
with open(fn, mode="w", encoding="utf-8") as f:
    f.write(str(c))
