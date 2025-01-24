from __future__ import annotations
import asyncio
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler
from typing import Self, Optional, List, Dict
from .types import *
from .utils import *

class AsyncRequest:

    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.client: Optional[HTTPConnection] = None

    async def _start(self) -> None:
        self.client = HTTPConnection(self.host, self.port)
        # print(f"Client connected {self.client}")
        await asyncio.to_thread(self.client.connect)

    async def start(self) -> None:
        await self._start()

    async def get(self, path: str) -> bytes:
        await asyncio.to_thread(self.client.request, 'GET', encode_uri_params(path))
        return self.client.getresponse().read()

    async def post(self, path: str, data: bytes) -> bytes:
        await asyncio.to_thread(self.client.request, 'POST', path, body=data)
        return self.client.getresponse().read()
    
    async def close(self) -> None:
        await asyncio.to_thread(self.client.close)

    def __enter__(self) -> Self:
        asyncio.run(self._start())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        asyncio.run(self.close())

    async def __aenter__(self) -> Self:
        await self._start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


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

        def handle_default_request(self):
            filename, _ = parse_path(path=self.path)
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.send_header("Content-Encoding", "utf-8")
            self.end_headers()
            self.wfile.write(f"Path: {filename} not found".encode("utf-8"))

        def get_handler(self, path: str, method: HTTPMethod) -> Optional[RequestHandler]:
            _any_handler = None
            for handler in self.handlers:
                if handler.path == path and handler.method == method:
                    return handler
                elif handler.path == 'any' and handler.method == method:
                    _any_handler = handler
            return _any_handler
        
        def send_headers(self, headers: Dict[str, str]) -> None:
            """
            Send the provided headers in the HTTP response.
            Parameters:
                headers (Dict[str, str]): A dictionary containing the headers to be sent.
            """
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()

        def send_body(self, body: bytes) -> None:
            """
            Send the provided body in the HTTP response.
            Parameters:
                body (bytes): The body to be sent.
            """
            try:
                self.wfile.write(body)
            except ConnectionAbortedError:
                print("Client has closed the connection, skipping response")

        async def process_request(self, handler: RequestHandler, request: RequestType) -> None:
            response: ResponseType = await handler.handle(request=RequestType(status_code=200, headers=self.headers, body=request.body, params=request.params, path=request.path))
            response.headers["Connection"] = "close"
            self.send_response(response.status_code)
            self.send_headers(response.headers)
            self.send_body(to_bytes(response.body))

        async def handle_request(self, method: HTTPMethod) -> None:
            """
            Handle an HTTP request.
            """
            # Обрабатываем запрос
            filename, params = parse_path(path=decode_uri_params(self.path))
            handler = self.get_handler(filename, method)
            request = RequestType(status_code=200, headers=self.headers, body=b"", params=params, path=filename)
            if method == HTTPMethod.POST:
                request.body = self.rfile.read(int(self.headers['Content-Length']))
            if handler:
                return await self.process_request(handler, request)
            # Отправляем ответ неизвестного запроса
            self.handle_default_request()

        def do_GET(self):
            asyncio.run(self.handle_request(HTTPMethod.GET))

        def do_POST(self):
            asyncio.run(self.handle_request(HTTPMethod.POST))

    return AsyncRequestHandler
