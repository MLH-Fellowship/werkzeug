from __future__ import annotations

import collections.abc as cabc
import typing as t

from .mixins import ImmutableDictMixin
from .structures import CallbackDict


def cache_control_property(key: str, empty: t.Any, type: type[t.Any] | None) -> t.Any:
    """Return a new property object for a cache header. Useful if you
    want to add support for a cache extension in a subclass.

    .. versionchanged:: 2.0
        Renamed from ``cache_property``.
    """
    return property(
        lambda x: x._get_cache_value(key, empty, type),
        lambda x, v: x._set_cache_value(key, v, type),
        lambda x: x._del_cache_value(key),
        f"accessor for {key!r}",
    )


class _CacheControl(CallbackDict[str, t.Any]):
    """Subclass of a dict that stores values for a Cache-Control header.  It
    has accessors for all the cache-control directives specified in RFC 2616.
    The class does not differentiate between request and response directives.

    Because the cache-control directives in the HTTP header use dashes the
    python descriptors use underscores for that.

    To get a header of the :class:`CacheControl` object again you can convert
    the object into a string or call the :meth:`to_header` method.  If you plan
    to subclass it and add your own items have a look at the sourcecode for
    that class.

    .. versionchanged:: 3.1

       ``no_transform`` is a boolean when present.

    .. versionchanged:: 2.1.0
        Setting int properties such as ``max_age`` will convert the
        value to an int.

    .. versionchanged:: 0.4

       Setting `no_cache` or `private` to boolean `True` will set the implicit
       none-value which is ``*``:

       >>> cc = ResponseCacheControl()
       >>> cc.no_cache = True
       >>> cc
       <ResponseCacheControl 'no-cache'>
       >>> cc.no_cache
       '*'
       >>> cc.no_cache = None
       >>> cc
       <ResponseCacheControl ''>

       In versions before 0.5 the behavior documented here affected the now
       no longer existing `CacheControl` class.
    """

    no_cache: str | bool | None = cache_control_property("no-cache", "*", None)
    no_store: bool = cache_control_property("no-store", None, bool)
    max_age: int | None = cache_control_property("max-age", -1, int)
    no_transform: bool = cache_control_property("no-transform", None, bool)

    def __init__(
        self,
        values: cabc.Mapping[str, t.Any] | cabc.Iterable[tuple[str, t.Any]] | None = (),
        on_update: cabc.Callable[[_CacheControl], None] | None = None,
    ):
        super().__init__(values, on_update)
        self.provided = values is not None

    def _get_cache_value(
        self, key: str, empty: t.Any, type: type[t.Any] | None
    ) -> t.Any:
        """Used internally by the accessor properties."""
        if type is bool:
            return key in self
        if key in self:
            value = self[key]
            if value is None:
                return empty
            elif type is not None:
                try:
                    value = type(value)
                except ValueError:
                    pass
            return value
        return None

    def _set_cache_value(
        self, key: str, value: t.Any, type: type[t.Any] | None
    ) -> None:
        """Used internally by the accessor properties."""
        if type is bool:
            if value:
                self[key] = None
            else:
                self.pop(key, None)
        else:
            if value is None:
                self.pop(key, None)
            elif value is True:
                self[key] = None
            else:
                if type is not None:
                    self[key] = type(value)
                else:
                    self[key] = value

    def _del_cache_value(self, key: str) -> None:
        """Used internally by the accessor properties."""
        if key in self:
            del self[key]

    def to_header(self) -> str:
        """Convert the stored values into a cache control header."""
        return http.dump_header(self)

    def __str__(self) -> str:
        return self.to_header()

    def __repr__(self) -> str:
        kv_str = " ".join(f"{k}={v!r}" for k, v in sorted(self.items()))
        return f"<{type(self).__name__} {kv_str}>"

    cache_property = staticmethod(cache_control_property)


class RequestCacheControl(ImmutableDictMixin[str, t.Any], _CacheControl):  # type: ignore[misc]
    """A cache control for requests.  This is immutable and gives access
    to all the request-relevant cache control headers.

    To get a header of the :class:`RequestCacheControl` object again you can
    convert the object into a string or call the :meth:`to_header` method.  If
    you plan to subclass it and add your own items have a look at the sourcecode
    for that class.

    .. versionchanged:: 3.1
       ``no_transform`` is a boolean when present.

    .. versionchanged:: 3.1
       ``min_fresh`` is ``None`` if a value is not provided for the attribute.

    .. versionchanged:: 2.1.0
        Setting int properties such as ``max_age`` will convert the
        value to an int.

    .. versionadded:: 0.5
       In previous versions a `CacheControl` class existed that was used
       both for request and response.
    """

    max_stale: str | int | None = cache_control_property("max-stale", "*", int)
    min_fresh: int | None = cache_control_property("min-fresh", None, int)
    only_if_cached: bool = cache_control_property("only-if-cached", None, bool)


class ResponseCacheControl(_CacheControl):
    """A cache control for responses.  Unlike :class:`RequestCacheControl`
    this is mutable and gives access to response-relevant cache control
    headers.

    To get a header of the :class:`ResponseCacheControl` object again you can
    convert the object into a string or call the :meth:`to_header` method.  If
    you plan to subclass it and add your own items have a look at the sourcecode
    for that class.

    .. versionchanged:: 3.1
       ``no_transform`` is a boolean when present.

    .. versionchanged:: 3.1
        Added the ``must_understand``, ``stale_while_revalidate``, and
        ``stale_if_error`` attributes.

    .. versionchanged:: 2.1.1
        ``s_maxage`` converts the value to an int.

    .. versionchanged:: 2.1.0
        Setting int properties such as ``max_age`` will convert the
        value to an int.

    .. versionadded:: 0.5
       In previous versions a `CacheControl` class existed that was used
       both for request and response.
    """

    public: bool = cache_control_property("public", None, bool)
    private: str | None = cache_control_property("private", "*", None)
    must_revalidate: bool = cache_control_property("must-revalidate", None, bool)
    proxy_revalidate: bool = cache_control_property("proxy-revalidate", None, bool)
    s_maxage: int | None = cache_control_property("s-maxage", None, int)
    immutable: bool = cache_control_property("immutable", None, bool)
    must_understand: bool = cache_control_property("must-understand", None, bool)
    stale_while_revalidate: int | None = cache_control_property(
        "stale-while-revalidate", None, int
    )
    stale_if_error: int | None = cache_control_property("stale-if-error", None, int)


# circular dependencies
from .. import http
