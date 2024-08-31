"""
requests.utils
~~~~~~~~~~~~~~

This module provides utility functions that are used within Requests
that are also useful for external consumption.
"""

import codecs
import contextlib
import io
import os
import re
import socket
import struct
import sys
import tempfile
import warnings
import zipfile
from collections import OrderedDict
from urllib3.util import make_headers, parse_url
from . import certs
from .__version__ import __version__
from ._internal_utils import (
    _HEADER_VALIDATORS_BYTE,
    _HEADER_VALIDATORS_STR,
    HEADER_VALIDATORS,
    to_native_string,
)
from .compat import (
    Mapping,
    basestring,
    bytes,
    getproxies,
    getproxies_environment,
    integer_types,
)
from .compat import parse_http_list as _parse_list_header
from .compat import (
    proxy_bypass,
    proxy_bypass_environment,
    quote,
    str,
    unquote,
    urlparse,
    urlunparse,
)
from .cookies import cookiejar_from_dict
from .exceptions import (
    FileModeWarning,
    InvalidHeader,
    InvalidURL,
    UnrewindableBodyError,
)
from .structures import CaseInsensitiveDict

NETRC_FILES = ".netrc", "_netrc"
DEFAULT_CA_BUNDLE_PATH = certs.where()
DEFAULT_PORTS = {"http": 80, "https": 443}
DEFAULT_ACCEPT_ENCODING = ", ".join(
    re.split(",\\s*", make_headers(accept_encoding=True)["accept-encoding"])
)
if sys.platform == "win32":

    def proxy_bypass_registry(host):
        try:
            import winreg
        except ImportError:
            return False
        try:
            internetSettings = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings",
            )
            proxyEnable = int(winreg.QueryValueEx(internetSettings, "ProxyEnable")[0])
            proxyOverride = winreg.QueryValueEx(internetSettings, "ProxyOverride")[0]
        except (OSError, ValueError):
            return False
        if not proxyEnable or not proxyOverride:
            return False
        proxyOverride = proxyOverride.split(";")
        proxyOverride = filter(None, proxyOverride)
        for test in proxyOverride:
            if test == "<local>":
                if "." not in host:
                    return True
            test = test.replace(".", "\\.")
            test = test.replace("*", ".*")
            test = test.replace("?", ".")
            if re.match(test, host, re.I):
                return True
        return False

    def proxy_bypass(host):
        if getproxies_environment():
            return proxy_bypass_environment(host)
        else:
            return proxy_bypass_registry(host)


def dict_to_sequence(d):
    if hasattr(d, "items"):
        d = d.items()
    return d


def super_len(o):
    total_length = None
    current_position = 0
    if isinstance(o, str):
        o = o.encode("utf-8")
    if hasattr(o, "__len__"):
        total_length = len(o)
    elif hasattr(o, "len"):
        total_length = o.len
    elif hasattr(o, "fileno"):
        try:
            fileno = o.fileno()
        except (io.UnsupportedOperation, AttributeError):
            pass
        else:
            total_length = os.fstat(fileno).st_size
            if "b" not in o.mode:
                warnings.warn(
                    "Requests has determined the content-length for this request using the binary size of the file: however, the file has been opened in text mode (i.e. without the 'b' flag in the mode). This may lead to an incorrect content-length. In Requests 3.0, support will be removed for files in text mode.",
                    FileModeWarning,
                )
    if hasattr(o, "tell"):
        try:
            current_position = o.tell()
        except OSError:
            if total_length is not None:
                current_position = total_length
        else:
            if hasattr(o, "seek") and total_length is None:
                try:
                    o.seek(0, 2)
                    total_length = o.tell()
                    o.seek(current_position or 0)
                except OSError:
                    total_length = 0
    if total_length is None:
        total_length = 0
    return max(0, total_length - current_position)


def get_netrc_auth(url, raise_errors=False):
    netrc_file = os.environ.get("NETRC")
    if netrc_file is not None:
        netrc_locations = (netrc_file,)
    else:
        netrc_locations = (f"~/{f}" for f in NETRC_FILES)
    try:
        from netrc import NetrcParseError, netrc

        netrc_path = None
        for f in netrc_locations:
            try:
                loc = os.path.expanduser(f)
            except KeyError:
                return
            if os.path.exists(loc):
                netrc_path = loc
                break
        if netrc_path is None:
            return
        ri = urlparse(url)
        splitstr = b":"
        if isinstance(url, str):
            splitstr = splitstr.decode("ascii")
        host = ri.netloc.split(splitstr)[0]
        try:
            _netrc = netrc(netrc_path).authenticators(host)
            if _netrc:
                login_i = 0 if _netrc[0] else 1
                return _netrc[login_i], _netrc[2]
        except (NetrcParseError, OSError):
            if raise_errors:
                raise
    except (ImportError, AttributeError):
        pass


