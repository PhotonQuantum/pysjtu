import typing
from dataclasses import MISSING, field
from typing import Type, Union, TypeVar, Optional, Callable

import marshmallow
import marshmallow_dataclass
from marshmallow import Schema, pre_load, pre_dump, post_load, post_dump, fields

from pysjtu.utils import replace_keys


class HookedSchema(Schema):
    """ A Schema that supports hooks.

    This is a helper wrapper for :class:`marshmallow.Schema`, which supports ordered hooks.

    The original decorator hooks provided by marshmallow do not ensure execution order if multiple hooks present.
    This class uses inheritance to ensure execution order.

    To use this class, inherit from it and use :func:`pysjtu.schema.FinalizeHook` to transform the class into a Schema.
    """

    def pre_load(self, data, **kwargs):
        return data

    def pre_dump(self, data, **kwargs):
        return data

    def post_load(self, data, **kwargs):
        return data

    def post_dump(self, data, **kwargs):
        return data


def FinalizeHook(cls: Type[HookedSchema]) -> Type[Schema]:
    """ Transform a HookedSchema into a Schema."""

    class FinalizedSchema(cls):
        @pre_load
        def pre_load(self, data, **kwargs):
            return super().pre_load(data, **kwargs)

        @pre_dump
        def pre_dump(self, data, **kwargs):
            return super().pre_dump(data, **kwargs)

        @post_load
        def post_load(self, data, **kwargs):
            return super().post_load(data, **kwargs)

        @post_dump
        def post_dump(self, data, **kwargs):
            return super().post_dump(data, **kwargs)

    return FinalizedSchema


class LoadDumpSchema(HookedSchema):
    """ A Schema that supports load and dump key renaming.

    Use `load_key` and `dump_key` in field metadata to specify the key to be used in load and dump.
    """

    def pre_load(self, data, **kwargs):
        pairs = tuple(
            (field.metadata['load_key'], field.data_key or field_name)
            for field_name, field in self.fields.items() if 'load_key' in field.metadata
        )
        return replace_keys(data, pairs)

    def post_dump(self, data, **kwargs):
        pairs = tuple(
            (field.data_key or field_name, field.metadata['dump_key'])
            for field_name, field in self.fields.items() if 'dump_key' in field.metadata
        )
        return replace_keys(data, pairs)


class UNSET:
    pass


def mfield(default: typing.Any = MISSING, *, required: bool = False, raw: bool = False,
           load_key: Union[str, UNSET] = UNSET, dump_key: Union[str, UNSET] = UNSET,
           data_key: Union[str, UNSET] = UNSET,
           load_default: Union[typing.Any, UNSET] = UNSET, dump_default: Union[typing.Any, UNSET] = UNSET,
           **kwargs):
    """ Helper method to create a marshmallow field with metadata.

    This method is a wrapper for :func:`dataclasses.field` that adds metadata to the field.
    It also supports the `load_key` and `dump_key` metadata, which are used by :class:`LoadDumpSchema`.
    """
    metadata = kwargs.setdefault("metadata", dict())
    for k in ["load_key", "dump_key"]:
        if locals()[k] is not UNSET:
            metadata[k] = locals()[k]
    for k in ["required", "data_key", "load_default", "dump_default"]:
        if locals()[k] is not UNSET:
            kwargs[k] = locals()[k]
    if raw:
        kwargs["marshmallow_field"] = fields.Raw
    return field(default=default, metadata=kwargs)


T = TypeVar("T")


def WithField(ty: Type[T], field: Optional[Type[marshmallow.fields.Field]] = None, **kwargs) -> Callable[[T], T]:
    """ Helper functor to attach custom serializer/deserializer to a field.

    :param ty: The type of the field.
    :param field: The marshmallow field (serializer/deserializer) to be attached.
    """
    if isinstance(ty, typing._GenericAlias):
        ty_name = str(ty)
    elif isinstance(ty, type):
        ty_name = ty.__name__
    else:
        raise TypeError("ty must be a type or a typing._GenericAlias")

    return marshmallow_dataclass.NewType(ty_name, ty, field=field, **kwargs)
