from .request import *

class AsyncClient:
    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
    
    async def get(self, path: str) -> ResponseType:
        async with AsyncRequest(self.host, self.port) as request:
            return await request.get(path)
        
    async def post(self, path: str, data: bytes) -> ResponseType:
        async with AsyncRequest(self.host, self.port) as request:
            return await request.post(path, data)