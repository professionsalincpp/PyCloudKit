from pycloudkit.src.utils import encode_uri_params
from ...src.filemanager import *
from ...src.types import *


def anyhandlerfile(path: str, rootpath: str) -> ResponseType:
    absolute_path = getabsolutepath(path, rootpath)
    content: bytes = b''
    try:
        content = getcontent(absolute_path)
        return ResponseType(status_code=200, headers={'Content-Type': 'application/octet-stream'}, body=content)
    except FileNotFoundError:
        print(f'File {absolute_path} not found')
        return ResponseType(status_code=404, headers={'Content-Type': 'text/plain'}, body=b'File not found')
    except FileIsDirectoryError:
        explorer_html_path = getabsolutepath(os.path.join(os.path.dirname(__file__), 'explorer.html'))
        content = getcontent(explorer_html_path)
        try:
            files = listfiles(absolute_path)
        except PermissionError:
            return ResponseType(status_code=403, headers={'Content-Type': 'text/plain'}, body=b'Permission denied')
        parent = os.path.dirname(absolute_path)
        
        content += f'<button onclick="redirect(\'{encode_uri_params(parent)}\')"><img style="width: 30px; height: 30px; vertical-align: middle" src="https://img.icons8.com/?size=100&id=71cUHRMvCNMk&format=png&color=000000"/>..</button><br/>'.encode()
        
        for file in files:
            content += f'<button onclick="redirect(\'{encode_uri_params(os.path.relpath(os.path.join(absolute_path, file), rootpath)).replace('\\', '/').lstrip(rootpath)}\')"><img style="width: 30px; height: 30px; vertical-align: middle" src="https://img.icons8.com/?size=100&id=71cUHRMvCNMk&format=png&color=000000"/>{os.path.relpath(os.path.join(absolute_path, file), rootpath)}</button><br/>'.encode()
    return ResponseType(status_code=200, headers={'Content-Type': 'text/html'}, body=content)

 
