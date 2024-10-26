# PyCloudKit: Набор инструментов для создания облака на Python

## Описание

PyCloudKit предоставляет набор инструментов для создания облака на Python. Он включает:
* Серверный класс для поддержания облака
* Клиентский класс для взаимодействия с облаком

## Функции

*   Легкость использования: PyCloudKit предоставляет простой интерфейс для создания и управления облаком.
*   Интеграция: PyCloudKit может работать с любым другим кодом, который взаимодействует с облаком.

## Примеры использования

### Простое облако

```python
from PyCloudKit import CloudServer

server = CloudServer('127.0.0.1', 8080, 'databases/cloud.db')

def main():
    server.start()

if __name__ == '__main__':
    main()
```

### Подключение к облаку

```python
from PyCloudKit import CloudClient

client = CloudClient('127.0.0.1', 8080)

def main():
    # Задать значение в облаке
    client.set('key', 'value')
    # Получить значение из облака
    value = client.get('key')
    print(value)

if __name__ == '__main__':
    main()
```
# Установка

Pyserver можно установить с помощью pip:

```bash
pip install PyCloudKit
```

# Лицензия

Pyserver является открытым проектом. Вы можете получить лицензию на [GitHub](https://github.com/professionsalincpp/PyCloudKit/main/LICENSE).