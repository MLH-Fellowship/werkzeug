import sys
import operator
try:
    import builtins
except ImportError:
    import __builtin__ as builtins


PY2 = sys.version_info[0] == 2

_identity = lambda x: x

if PY2:
    unichr = unichr
    text_type = unicode
    string_types = (str, unicode)
    integer_types = (int, long)

    iterkeys = lambda d, *args, **kwargs: d.iterkeys(*args, **kwargs)
    itervalues = lambda d, *args, **kwargs: d.itervalues(*args, **kwargs)
    iteritems = lambda d, *args, **kwargs: d.iteritems(*args, **kwargs)

    iterlists = lambda d, *args, **kwargs: d.iterlists(*args, **kwargs)
    iterlistvalues = lambda d, *args, **kwargs: d.iterlistvalues(*args, **kwargs)

    exec('def reraise(tp, value, tb=None):\n raise tp, value, tb')

    def implements_iterator(cls):
        cls.next = cls.__next__
        del cls.__next__
        return cls

    def implements_to_string(cls):
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: x.__unicode__().encode('utf-8')
        return cls

    def implements_bool(cls):
        cls.__nonzero__ = cls.__bool__
        del cls.__bool__
        return cls

    from itertools import imap, izip, ifilter
    xrange = xrange

    from StringIO import StringIO, StringIO as BytesIO
    NativeStringIO = BytesIO

    def make_literal_wrapper(reference):
        return lambda x: x

    def normalize_string_tuple(tup):
        """Normalizes a string tuple to a common type. Following Python 2
        rules, upgrades to unicode are implicit.
        """
        if any(isinstance(x, text_type) for x in tup):
            return tuple(to_unicode(x) for x in tup)
        return tup

    def try_coerce_native(s):
        """Try to coerce a unicode string to native if possible. Otherwise,
        leave it as unicode.
        """
        try:
            return str(s)
        except UnicodeError:
            return s

    def wsgi_decoding_dance(s, charset='utf-8', errors='replace'):
        return s.decode(charset)

    def wsgi_encoding_dance(s, charset='utf-8', errors='replace'):
        return s.encode(charset)

    def to_bytes(x, charset=sys.getdefaultencoding(), errors='strict'):
        """please use carefully"""
        if x is None:
            return None
        if isinstance(x, unicode):
            return x.encode(charset, errors)
        return str(x)

    def to_native(x, charset=sys.getdefaultencoding(), errors='strict'):
        """please use carefully"""
        if x is None or isinstance(x, str):
            return x
        return x.encode(charset, errors)

else:
    unichr = chr
    text_type = str
    string_types = (str, )
    integer_types = (int, )

    iterkeys = lambda d, *args, **kwargs: iter(d.keys(*args, **kwargs))
    itervalues = lambda d, *args, **kwargs: iter(d.values(*args, **kwargs))
    iteritems = lambda d, *args, **kwargs: iter(d.items(*args, **kwargs))

    iterlists = lambda d, *args, **kwargs: iter(d.lists(*args, **kwargs))
    iterlistvalues = lambda d, *args, **kwargs: iter(d.listvalues(*args, **kwargs))

    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    implements_iterator = _identity
    implements_to_string = _identity
    implements_bool = _identity
    imap = map
    izip = zip
    ifilter = filter
    xrange = range

    from io import StringIO, BytesIO
    NativeStringIO = StringIO

    def make_literal_wrapper(reference):
        if isinstance(reference, text_type):
            return lambda x: x
        return lambda x: x.encode('latin1')

    def normalize_string_tuple(tup):
        """Ensures that all types in the tuple are either strings
        or bytes.
        """
        tupiter = iter(tup)
        is_text = isinstance(next(tupiter, None), text_type)
        for arg in tupiter:
            if isinstance(arg, text_type) != is_text:
                raise TypeError('Cannot mix str and bytes arguments (got %s)'
                    % repr(tup))
        return tup

    try_coerce_native = _identity

    def wsgi_decoding_dance(s, charset='utf-8', errors='replace'):
        return s.encode('latin1').decode(charset, errors)

    def wsgi_encoding_dance(s, charset='utf-8', errors='replace'):
        return s.encode(charset).decode('latin1', errors)

    def to_bytes(x, charset=sys.getdefaultencoding(), errors='strict'):
        """please use carefully"""
        if x is None:
            return None
        if not isinstance(x, bytes):
            x = str(x).encode(charset, errors)
        return x

    def to_native(x, charset=sys.getdefaultencoding(), errors='strict'):
        """please use carefully"""
        if x is None or isinstance(x, str):
            return x
        return x.decode(charset, errors)


def to_unicode(x, charset=sys.getdefaultencoding(), errors='strict'):
    """please use carefully"""
    if x is None:
        return None
    if not isinstance(x, bytes):
        return text_type(x)
    return x.decode(charset, errors)