def guess_filename(obj):
    name = getattr(obj, "name", None)
    if name and isinstance(name, basestring) and name[0] != "<" and name[-1] != ">":
        return os.path.basename(name)


def extract_zipped_paths(path):
    if os.path.exists(path):
        return path
    archive, member = os.path.split(path)
    while archive and not os.path.exists(archive):
        archive, prefix = os.path.split(archive)
        if not prefix:
            break
        member = "/".join([prefix, member])
    if not zipfile.is_zipfile(archive):
        return path
    zip_file = zipfile.ZipFile(archive)
    if member not in zip_file.namelist():
        return path
    tmp = tempfile.gettempdir()
    extracted_path = os.path.join(tmp, member.split("/")[-1])
    if not os.path.exists(extracted_path):
        with atomic_open(extracted_path) as file_handler:
            file_handler.write(zip_file.read(member))
    return extracted_path


@contextlib.contextmanager
def atomic_open(filename):
    tmp_descriptor, tmp_name = tempfile.mkstemp(dir=os.path.dirname(filename))
    try:
        with os.fdopen(tmp_descriptor, "wb") as tmp_handler:
            yield tmp_handler
        os.replace(tmp_name, filename)
    except BaseException:
        os.remove(tmp_name)
        raise


def from_key_val_list(value):
    if value is None:
        return None
    if isinstance(value, (str, bytes, bool, int)):
        raise ValueError("cannot encode objects that are not 2-tuples")
    return OrderedDict(value)


def to_key_val_list(value):
    if value is None:
        return None
    if isinstance(value, (str, bytes, bool, int)):
        raise ValueError("cannot encode objects that are not 2-tuples")
    if isinstance(value, Mapping):
        value = value.items()
    return list(value)


def parse_list_header(value):
    result = []
    for item in _parse_list_header(value):
        if item[:1] == item[-1:] == '"':
            item = unquote_header_value(item[1:-1])
        result.append(item)
    return result


def parse_dict_header(value):
    result = {}
    for item in _parse_list_header(value):
        if "=" not in item:
            result[item] = None
            continue
        name, value = item.split("=", 1)
        if value[:1] == value[-1:] == '"':
            value = unquote_header_value(value[1:-1])
        result[name] = value
    return result


def unquote_header_value(value, is_filename=False):
    if value and value[0] == value[-1] == '"':
        value = value[1:-1]
        if not is_filename or value[:2] != "\\\\":
            return value.replace("\\\\", "\\").replace('\\"', '"')
    return value


def dict_from_cookiejar(cj):
    cookie_dict = {cookie.name: cookie.value for cookie in cj}
    return cookie_dict


def add_dict_to_cookiejar(cj, cookie_dict):
    return cookiejar_from_dict(cookie_dict, cj)


def get_encodings_from_content(content):
    warnings.warn(
        "In requests 3.0, get_encodings_from_content will be removed. For more information, please see the discussion on issue #2266. (This warning should only appear once.)",
        DeprecationWarning,
    )
    charset_re = re.compile("<meta.*?charset=[\"\\']*(.+?)[\"\\'>]", flags=re.I)
    pragma_re = re.compile(
        "<meta.*?content=[\"\\']*;?charset=(.+?)[\"\\'>]", flags=re.I
    )
    xml_re = re.compile("^<\\?xml.*?encoding=[\"\\']*(.+?)[\"\\'>]")
    return (
        charset_re.findall(content)
        + pragma_re.findall(content)
        + xml_re.findall(content)
    )


def _parse_content_type_header(header):
    tokens = header.split(";")
    content_type, params = tokens[0].strip(), tokens[1:]
    params_dict = {}
    items_to_strip = "\"' "
    for param in params:
        param = param.strip()
        if param:
            key, value = param, True
            index_of_equals = param.find("=")
            if index_of_equals != -1:
                key = param[:index_of_equals].strip(items_to_strip)
                value = param[index_of_equals + 1 :].strip(items_to_strip)
            params_dict[key.lower()] = value
    return content_type, params_dict


def get_encoding_from_headers(headers):
    content_type = headers.get("content-type")
    if not content_type:
        return None
    content_type, params = _parse_content_type_header(content_type)
    if "charset" in params:
        return params["charset"].strip("'\"")
    if "text" in content_type:
        return "ISO-8859-1"
    if "application/json" in content_type:
        return "utf-8"


def stream_decode_response_unicode(iterator, r):
    if r.encoding is None:
        yield from iterator
        return
    decoder = codecs.getincrementaldecoder(r.encoding)(errors="replace")
    for chunk in iterator:
        rv = decoder.decode(chunk)
        if rv:
            yield rv
    rv = decoder.decode(b"", final=True)
    if rv:
        yield rv


