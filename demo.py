import pickle
from pysjtu import api

with open("cookie", mode="rb") as f:
    cookie_jar = pickle.load(f)

sess = api.Session()
sess.cookies = cookie_jar
schedule = sess.schedule(2019, 1)
print(schedule.all())
print(schedule.filter(name="高等数学II"))
print(list(map(lambda x: x["name"], schedule.filter(week=2, day=range(1,3), time=[range(10,12), 1]))))
