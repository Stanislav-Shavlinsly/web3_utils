# Инструкция по работе с контрактом

Этот проект предоставляет простые функции для работы с Ethereum контрактами через Python. Вы можете использовать эти функции для взаимодействия с контрактами на различных сетях Ethereum.

## Установка зависимостей

Для установки зависимостей, необходимо выполнить следующую команду в терминале:

`pip install -r requirements.txt`


Эта команда установит все необходимые библиотеки Python, указанные в файле requirements.txt.

## Использование функций

1. Установите зависимости, как описано выше.
2. Импортируйте необходимые функции из модуля `ethereum_utils`.
3. Создайте экземпляр контракта с помощью функции `new_contract`.
4. Вызовите методы контракта с помощью функции `read_method` или отправьте транзакцию с помощью функции `send_transaction`.

## Пример использования

```python
from ethereum_utils import new_contract, read_method, send_transaction

# Создание экземпляра контракта
contract_address = '0x123abc...'
contract_obj = new_contract(contract_address)

# Вызов метода для чтения данных из контракта
result = read_method(contract_obj, 'methodName', arg1, arg2)

# Отправка транзакции к контракту
tx_hash = send_transaction(contract_obj, wallet_address, private_key, 'methodName', arg1, arg2)