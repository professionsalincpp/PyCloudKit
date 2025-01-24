import asyncio
import http.server
from http import HTTPMethod
from typing import Callable, List, Literal, Optional
from .request import create_async_request_handler, RequestHandler

class AsyncServer:
    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.server: Optional[http.server.HTTPServer] = None
        self.task: Optional[asyncio.Task] = None
        self.handlers: List[RequestHandler] = []
        self.__post_init__()
        print(f'Start server on http://{self.host}:{self.port}')

    def __post_init__(self):
        pass

    def route(self, path: str, method: Literal[HTTPMethod.GET, HTTPMethod.POST] = HTTPMethod.GET) -> None:
        def decorator(func: Callable[[RequestHandler], RequestHandler]) -> Callable[[RequestHandler], RequestHandler]:
            handler = RequestHandler(func, method, path)
            self.handlers.append(handler)
            return func
        return decorator
    
    def routedefault(self, func: Callable[[RequestHandler], RequestHandler]) -> Callable[[RequestHandler], RequestHandler]:
        def decorator(func: Callable[[RequestHandler], RequestHandler]) -> Callable[[RequestHandler], RequestHandler]:
            handler = RequestHandler(func, path='any')
            self.handlers.append(handler)
            return func
        return decorator

    def start(self) -> None:
        self.server = http.server.HTTPServer((self.host, self.port), create_async_request_handler(self.handlers))
        self.server.serve_forever()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()