def iter_slices(string, slice_length):
    pos = 0
    if slice_length is None or slice_length <= 0:
        slice_length = len(string)
    while pos < len(string):
        yield string[pos : pos + slice_length]
        pos += slice_length


def get_unicode_from_response(r):
    warnings.warn(
        "In requests 3.0, get_unicode_from_response will be removed. For more information, please see the discussion on issue #2266. (This warning should only appear once.)",
        DeprecationWarning,
    )
    tried_encodings = []
    encoding = get_encoding_from_headers(r.headers)
    if encoding:
        try:
            return str(r.content, encoding)
        except UnicodeError:
            tried_encodings.append(encoding)
    try:
        return str(r.content, encoding, errors="replace")
    except TypeError:
        return r.content


UNRESERVED_SET = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "0123456789-._~"
)


def unquote_unreserved(uri):
    parts = uri.split("%")
    for i in range(1, len(parts)):
        h = parts[i][0:2]
        if len(h) == 2 and h.isalnum():
            try:
                c = chr(int(h, 16))
            except ValueError:
                raise InvalidURL(f"Invalid percent-escape sequence: '{h}'")
            if c in UNRESERVED_SET:
                parts[i] = c + parts[i][2:]
            else:
                parts[i] = f"%{parts[i]}"
        else:
            parts[i] = f"%{parts[i]}"
    return "".join(parts)


def requote_uri(uri):
    safe_with_percent = "!#$%&'()*+,/:;=?@[]~"
    safe_without_percent = "!#$&'()*+,/:;=?@[]~"
    try:
        return quote(unquote_unreserved(uri), safe=safe_with_percent)
    except InvalidURL:
        return quote(uri, safe=safe_without_percent)


def address_in_network(ip, net):
    ipaddr = struct.unpack("=L", socket.inet_aton(ip))[0]
    netaddr, bits = net.split("/")
    netmask = struct.unpack("=L", socket.inet_aton(dotted_netmask(int(bits))))[0]
    network = struct.unpack("=L", socket.inet_aton(netaddr))[0] & netmask
    return ipaddr & netmask == network & netmask


def dotted_netmask(mask):
    bits = 4294967295 ^ (1 << 32 - mask) - 1
    return socket.inet_ntoa(struct.pack(">I", bits))


def is_ipv4_address(string_ip):
    try:
        socket.inet_aton(string_ip)
    except OSError:
        return False
    return True


def is_valid_cidr(string_network):
    if string_network.count("/") == 1:
        try:
            mask = int(string_network.split("/")[1])
        except ValueError:
            return False
        if mask < 1 or mask > 32:
            return False
        try:
            socket.inet_aton(string_network.split("/")[0])
        except OSError:
            return False
    else:
        return False
    return True


@contextlib.contextmanager
def set_environ(env_name, value):
    value_changed = value is not None
    if value_changed:
        old_value = os.environ.get(env_name)
        os.environ[env_name] = value
    try:
        yield
    finally:
        if value_changed:
            if old_value is None:
                del os.environ[env_name]
            else:
                os.environ[env_name] = old_value


def should_bypass_proxies(url, no_proxy):

    def get_proxy(key):
        return os.environ.get(key) or os.environ.get(key.upper())

    no_proxy_arg = no_proxy
    if no_proxy is None:
        no_proxy = get_proxy("no_proxy")
    parsed = urlparse(url)
    if parsed.hostname is None:
        return True
    if no_proxy:
        no_proxy = (host for host in no_proxy.replace(" ", "").split(",") if host)
        if is_ipv4_address(parsed.hostname):
            for proxy_ip in no_proxy:
                if is_valid_cidr(proxy_ip):
                    if address_in_network(parsed.hostname, proxy_ip):
                        return True
                elif parsed.hostname == proxy_ip:
                    return True
        else:
            host_with_port = parsed.hostname
            if parsed.port:
                host_with_port += f":{parsed.port}"
            for host in no_proxy:
                if parsed.hostname.endswith(host) or host_with_port.endswith(host):
                    return True
    with set_environ("no_proxy", no_proxy_arg):
        try:
            bypass = proxy_bypass(parsed.hostname)
        except (TypeError, socket.gaierror):
            bypass = False
    if bypass:
        return True
    return False


def get_environ_proxies(url, no_proxy=None):
    if should_bypass_proxies(url, no_proxy=no_proxy):
        return {}
    else:
        return getproxies()


