from .util import overlap


class ScheduleCourse:
    _members = ["name", "day", "week", "time", "location", "credit", "assessment", "remark", "teacher", "meta",
                "class_hour"]

    def __init__(self, **kwargs):
        for member in self._members:
            setattr(self, member, None)
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"<ScheduleCourse name={self.name} week={self.week} day={self.day} time={self.time}>"


class Schedule:
    _courses = []

    def load(self, data):
        schema = CourseSchema(many=True)
        self._courses = schema.load(data)

    def all(self):
        return self._courses

    def filter(self, **param):
        rtn = self._courses
        for (k, v) in param.items():
            if not hasattr(ScheduleCourse(), k):
                raise KeyError("Invalid criteria!")
            if k in ("week", "time", "day"):
                rtn = list(filter(lambda x: overlap(getattr(x, k), v), rtn))
            else:
                rtn = list(filter(lambda x: getattr(x, k) == v, rtn))
        return rtn


from .schema import *
