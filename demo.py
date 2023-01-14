import os

from pysjtu import Session, Client, CourseRange, JCSSRecognizer, create_client

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

try:
    sess_file = open("session", mode="r+b")
except FileNotFoundError:
    sess_file = None  # type: ignore

client = create_client(os.environ["SJTU_USER"], os.environ["SJTU_PASS"])

with Session(session_file=sess_file, ocr=JCSSRecognizer()) if sess_file else Session(username=os.environ["SJTU_USER"],
                                                                                     password=os.environ["SJTU_PASS"],
                                                                                     ocr=JCSSRecognizer()) as sess:
    client = Client(session=sess)

    query_params = client.default_gpa_query_params

    print(client.gpa(query_params, timeout=30))

    query_params.course_range = CourseRange.ALL
    print(client.gpa(query_params, timeout=30))

    if not sess_file:
        sess.dump(open("session", mode="wb"))
