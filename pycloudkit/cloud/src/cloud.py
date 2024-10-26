import sqlite3
from typing import Any
try:
    from pycloudkit.src.server import AsyncServer
    from pycloudkit.src.client import AsyncClient
    from pycloudkit.src.request import *
except ImportError:
    raise ImportError("PyCloudKit is not installed")
from .cloudtypes import *


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
        fetched = self.cursor.fetchone()
        if fetched is None:
            return "No such key"
        return from_string(fetched[0])

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
        self.handlers.append(RequestHandler(self.get_GET, HTTPMethod.GET, "/get"))
        self.handlers.append(RequestHandler(self.set_GET, HTTPMethod.GET, "/set"))
        self.handlers.append(RequestHandler(self.get_POST, HTTPMethod.POST, "/get"))
        self.handlers.append(RequestHandler(self.set_POST, HTTPMethod.POST, "/set"))
        self.handlers.append(RequestHandler(self.delete, HTTPMethod.GET, "/delete"))

    def start(self) -> None:
        super().start()
        
    async def get_GET(self, request: RequestType) -> ResponseType:
        if request.params.get("key") is None:
            return ResponseType(404, {}, "Bad request, please specify key")
        key = request.params["key"]
        return ResponseType(200, {}, body=str(self.database.get(key)).encode("utf-8"))

    async def set_GET(self, request: RequestType) -> ResponseType:
        if request.params.get("key") is None or request.params.get("value") is None:
            return ResponseType(404, {}, body="Bad request, please specify key and value")
        key = request.params["key"]
        value = request.params["value"]
        self.database.set(key, from_string(decode_string(value)))
        return ResponseType(200, {}, body="OK")
    
    async def get_POST(self, request: RequestType) -> ResponseType:
        body_dict = load_body_json(request.body)
        if body_dict.get("key") is None:
            return ResponseType(404, body="Bad request, please specify key")
        key = body_dict["key"]
        return ResponseType(200, {}, body=self.database.get(key).encode("utf-8"))

    async def set_POST(self, request: RequestType) -> ResponseType:
        body_dict = load_body_json(request.body)
        if body_dict.get("key") is None or body_dict.get("value") is None:
            return ResponseType(404, body="Bad request, please specify key and value")
        key = body_dict["key"]
        value = body_dict["value"]
        self.database.set(key, from_string(value))
        return ResponseType(200, {}, body="OK")

    async def delete(self, request: RequestType) -> ResponseType:
        if request.params.get("key") is None:
            return ResponseType(404, body="Bad request, please specify key")
        key = request.params["key"]
        self.database.delete(key)
        return ResponseType(200, {}, body="OK")

class CloudClient(AsyncClient):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)

    async def set(self, key: str, value: Any) -> None:
        obj = AnyCloudObject(value)
        print(f"Set {key} to {obj.to_string()}")
        body: str = make_json("{\"key\": \"$0\", \"value\": \"$1\"}", [key, obj.to_string()])
        print(f"Body: {body}")
        await super().post(f"/set", body.encode("utf-8"))

    async def get(self, key: str) -> Any:
        objstr = (await super().get(f"/get?key={key}")).decode("utf-8")
        print(f"Get {key} from {objstr}")
        obj = AnyCloudObject(from_string(decode_string(objstr)))
        return obj.value
    
    async def delete(self, key: str) -> None:
        await super().get(f"/delete?key={key}")
        