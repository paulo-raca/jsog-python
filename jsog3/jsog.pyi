from _typeshed import SupportsRead
from collections.abc import Callable
from typing import IO, Any
from json import JSONEncoder, JSONDecoder

__all__ = ["dump", "dumps", "load", "loads", "encode", "decode"]

# Typing for dump/dumps/load/loads were extracted from Python's typeshed library:
# https://github.com/python/typeshed/blob/master/stdlib/json/__init__.pyi

def dumps(
    obj: Any,
    *,
    skipkeys: bool = ...,
    ensure_ascii: bool = ...,
    check_circular: bool = ...,
    allow_nan: bool = ...,
    cls: type[JSONEncoder] | None = ...,
    indent: None | int | str = ...,
    separators: tuple[str, str] | None = ...,
    default: Callable[[Any], Any] | None = ...,
    sort_keys: bool = ...,
    **kwds: Any,
) -> str: ...
def dump(
    obj: Any,
    fp: IO[str],
    *,
    skipkeys: bool = ...,
    ensure_ascii: bool = ...,
    check_circular: bool = ...,
    allow_nan: bool = ...,
    cls: type[JSONEncoder] | None = ...,
    indent: None | int | str = ...,
    separators: tuple[str, str] | None = ...,
    default: Callable[[Any], Any] | None = ...,
    sort_keys: bool = ...,
    **kwds: Any,
) -> None: ...
def loads(
    s: str | bytes,
    *,
    cls: type[JSONDecoder] | None = ...,
    object_hook: Callable[[dict[Any, Any]], Any] | None = ...,
    parse_float: Callable[[str], Any] | None = ...,
    parse_int: Callable[[str], Any] | None = ...,
    parse_constant: Callable[[str], Any] | None = ...,
    object_pairs_hook: Callable[[list[tuple[Any, Any]]], Any] | None = ...,
    **kwds: Any,
) -> Any: ...
def load(
    fp: SupportsRead[str | bytes],
    *,
    cls: type[JSONDecoder] | None = ...,
    object_hook: Callable[[dict[Any, Any]], Any] | None = ...,
    parse_float: Callable[[str], Any] | None = ...,
    parse_int: Callable[[str], Any] | None = ...,
    parse_constant: Callable[[str], Any] | None = ...,
    object_pairs_hook: Callable[[list[tuple[Any, Any]]], Any] | None = ...,
    **kwds: Any,
) -> Any: ...

def encode(original: Any) -> Any: ...

def decode(encoded: Any) -> Any: ...
