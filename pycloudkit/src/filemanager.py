import os

class FileIsDirectoryError(Exception):
    pass

def getabsolutepath(path: str, root_path: str = '/') -> str:
    return os.path.join(root_path, path)

def getcontent(path: str) -> bytes:
    if os.path.isdir(path):
        raise FileIsDirectoryError(f"File {path} is a directory")
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {path} does not exist")
    with open(path, 'rb') as file:
        return file.read()
    
def listfiles(path: str) -> list[str]:
    return os.listdir(path)
    