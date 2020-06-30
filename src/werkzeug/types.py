"""
Custom types which Werkzeug uses. These provide for better editor tooling and streamline internal
development.
"""
from typing import Union

BytesOrStr = Union[bytes, str]
