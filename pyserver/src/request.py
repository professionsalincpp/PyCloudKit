from __future__ import annotations
import asyncio
import inspect
from dataclasses import dataclass
from enum import Enum
from http.client import HTTPConnection, HTTPResponse
from http.server import BaseHTTPRequestHandler
from typing import Callable, Literal, Optional, Tuple, List, Dict

class AsyncRequest:

    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.client: Optional[HTTPConnection] = None

    async def _start(self) -> None:
        self.client = HTTPConnection(self.host, self.port)
        await asyncio.to_thread(self.client.connect)

    async def start(self) -> None:
        await asyncio.to_thread(self._start)

    async def stop(self) -> None:
        await asyncio.to_thread(self.client.close)

    async def get(self, path: str) -> bytes:
        await asyncio.to_thread(self.client.request, 'GET', path)
        return self.client.getresponse().read()

    async def post(self, path: str, data: bytes) -> bytes:
        await asyncio.to_thread(self.client.request, 'POST', path, body=data)
        return self.client.getresponse().read()
    
@dataclass
class Response:
    status_code: int
    headers: Dict[str, str]
    body: bytes
    def __str__(self) -> str:
        return f"Response(status_code={self.status_code}, headers={self.headers}, body={self.body})"

    def __repr__(self) -> str:
        return f"Response(status_code={self.status_code}, headers={self.headers}, body={self.body})"

@dataclass
class Request(Response):
    params: Dict[str, str]
    def __str__(self) -> str:
        return f"Request(status_code={self.status_code}, headers={self.headers}, body={self.body}, params={self.params})"

    def __repr__(self) -> str:
        return f"Request(status_code={self.status_code}, headers={self.headers}, body={self.body}, params={self.params})"

class RequestHandler:
    class Method(Enum):
        GET = 1
        POST = 2
    def __init__(self, func: Callable[[Request], Response], method: Method=Method.GET, path: str="/") -> None:
        self.func = func
        self.method = method
        self.path = path

    async def check_signature(self) -> None:
        if not inspect.iscoroutinefunction(self.func):
            raise ValueError("func must be a coroutine function")
        if len(inspect.signature(self.func).parameters) != 1 and len(inspect.signature(self.func).parameters) != 0:
            raise ValueError("func must have 1 or 0 parameters")
    
    async def handle(self, request: Request) -> Response:
        await self.check_signature()
        result = None
        func_params = inspect.signature(self.func).parameters
        if len(func_params) == 1:
            result = await self.func(request)
        elif len(func_params) == 0:
            result = await self.func()
        return result


def create_async_request_handler(handlers: List[RequestHandler]) -> type[create_async_request_handler.AsyncRequestHandler]:
    class AsyncRequestHandler(BaseHTTPRequestHandler):
        def __init__(self, request, client_address, server):
            """
            :param request: The request object
            :param client_address: The client address
            :param server: The server object
            """
            self.__init_handlers(handlers)  # Call the __init__ method of the current class
            super().__init__(request, client_address, server)

        def __init_handlers(self, handlers: List[RequestHandler]) -> None:
            self.handlers = handlers

        async def handle_get_request(self):
            # Обрабатываем запрос
            filename = self.path.rstrip('/')  # удалить "/" в конце
            params: Dict[str, str] = {}
            if '?' in filename:
                filename, params_str = filename.split('?')
                for param in params_str.split('&'):
                    key, value = param.split('=')
                    params[key] = value
            for handler in self.handlers:
                if handler.path == filename and handler.method == RequestHandler.Method.GET:
                    response: Response = await handler.handle(request=Request(status_code=200, headers=self.headers, body=b"", params=params))
                    response.headers["Connection"] = "close"
                    self.send_response(response.status_code)
                    for key, value in response.headers.items():
                        self.send_header(key, value)
                    self.end_headers()
                    if self.client_address:
                        print(f"Client connected from {self.client_address[0]}:{self.client_address[1]}")
                        if type(response.body) == str:
                            response.body = response.body.encode("utf-8")
                        try:
                            self.wfile.write(response.body)
                        except ConnectionAbortedError:
                            print("Client has closed the connection, skipping response")
                    return
            # Отправляем ответ неизвестного запроса
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.send_header("Content-Encoding", "utf-8")
            self.end_headers()
            self.wfile.write(f"Path: {filename} not found".encode("utf-8"))

        def do_GET(self):
            asyncio.run(self.handle_get_request())

        def do_POST(self):
            asyncio.run(self.handle_get_request())

    return AsyncRequestHandler
