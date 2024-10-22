import sqlite3
from typing import Union, Any, override, overload
from ..src.server import AsyncServer
from ..src.client import AsyncClient
from ..src.request import *

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

class CloudObject:
    def __init__(self, value: Any) -> None:
        self.value = value

    def to_string(self) -> str:
        raise NotImplementedError

    def from_string(self, value: str) -> None:
        raise NotImplementedError


class PyCloudObject(CloudObject):
    def __init__(self, value: Any) -> None:
        self.value = value

    def to_string(self) -> str:
        if isinstance(self.value, str):
            return f'"{self.value}"'
        return str(self.value)
    
    def from_string(self, value: str) -> None:
        self.value = eval(value)

    def __repr__(self) -> str:
        return self.to_string()

class ClassCloudObject(CloudObject):
    def __init__(self, value: object) -> None:
        super().__init__(value)
        
    def to_string(self) -> str:
        _class = self.value.__class__
        _dict = _class.__dict__
        return f"{_class.__name__}({_dict})"

    def from_string(self, value: str) -> None:
        _classstr = value.split('(')[0]
        _dictstr = value.split('(')[1].rstrip(')')
        _class = eval(f"{_classstr}")
        _dict = eval(f"{_dictstr}")
        self.value = _class(**_dict)
        _class.__dict__ = _dict

    def __repr__(self) -> str:
        return self.to_string()
    

class AnyCloudObject(CloudObject):
    def __init__(self, value: Any) -> None:
        super().__init__(value)

    def to_string(self) -> str:
        if is_py_object(self.value):
            return PyCloudObject(self.value).to_string()
        elif is_class_object(self.value):
            return ClassCloudObject(self.value).to_string()
        raise NotImplementedError

    def from_string(self, value: str) -> None:
        self.value = eval(value)


class CloudDatabase:
    def __init__(self, path: str) -> None:
        self.path: str = path
        self.data: dict[str, AnyCloudObject] = {}
        self.database = sqlite3.connect(self.path)
        self.cursor = self.database.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS objects (key TEXT PRIMARY KEY, value TEXT)")
        self.database.commit()

    def load(self) -> None:
        self.cursor.execute("SELECT key, value FROM objects")
        for key, value in self.cursor.fetchall():
            self.data[key] = AnyCloudObject(from_string(value))

    def get(self, key: str) -> str:
        self.cursor.execute("SELECT value FROM objects WHERE key = ?", (key,))
        return from_string(self.cursor.fetchone()[0])

    def set(self, key: str, value: Any) -> None:
        self.data[key] = AnyCloudObject(value)
        self.cursor.execute("INSERT OR REPLACE INTO objects VALUES (?, ?)", (key, self.data[key].to_string()))
        self.database.commit()

    def exists(self, key: str) -> bool:
        return key in self.data

    def delete(self, key: str) -> None:
        del self.data[key]
        self.cursor.execute("DELETE FROM objects WHERE key = ?", (key,))
        self.database.commit()

    def clear(self) -> None:
        self.data.clear()
        self.cursor.execute("DELETE FROM objects")
        self.database.commit()

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        self.delete(key)


class CloudServer(AsyncServer):
    def __init__(self, host: str, port: int, database_path: str) -> None:
        super().__init__(host, port)
        self.database = CloudDatabase(database_path)
        self.database.load()
        self.handlers.append(RequestHandler(self.get, RequestHandler.Method.GET, "/get"))
        self.handlers.append(RequestHandler(self.set, RequestHandler.Method.GET, "/set"))
        self.handlers.append(RequestHandler(self.delete, RequestHandler.Method.GET, "/delete"))

    def start(self) -> None:
        super().start()
        
    async def get(self, request: Request) -> Response:
        if request.params.get("key") is None:
            return Response(404, {}, "Bad request, please specify key")
        key = request.params["key"]
        return Response(200, {}, body=str(self.database.get(key)).encode("utf-8"))

    async def set(self, request: Request) -> Response:
        if request.params.get("key") is None or request.params.get("value") is None:
            return Response(404, {}, body="Bad request, please specify key and value")
        key = request.params["key"]
        value = request.params["value"]
        self.database.set(key, from_string(decode_string(value)))
        return Response(200, {}, body="OK")

    async def delete(self, request: Request) -> Response:
        if request.params.get("key") is None:
            return Response(404, body="Bad request, please specify key")
        key = request.params["key"]
        self.database.delete(key)
        return Response(200, body="OK")

class CloudClient(AsyncClient):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)

    async def set(self, key: str, value: Any) -> None:
        obj = AnyCloudObject(value)
        print(f"Set {key} to {obj.to_string()}")
        await super().get(f"/set?key={key}&value={obj.to_string()}")

    async def get(self, key: str) -> Any:
        objstr = (await super().get(f"/get?key={key}")).decode("utf-8")
        print(f"Get {key} from {objstr}")
        obj = AnyCloudObject(from_string(decode_string(objstr)))
        return obj.value
    
    async def delete(self, key: str) -> None:
        await super().get(f"/delete?key={key}")
        