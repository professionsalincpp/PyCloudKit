from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict
import inspect

@dataclass
class ResponseType:
    """
    A response object
    Represents a HTTP response.
    """
    status_code: int
    headers: Dict[str, str]
    body: bytes
    def __str__(self) -> str:
        return f"Response(status_code={self.status_code}, headers={self.headers}, body={self.body})"

@dataclass
class RequestType(ResponseType):
    """
    A request object
    Represents a HTTP request.
    """
    params: Dict[str, str]
    def __str__(self) -> str:
        return f"Request(status_code={self.status_code}, headers={self.headers}, body={self.body}, params={self.params})"

class RequestHandler:
    class Method(Enum):
        GET = 1
        POST = 2
    def __init__(self, func: Callable[[RequestType], ResponseType], method: Method=Method.GET, path: str="/") -> None:
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