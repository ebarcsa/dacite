from dataclasses import Field
from typing import TypeVar, Type, Optional, Mapping, Any, Union, Tuple

from dacite.data import Data

T = TypeVar("T")

SchemaUnion = Union[str, Mapping[str, Any], Tuple[str, Mapping[str, Union[str, Tuple[str, Any]]]]]
SchemaMapping = Mapping[str, SchemaUnion]


SCHEMA_ATTR = "_dacite_schema"


def map_field(field: str, schema: SchemaUnion):
    def decorator(cls):
        if not hasattr(cls, SCHEMA_ATTR):
            setattr(cls, SCHEMA_ATTR, {})
        cls._dacite_schema[field] = schema
        return cls
    return decorator


def map_fields(schema: SchemaMapping):
    def decorator(cls):
        if not hasattr(cls, SCHEMA_ATTR):
            setattr(cls, SCHEMA_ATTR, {})
        cls._dacite_schema = {**cls._dacite_schema, **schema}
        return cls
    return decorator


def _get_mapped_data_and_schema(
    data_class: Type[T], field: Field, data: Data, schema: Optional[SchemaMapping]
) -> Tuple[Any, Optional[SchemaMapping]]:
    if hasattr(data_class, SCHEMA_ATTR):
        if schema is None:
            schema = {}
        schema = {**getattr(data_class, SCHEMA_ATTR), **schema}
    print("{} {} {}".format(data_class, schema, field.name))
    if schema is not None and field.name in schema:
        field_schema = schema[field.name]
        print("{} {}".format(type(field_schema), field_schema))
        if isinstance(field_schema, str):
            return data[field_schema], None
        if isinstance(field_schema, tuple):
            parts = field_schema[0].split(".")
            for part in parts:
                data = data[part]
            return data, field_schema[1]
        if isinstance(field_schema, dict):
            return data[field.name], field_schema
        else:
            raise ValueError('Class {}, field "{}" has invalid schema: {}'.format(data_class, field.name, field_schema))
    return data[field.name], None
