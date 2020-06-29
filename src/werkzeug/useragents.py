from __future__ import annotations
import re
from typing import Dict, Tuple, Union, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from werkzeug.wrappers.request import Request


class UserAgentParser:
    """A simple user agent parser.  Used by the `UserAgent`."""

    platforms: Any = (
        (" cros ", "chromeos"),
        ("iphone|ios", "iphone"),
        ("ipad", "ipad"),
        (r"darwin|mac|os\s*x", "macos"),
        ("win", "windows"),
        (r"android", "android"),
        ("netbsd", "netbsd"),
        ("openbsd", "openbsd"),
        ("freebsd", "freebsd"),
        ("dragonfly", "dragonflybsd"),
        ("(sun|i86)os", "solaris"),
        (r"x11|lin(\b|ux)?", "linux"),
        (r"nintendo\s+wii", "wii"),
        ("irix", "irix"),
        ("hp-?ux", "hpux"),
        ("aix", "aix"),
        ("sco|unix_sv", "sco"),
        ("bsd", "bsd"),
        ("amiga", "amiga"),
        ("blackberry|playbook", "blackberry"),
        ("symbian", "symbian"),
    )
    browsers: Any = (
        ("googlebot", "google"),
        ("msnbot", "msn"),
        ("yahoo", "yahoo"),
        ("ask jeeves", "ask"),
        (r"aol|america\s+online\s+browser", "aol"),
        (r"opera|opr", "opera"),
        ("edge|edg", "edge"),
        ("chrome|crios", "chrome"),
        ("seamonkey", "seamonkey"),
        ("firefox|firebird|phoenix|iceweasel", "firefox"),
        ("galeon", "galeon"),
        ("safari|version", "safari"),
        ("webkit", "webkit"),
        ("camino", "camino"),
        ("konqueror", "konqueror"),
        ("k-meleon", "kmeleon"),
        ("netscape", "netscape"),
        (r"msie|microsoft\s+internet\s+explorer|trident/.+? rv:", "msie"),
        ("lynx", "lynx"),
        ("links", "links"),
        ("Baiduspider", "baidu"),
        ("bingbot", "bing"),
        ("mozilla", "mozilla"),
    )

    _browser_version_re = r"(?:{pattern})[/\sa-z(]*(\d+[.\da-z]+)?"
    _language_re = re.compile(
        r"(?:;\s*|\s+)(\b\w{2}\b(?:-\b\w{2}\b)?)\s*;|"
        r"(?:\(|\[|;)\s*(\b\w{2}\b(?:-\b\w{2}\b)?)\s*(?:\]|\)|;)"
    )

    def __init__(self) -> None:
        self.platforms = [(b, re.compile(a, re.I)) for a, b in self.platforms]
        self.browsers = [
            (b, re.compile(self._browser_version_re.format(pattern=a), re.I))
            for a, b in self.browsers
        ]

    def __call__(
        self, user_agent: str
    ) -> Union[
        Tuple[str, str, str, str],
        Tuple[None, str, str, None],
        Tuple[None, None, None, None],
        Tuple[str, str, str, None],
    ]:
        for platform, regex in self.platforms:  # noqa: B007
            match = regex.search(user_agent)
            if match is not None:
                break
        else:
            platform = None
        for browser, regex in self.browsers:  # noqa: B007
            match = regex.search(user_agent)
            if match is not None:
                version = match.group(1)
                break
        else:
            browser = version = None
        match = self._language_re.search(user_agent)
        if match is not None:
            language = match.group(1) or match.group(2)
        else:
            language = None
        return platform, browser, version, language


class UserAgent:
    """Represents a user agent.  Pass it a WSGI environment or a user agent
    string and you can inspect some of the details from the user agent
    string via the attributes.  The following attributes exist:

    .. attribute:: string

       the raw user agent string

    .. attribute:: platform

       the browser platform. ``None`` if not recognized.
       The following platforms are currently recognized:

       -   `aix`
       -   `amiga`
       -   `android`
       -   `blackberry`
       -   `bsd`
       -   `chromeos`
       -   `dragonflybsd`
       -   `freebsd`
       -   `hpux`
       -   `ipad`
       -   `iphone`
       -   `irix`
       -   `linux`
       -   `macos`
       -   `netbsd`
       -   `openbsd`
       -   `sco`
       -   `solaris`
       -   `symbian`
       -   `wii`
       -   `windows`

    .. attribute:: browser

        the name of the browser. ``None`` if not recognized.
        The following browsers are currently recognized:

        -   `aol` *
        -   `ask` *
        -   `baidu` *
        -   `bing` *
        -   `camino`
        -   `chrome`
        -   `edge`
        -   `firefox`
        -   `galeon`
        -   `google` *
        -   `kmeleon`
        -   `konqueror`
        -   `links`
        -   `lynx`
        -   `mozilla`
        -   `msie`
        -   `msn`
        -   `netscape`
        -   `opera`
        -   `safari`
        -   `seamonkey`
        -   `webkit`
        -   `yahoo` *

        (Browsers marked with a star (``*``) are crawlers.)

    .. attribute:: version

        the version of the browser. ``None`` if not recognized.

    .. attribute:: language

        the language of the browser. ``None`` if not recognized.
    """

    string: Any
    _parser = UserAgentParser()

    def __init__(self, environ_or_string: Dict[str, Union[str, Request]]) -> None:
        if isinstance(environ_or_string, dict):
            environ_or_string = environ_or_string.get("HTTP_USER_AGENT", "")
        self.string = environ_or_string
        self.platform, self.browser, self.version, self.language = self._parser(
            environ_or_string
        )

    def to_header(self) -> str:
        return self.string

    def __str__(self) -> str:
        return self.string

    def __nonzero__(self) -> bool:
        return bool(self.browser)

    __bool__: Any = __nonzero__

    def __repr__(self):
        return f"<{type(self).__name__} {self.browser!r}/{self.version}>"
