import typing

from marshmallow import fields  # type: ignore

from pysjtu.utils import parse_course_week


class ChineseBool(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return value == "是"


class CommaSplitted(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return value.split(",")

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        return ",".join(str(item) for item in value)


class CourseTime(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        value = value.replace("节", "")
        cs = list(map(int, value.split("-")))
        return list(cs) if len(cs) == 1 else range(cs[0], cs[1] + 1)


class CreditHourDetail(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        class_hour_details = value.split(",")
        rtn = {}
        for item in class_hour_details:
            try:
                name, hour = item.split(":")
                rtn[name] = float(hour)
            except ValueError:
                rtn["N/A"] = 0
        return rtn


class CourseWeek(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return parse_course_week(value)


class ColonSplitted(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return value.split(";")

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        return ";".join(str(item) for item in value)  # pragma: no cover


class BrSplitted(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return value.split("<br/>")

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        return "<br/>".join(str(item) for item in value)  # pragma: no cover
