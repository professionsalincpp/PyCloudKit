import asyncio
from pyserver.cloud import CloudClient
from pyserver.cloud.src.cloud import from_string

client = CloudClient('127.0.0.1', 8080)

def set(key, value):
    asyncio.run(client.set(key, value))

def get(key):
    return asyncio.run(client.get(key))

def main():
    while True:
        a = input()
        splitted = a.split(" ")
        if splitted[0] == "":
            break
        if len(splitted) >= 2:
            print(f"Set {splitted[0]} to {splitted[1]} with type {type(from_string(splitted[1]))}")
            set(splitted[0], from_string(splitted[1]))
        elif len(splitted) == 1:
            print(get(splitted[0]))

if __name__ == "__main__":
    main()
