import pickle
from pysjtu import api

with open("cookie", mode="rb") as f:
    cookie_jar = pickle.load(f)

sess = api.Session()
sess.cookies = cookie_jar
print(sess.schedule(2019, 1).all())
