# Конфигурация контракта

Файл `config.py` содержит класс `ContractConfig`, который предназначен для хранения конфигурационных данных контракта Ethereum. Этот класс позволяет удобно организовывать и использовать конфигурацию для подключения к различным сетям Ethereum.

## Примеры конфигураций

Примеры конфигураций для различных сетей Ethereum представлены в файле `config.py`. Каждая конфигурация состоит из трех атрибутов:

- `provider`: URL-адрес провайдера для подключения к сети Ethereum.
- `url_abi`: URL-адрес для получения ABI контракта.
- `chain_id`: Идентификатор цепочки блокчейна (chain ID) для сети Ethereum.

Для установки сети, необходимо в файле `ethereum_utils.py` в переменную `contract_config` установить объект класса `ContractConfig` с необходимой сетью

```python
ethereum_holesky_config = ContractConfig(
    provider='https://ethereum-holesky.blockpi.network/v1/rpc/public',
    url_abi='https://api-holesky.etherscan.io/api?module=contract&action=getabi&address=',
    chain_id=17000
)

ethereum_goerli_config = ContractConfig(
    provider='https://sepolia.infura.io/v3/0d6408dc0e754ca884f3b60a54de3228',
    url_abi='https://api-goerli.etherscan.io/api?module=contract&action=getabi&address=',
    chain_id=5
)

ethereum_sepolia_config = ContractConfig(
    provider='https://sepolia.infura.io/v3/0d6408dc0e754ca884f3b60a54de3228',
    url_abi='https://api-sepolia.etherscan.io/api?module=contract&action=getabi&address=',
    chain_id=11155111
)

bsc_testnet_config = ContractConfig(
    provider='https://bsc-testnet.nodereal.io/v1/8f87841ec0744b58800f17e1832bee38',
    url_abi='https://api-testnet.bscscan.com/api?module=contract&action=getabi&address=',
    chain_id=97
)
```
# Ethereum Utils

Файл ethereum_utils.py содержит набор функций для работы с сетью Ethereum и смарт-контрактами. Этот модуль обеспечивает возможность создания объектов контрактов, выполнения методов контрактов, отправки транзакций, а также декодирования логов транзакций.

## Установка зависимостей

Для работы с кодом необходимо установить зависимости из файла `requirements.txt.` Для этого выполните следующую команду:

`pip install -r requirements.txt`

## Примеры использования

```python
# Импорт модуля и конфигурации контракта
from ethereum_utils import *

# Создание объекта контракта
contract_obj = new_contract('0x864Ce253cd3b6a1e923302F1805aB1DFa1647bF4')

# Чтение метода контракта
result = read_method(contract_obj, 'methodName', arg1, arg2)

# Отправка транзакции к контракту
tx_hash = send_transaction(contract_obj, wallet_address, private_key, 'methodName', arg1, arg2)

# Получение списка всех событий контракта
events_list = list_events(contract_obj)

# Декодирование логов транзакции по определенному списку ивентов
decoded_logs = decode_transaction_logs(contract_obj, tx_hash, event_names=['Event1', 'Event2'])

# Декодирование логов транзакции по всем ивентам
decoded_logs = decode_transaction_logs(contract_obj, tx_hash, event_names=['Event1', 'Event2'])

# Получение информации о блоке по его номеру
block_info = get_block_info(block_number)

# Получение информации о транзакции по её хешу
tx_info = get_transaction_info(tx_hash)

```
