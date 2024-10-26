from .request import *

class AsyncClient:
    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
    
    async def get(self, path: str) -> ResponseType:
        request = AsyncRequest(self.host, self.port)
        await request.start()
        try:
            print(f"Requesting {path}")
            return await request.get(path)
        finally:
            await request.close()
        
    async def post(self, path: str, data: bytes) -> ResponseType:
        request = AsyncRequest(self.host, self.port)
        await request.start()
        try:
            return await request.post(path, data)
        finally:
            await request.close()