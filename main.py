from PyCloudKit import CloudServer

server = CloudServer('127.0.0.1', 8080, 'databases/cloud.db')
              
def main():
    server.start()

if __name__ == '__main__':
    main()