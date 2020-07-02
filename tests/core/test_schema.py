from dataclasses import dataclass

import pytest

import dacite
from dacite import from_dict


def test_from_dict_with_naming_changed():
    @dataclass
    class X:
        s: str
        i: int
        f: float

    result = from_dict(X, data={"s": "test", "k": 2, "j": 2.3}, schema={"i": "k", "f": "j"})

    assert result == X(s="test", i=2, f=2.3)


def test_from_dict_with_single_map_field_decorator_without_schema():
    @dataclass
    @dacite.map_field("i", "k")
    class X:
        s: str
        i: int

    result = from_dict(X, data={"s": "test", "k": 2, "j": 2.3})

    assert result == X(s="test", i=2)


def test_from_dict_with_single_map_field_decorator_with_schema():
    @dataclass
    @dacite.map_field("i", "k")
    class X:
        s: str
        i: int
        f: float

    result = from_dict(X, data={"s": "test", "k": 2, "j": 2.3}, schema={"f": "j"})

    assert result == X(s="test", i=2, f=2.3)


def test_from_dict_with_multiple_map_field_decorator():
    @dataclass
    @dacite.map_field("i", "k")
    @dacite.map_field("f", "j")
    class X:
        s: str
        i: int
        f: float

    result = from_dict(X, data={"s": "test", "k": 2, "j": 2.3})

    assert result == X(s="test", i=2, f=2.3)


def test_from_dict_with_single_map_fields_decorator():
    @dataclass
    @dacite.map_fields({"i": "k", "f": "j"})
    class X:
        s: str
        i: int
        f: float

    result = from_dict(X, data={"s": "test", "k": 2, "j": 2.3})

    assert result == X(s="test", i=2, f=2.3)


def test_from_dict_with_multiple_map_fields_decorator():
    @dataclass
    @dacite.map_fields({"i": "k"})
    @dacite.map_fields({"f": "j"})
    class X:
        s: str
        i: int
        f: float

    result = from_dict(X, data={"s": "test", "k": 2, "j": 2.3})

    assert result == X(s="test", i=2, f=2.3)


def test_from_dict_with_mixed_map_field_s_decorator():
    @dataclass
    @dacite.map_fields({"i": "k"})
    @dacite.map_field("f", "j")
    class X:
        s: str
        i: int
        f: float

    result = from_dict(X, data={"s": "test", "k": 2, "j": 2.3})

    assert result == X(s="test", i=2, f=2.3)


def test_from_dict_with_nested_object_name_change():
    @dataclass
    class Y:
        x: str
        y: int

    @dataclass
    class X:
        s: str
        i: int
        f: Y

    result = from_dict(
        X,
        data={"s": "testX", "k": 2, "j": {"l": 1, "y": {"x": "testY", "l": 3}}},
        schema={"i": "k", "f": ("j.y", {"y": "l"})},
    )

    assert result == X(s="testX", i=2, f=Y("testY", 3))


def test_from_dict_with_deeply_nested_object():
    @dataclass
    @dacite.map_field("a", "h")
    class Z:
        a: str
        b: int

    @dataclass
    class Y:
        x: str
        y: Z

    @dataclass
    class X:
        s: str
        i: int
        f: Y

    result = from_dict(
        X,
        data={"s": "testX", "k": 2, "j": {"l": 1, "y": {"l": 1, "y": {"x": "testY", "y": {"h": "testZ", "m": 2}}}}},
        schema={"i": "k", "f": ("j.y.y", {"y": {"b": "m"}})},
    )

    assert result == X(s="testX", i=2, f=Y(x="testY", y=Z(a="testZ", b=2)))


def test_from_dict_with_simple_invalid_schema():
    @dataclass
    class X:
        s: str
        i: int

    with pytest.raises(ValueError) as exception_info:
        from_dict(X, data={"s": "testX", "i": 3}, schema={"s": None})

    err = str(exception_info.value)
    assert "invalid schema" in err and "X" in err and '"s"' in err and "None" in err


def test_from_dict_with_invalid_scheme_nested():
    @dataclass
    class Y:
        x: str
        y: int

    @dataclass
    class X:
        s: str
        f: Y

    with pytest.raises(ValueError) as exception_info:
        from_dict(X, data={"s": "testX", "f": {"x": 1, "m": 3}}, schema={"f": {"y", "m"}})

    err = str(exception_info.value)
    assert "invalid schema" in err and "X" in err and '"f"' in err
