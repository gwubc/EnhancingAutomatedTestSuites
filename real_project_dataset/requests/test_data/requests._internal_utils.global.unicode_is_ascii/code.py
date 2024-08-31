"""
requests._internal_utils
~~~~~~~~~~~~~~

Provides utility functions that are consumed internally by Requests
which depend on extremely few external helpers (such as compat)
"""

import re
from .compat import builtin_str

_VALID_HEADER_NAME_RE_BYTE = re.compile(b"^[^:\\s][^:\\r\\n]*$")
_VALID_HEADER_NAME_RE_STR = re.compile("^[^:\\s][^:\\r\\n]*$")
_VALID_HEADER_VALUE_RE_BYTE = re.compile(b"^\\S[^\\r\\n]*$|^$")
_VALID_HEADER_VALUE_RE_STR = re.compile("^\\S[^\\r\\n]*$|^$")
_HEADER_VALIDATORS_STR = _VALID_HEADER_NAME_RE_STR, _VALID_HEADER_VALUE_RE_STR
_HEADER_VALIDATORS_BYTE = (_VALID_HEADER_NAME_RE_BYTE, _VALID_HEADER_VALUE_RE_BYTE)
HEADER_VALIDATORS = {bytes: _HEADER_VALIDATORS_BYTE, str: _HEADER_VALIDATORS_STR}


def to_native_string(string, encoding="ascii"):
    if isinstance(string, builtin_str):
        out = string
    else:
        out = string.decode(encoding)
    return out


def unicode_is_ascii(u_string):
    assert isinstance(u_string, str)
    try:
        u_string.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False