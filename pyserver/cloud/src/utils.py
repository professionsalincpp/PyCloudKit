from typing import Any, Union

py_object_union = Union[str, int, float, bool, list, dict, bytes, bytearray, tuple, None] 

def is_py_object(value: Any) -> bool:
    return isinstance(value, py_object_union)

def is_class_object(value: Any) -> bool:
    return isinstance(value, object) and not is_py_object(value)

def decode_string(value: str) -> str:
    return value.replace("%22", '"').replace("%27", "'").replace("%20", " ").replace("%5B", "[").replace("%5D", "]").replace("%2C", ",").replace("%3D", "=").replace("%2B", "+").replace("%3A", ":").replace("%3B", ";").replace("%40", "@").replace("%24", "$").replace("%7B", "{").replace("%7D", "}")

def encode_string(value: str) -> str:
    return value.replace('"', "%22").replace("'", "%27").replace(' ', "%20").replace("[", "%5B").replace("]", "%5D").replace(",", "%2C").replace("=", "%3D").replace("+", "%2B").replace(":", "%3A").replace(";","%3B").replace("@","%40").replace("$","%24").replace("{","%7B").replace("}","%7D")

def from_string(value: str) -> Any:
    try:
        return eval(value)
    except:
        return value