def encode_uri_params(value: str) -> str:
    return value.replace('"', "%22").replace("'", "%27").replace(' ', "%20").replace("[", "%5B").replace("]", "%5D").replace(",", "%2C").replace("+", "%2B").replace(":", "%3A").replace(";","%3B").replace("@","%40").replace("$","%24").replace("{","%7B").replace("}","%7D")
