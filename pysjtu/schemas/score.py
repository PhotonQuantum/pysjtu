import typing

from marshmallow import EXCLUDE, Schema, fields, post_load  # type: ignore

from pysjtu.schemas.base import ChineseBool


class ScoreFactorName(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return value[:value.find("(")]


class ScoreFactorPercentage(fields.Field):
    def _deserialize(
            self,
            value: typing.Any,
            attr: typing.Optional[str],
            data: typing.Optional[typing.Mapping[str, typing.Any]],
            **kwargs
    ):
        if not value:
            return None  # pragma: no cover
        return float(value[value.find("(") + 1:value.find("%")]) / 100


class ScoreFactorSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = ScoreFactorName(required=True, data_key="xmblmc")
    percentage = ScoreFactorPercentage(required=True, data_key="xmblmc", load_only=True)
    score = fields.String(required=True, data_key="xmcj")

    # noinspection PyUnusedLocal
    @post_load
    def wrap(self, data, **kwargs):
        return ScoreFactor(**data)


class ScoreSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True, data_key="kcmc")
    teacher = fields.Str(data_key="jsxm")
    score = fields.Str(required=True, data_key="cj")
    credit = fields.Float(required=True, data_key="xf")
    gp = fields.Float(required=True, data_key="jd")
    invalid = ChineseBool(data_key="cjsfzf")
    course_type = fields.Str(data_key="kcbj")
    category = fields.Str(data_key="kclbmc")
    score_type = fields.Str(data_key="ksxz")
    method = fields.Str(data_key="khfsmc")
    course_id = fields.Str(data_key="kch_id")
    class_name = fields.Str(data_key="jxbmc")
    class_id = fields.Str(data_key="jxb_id")

    # noinspection PyUnusedLocal
    @post_load
    def wrap(self, data, **kwargs):
        return Score(**data)


from pysjtu.models.score import Score, ScoreFactor
