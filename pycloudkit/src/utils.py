from typing import Dict, List, Optional, Tuple

def encode_uri_params(value: str) -> str:
    return value.replace('"', "%22").replace("'", "%27").replace(' ', "%20").replace("[", "%5B").replace("]", "%5D").replace(",", "%2C").replace("+", "%2B").replace(":", "%3A").replace(";","%3B").replace("@","%40").replace("$","%24").replace("{","%7B").replace("}","%7D")

def decode_uri_params(value: str) -> str:
    return value.replace("%22", '"').replace("%27", "'").replace("%20", " ").replace("%5B", "[").replace("%5D", "]").replace("%2C", ",").replace("%3D", "=").replace("%2B", "+").replace("%3A", ":").replace("%3B", ";").replace("%40", "@").replace("%24", "$").replace("%7B", "{").replace("%7D", "}")

def parse_path(path: str) -> Tuple[str, Dict[str, str]]:
    filename = path
    params: Dict[str, str] = {}
    if '?' in filename:
        filename, params_str = filename.split('?')
        params = parse_query_string(params_str)
    return filename, params

def to_bytes(value: str | bytes) -> bytes:
    if isinstance(value, str):
        return value.encode("utf-8")
    return value

def parse_query_string(query_string: str) -> Dict[str, str]:
    params: Dict[str, str] = {}
    for param in query_string.split('&'):
        key, value = param.split('=')
        params[key] = value
    return params

def make_json(src: str, params: Optional[List[str]] = None) -> str:
    if params is None:
        return src
    if src.count("$") != len(params):
        raise Exception("Incorrect number of params")
    for i in range(len(params)):
        src = src.replace(f"${i}", params[i])
    return src