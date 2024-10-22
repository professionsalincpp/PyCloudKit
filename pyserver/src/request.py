from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from enum import Enum
from http.client import HTTPConnection, HTTPResponse
from http.server import BaseHTTPRequestHandler
from typing import Optional, List, Dict
from .types import *
from .utils import *

class AsyncRequest:

    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.client: Optional[HTTPConnection] = None

    async def _start(self) -> None:
        self.client = HTTPConnection(self.host, self.port)
        print(f"Client connected {self.client}")
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
                print("params_str", params_str)
                for param in params_str.split('&'):
                    key, value = param.split('=')
                    params[key] = value
            for handler in self.handlers:
                if handler.path == filename and handler.method == RequestHandler.Method.GET:
                    response: ResponseType = await handler.handle(request=RequestType(status_code=200, headers=self.headers, body=b"", params=params))
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