def select_proxy(url, proxies):
    proxies = proxies or {}
    urlparts = urlparse(url)
    if urlparts.hostname is None:
        return proxies.get(urlparts.scheme, proxies.get("all"))
    proxy_keys = [
        urlparts.scheme + "://" + urlparts.hostname,
        urlparts.scheme,
        "all://" + urlparts.hostname,
        "all",
    ]
    proxy = None
    for proxy_key in proxy_keys:
        if proxy_key in proxies:
            proxy = proxies[proxy_key]
            break
    return proxy


def resolve_proxies(request, proxies, trust_env=True):
    proxies = proxies if proxies is not None else {}
    url = request.url
    scheme = urlparse(url).scheme
    no_proxy = proxies.get("no_proxy")
    new_proxies = proxies.copy()
    if trust_env and not should_bypass_proxies(url, no_proxy=no_proxy):
        environ_proxies = get_environ_proxies(url, no_proxy=no_proxy)
        proxy = environ_proxies.get(scheme, environ_proxies.get("all"))
        if proxy:
            new_proxies.setdefault(scheme, proxy)
    return new_proxies


def default_user_agent(name="python-requests"):
    return f"{name}/{__version__}"


def default_headers():
    return CaseInsensitiveDict(
        {
            "User-Agent": default_user_agent(),
            "Accept-Encoding": DEFAULT_ACCEPT_ENCODING,
            "Accept": "*/*",
            "Connection": "keep-alive",
        }
    )


def parse_header_links(value):
    links = []
    replace_chars = " '\""
    value = value.strip(replace_chars)
    if not value:
        return links
    for val in re.split(", *<", value):
        try:
            url, params = val.split(";", 1)
        except ValueError:
            url, params = val, ""
        link = {"url": url.strip("<> '\"")}
        for param in params.split(";"):
            try:
                key, value = param.split("=")
            except ValueError:
                break
            link[key.strip(replace_chars)] = value.strip(replace_chars)
        links.append(link)
    return links


_null = "\x00".encode("ascii")
_null2 = _null * 2
_null3 = _null * 3


def guess_json_utf(data):
    sample = data[:4]
    if sample in (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE):
        return "utf-32"
    if sample[:3] == codecs.BOM_UTF8:
        return "utf-8-sig"
    if sample[:2] in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE):
        return "utf-16"
    nullcount = sample.count(_null)
    if nullcount == 0:
        return "utf-8"
    if nullcount == 2:
        if sample[::2] == _null2:
            return "utf-16-be"
        if sample[1::2] == _null2:
            return "utf-16-le"
    if nullcount == 3:
        if sample[:3] == _null3:
            return "utf-32-be"
        if sample[1:] == _null3:
            return "utf-32-le"
    return None


def prepend_scheme_if_needed(url, new_scheme):
    parsed = parse_url(url)
    scheme, auth, host, port, path, query, fragment = parsed
    netloc = parsed.netloc
    if not netloc:
        netloc, path = path, netloc
    if auth:
        netloc = "@".join([auth, netloc])
    if scheme is None:
        scheme = new_scheme
    if path is None:
        path = ""
    return urlunparse((scheme, netloc, path, "", query, fragment))


def get_auth_from_url(url):
    parsed = urlparse(url)
    try:
        auth = unquote(parsed.username), unquote(parsed.password)
    except (AttributeError, TypeError):
        auth = "", ""
    return auth


def check_header_validity(header):
    name, value = header
    _validate_header_part(header, name, 0)
    _validate_header_part(header, value, 1)


def _validate_header_part(header, header_part, header_validator_index):
    if isinstance(header_part, str):
        validator = _HEADER_VALIDATORS_STR[header_validator_index]
    elif isinstance(header_part, bytes):
        validator = _HEADER_VALIDATORS_BYTE[header_validator_index]
    else:
        raise InvalidHeader(
            f"Header part ({header_part!r}) from {header} must be of type str or bytes, not {type(header_part)}"
        )
    if not validator.match(header_part):
        header_kind = "name" if header_validator_index == 0 else "value"
        raise InvalidHeader(
            f"Invalid leading whitespace, reserved character(s), or return character(s) in header {header_kind}: {header_part!r}"
        )


def urldefragauth(url):
    scheme, netloc, path, params, query, fragment = urlparse(url)
    if not netloc:
        netloc, path = path, netloc
    netloc = netloc.rsplit("@", 1)[-1]
    return urlunparse((scheme, netloc, path, params, query, ""))


def rewind_body(prepared_request):
    body_seek = getattr(prepared_request.body, "seek", None)
    if body_seek is not None and isinstance(
        prepared_request._body_position, integer_types
    ):
        try:
            body_seek(prepared_request._body_position)
        except OSError:
            raise UnrewindableBodyError(
                "An error occurred when rewinding request body for redirect."
            )
    else:
        raise UnrewindableBodyError("Unable to rewind request body for redirect.")