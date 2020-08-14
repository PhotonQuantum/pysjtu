import os

from pysjtu import AsyncSession, Client, CourseRange, JCSSRecognizer
from pysjtu.exceptions import GPACalculationException
import asyncio

# from datetime import datetime, timezone
# import arrow
# from ics import Calendar, Event

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

async def main():
    try:
        sess_file = open("session", mode="r+b")
    except FileNotFoundError:
        sess_file = None    # type: ignore

    async with JCSSRecognizer("https://jcss.lightquantum.me") as ocr_module:
        async with AsyncSession(session_file=sess_file, ocr=ocr_module) if sess_file else AsyncSession(username=os.environ["SJTU_USER"],
                                                                       password=os.environ["SJTU_PASS"], ocr=ocr_module) as sess:
            client = Client(session=sess)

            print(await client.student_id)
            schedule = await client.schedule(2019, 1)
            print(schedule)
            print(schedule.filter(name="高等数学II"))
            return
            print(list(map(lambda x: x.name, schedule.filter(week=2, day=range(1, 3), time=[range(10, 12), 1]))))

            '''
            c = Calendar()
            local_tz = datetime.now(timezone.utc).astimezone().tzinfo
            for lesson in schedule:
                e = Event()
                e.name = lesson.name
                e.begin = arrow.get(datetime(2020, 1, 5 + lesson.day, *lesson_time[lesson.time[0] - 1][0], tzinfo=local_tz))
                e.end = arrow.get(datetime(2020, 1, 5 + lesson.day, *lesson_time[lesson.time[-1] - 1][1], tzinfo=local_tz))
                e.location = lesson.location
                c.events.add(e)

            with open("test.ics", mode="w") as f:
                f.write(str(c))
            '''

            score = await client.score(2019, 0)
            print(score)
            print(await score[0].detail)

            exam = await client.exam(2019, 0)
            print(exam)

            query = await client.query_courses(2019, 0, name="高等数学")
            print(await query[3:18])
            async for item in query:
                print(item, end=" ")
            print()

            print(await client.term_start_date)
            query_params = await client.default_gpa_query_params

            try:
                print(await client.gpa(query_params))

                query_params.course_range = CourseRange.ALL
                print(await client.gpa(query_params))
            except GPACalculationException:
                print("gpa can't be read.")

            if not sess_file:
                sess.dump(open("session", mode="wb"))

if __name__ == "__main__":
    asyncio.run(main())