import sys
from dataclasses import Field
from typing import TypeVar, Type, Optional, Mapping, Any, Union, Tuple

from dacite.data import Data
from dacite.exceptions import DaciteError

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


def _try_keys(data, *keys):
    for key in keys:
        if key in data:
            return data[key]
    error = 'Keys {} not found in : {}'.format(keys, data)
    print(error, file=sys.stderr)
    raise DaciteError(error)


def _follow_nested_keys(data, field_name, mapped_key):
    orig_data = data
    parts = mapped_key.split(".")
    for part in parts:
        if part not in data:
            return _try_keys(orig_data, field_name, parts[0])
        data = data[part]
    return data


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
            return _follow_nested_keys(data, field.name, field_remap), None
        if isinstance(field_remap, tuple):
            return _follow_nested_keys(data, field.name, field_remap[0]), field_remap[1]
        if isinstance(field_remap, dict):
            return data[field.name], field_remap
        else:
            error = 'Class {}, field "{}" has invalid remap: {}'.format(data_class, field.name, field_remap)
            print(error, file=sys.stderr)
            raise DaciteError(error)
    return data[field.name], None
