"""
Custom types which Werkzeug uses. These provide for better editor tooling and streamline internal
development.
"""
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import Union

if TYPE_CHECKING:
    from .datastructures import Headers

BytesOrStr = Union[bytes, str]
# A value which can be encoded using Unicode.
UnicodeEncodable = Union[bytes, str, int]

# a generic type parameter used in many functions
T = TypeVar("T")
# a number (either floating point or an integer)
Number = TypeVar("Number", int, float)

# A WSGI environment
WSGIEnvironment = Dict[str, Any]

AnyHeaders = TypeVar("AnyHeaders", List[Tuple[str, str]], Headers)
