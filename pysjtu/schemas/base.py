import typing

from marshmallow import ValidationError, fields  # type: ignore

from pysjtu.utils import parse_course_week


class StrBool(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        if value in ["0"]:
            return False
        if value in ["1"]:
            return True
        raise ValidationError("StrBool values must be one of [0, 1].")

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        if value is None:
            return ""  # pragma: no cover
        if value is False:
            return "0"
        if value is True:
            return "1"
        raise ValidationError("Invalid bool value.")


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


class SplitField(fields.Field):
    def __init__(self, sep: str, *args, **kwargs):
        self.sep = sep
        super().__init__(*args, **kwargs)

    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return value.split(self.sep)

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs):
        return self.sep.join(str(item) for item in value)


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
