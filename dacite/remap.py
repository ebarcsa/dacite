from dataclasses import Field
from typing import TypeVar, Type, Optional, Mapping, Any, Union, Tuple

from dacite.data import Data

T = TypeVar("T")

RemapUnion = Union[str, Mapping[str, Any], Tuple[str, Mapping[str, Union[str, Tuple[str, Any]]]]]
RemapMapping = Mapping[str, RemapUnion]


SCHEMA_ATTR = "_dacite_remap"


def map_field(field: str, remap: RemapUnion):
    def decorator(cls):
        if not hasattr(cls, SCHEMA_ATTR):
            setattr(cls, SCHEMA_ATTR, {})
        cls._dacite_remap[field] = remap
        return cls
    return decorator


def map_fields(remap: RemapMapping):
    def decorator(cls):
        if not hasattr(cls, SCHEMA_ATTR):
            setattr(cls, SCHEMA_ATTR, {})
        cls._dacite_remap = {**cls._dacite_remap, **remap}
        return cls
    return decorator


def _get_mapped_data_and_remap(
    data_class: Type[T], field: Field, data: Data, remap: Optional[RemapMapping]
) -> Tuple[Any, Optional[RemapMapping]]:
    if hasattr(data_class, SCHEMA_ATTR):
        if remap is None:
            remap = {}
        remap = {**getattr(data_class, SCHEMA_ATTR), **remap}
    if remap is not None and field.name in remap:
        field_remap = remap[field.name]
        if isinstance(field_remap, str):
            return data[field_remap], None
        if isinstance(field_remap, tuple):
            parts = field_remap[0].split(".")
            for part in parts:
                data = data[part]
            return data, field_remap[1]
        if isinstance(field_remap, dict):
            return data[field.name], field_remap
        else:
            raise ValueError('Class {}, field "{}" has invalid remap: {}'.format(data_class, field.name, field_remap))
    return data[field.name], None
