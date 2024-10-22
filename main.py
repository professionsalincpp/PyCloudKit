import pyserver

server = pyserver.AsyncServer('localhost', 8080)

@server.route('/add')
async def add(request: pyserver.Request) -> pyserver.Response:
    if request.params.get('a') is None or request.params.get('b') is None:
        return pyserver.Response(400, {'Content-Type': 'text/plain'}, b'Please provide a and b')
    a = int(request.params['a'])
    b = int(request.params['b'])
    return pyserver.Response(200, {'Content-Type': 'text/plain'}, str(a + b).encode('utf-8'))
              
def main():
    server.start()

if __name__ == '__main__':
    main()