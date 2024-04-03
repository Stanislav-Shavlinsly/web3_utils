import requests
import json
from web3 import Web3
from web3.contract import Contract
from web3.middleware import geth_poa_middleware
from web3.exceptions import MismatchedABI

from config import ethereum_holesky_config, ethereum_goerli_config, ethereum_sepolia_config, bsc_testnet_config

contract_config = ethereum_sepolia_config

PROVIDER = contract_config.provider
URL_ABI = contract_config.url_abi
CHAIN_ID = contract_config.chain_id

web3 = Web3(Web3.HTTPProvider(PROVIDER))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)


def new_contract(contract_address: str) -> Contract:
    """
    Создает новый объект контракта на основе его адреса.

    Args:
    contract_address (str): Адрес контракта.

    Returns:
    Contract: Объект контракта.
    """
    url = URL_ABI + contract_address
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    abi_3 = response.text
    abi = json.loads(abi_3)['result']

    contract_obj = web3.eth.contract(address=contract_address, abi=abi)
    return contract_obj


def read_method(contract_obj: Contract, method_name: str, *args) -> str | int | bool:
    """
    Выполняет чтение метода контракта.

    Args:
    contract_obj (Contract): Объект контракта.
    method_name (str): Название метода.
    *args: Аргументы метода.

    Returns:
    Union[str, int, bool]: Результат выполнения метода.
    """
    method = contract_obj.functions[method_name](*args)
    return method.call()


def send_transaction(contract_obj: Contract, wallet_address: str, private_key: str, method_name: str,
                     *args) -> str | bool:
    """
    Отправляет транзакцию к контракту.

    Args:
    contract_obj (Contract): Объект контракта.
    wallet_address (str): Адрес кошелька.
    private_key (str): Приватный ключ кошелька.
    method_name (str): Название метода контракта.
    *args: Аргументы метода.

    Returns:
    Union[str, bool]: Хэш транзакции в случае успешной отправки или False в случае ошибки.
    """
    if not web3.isConnected():
        print("Не удалось подключиться к сети Ethereum.")
        return False

    method = contract_obj.functions[method_name](*args)

    transaction = {
        'to': contract_obj.address,
        'value': 0,
        'gas': 400000,
        'gasPrice': web3.eth.gasPrice,
        'nonce': web3.eth.getTransactionCount(wallet_address),
        'chainId': CHAIN_ID,
    }
    transaction['data'] = method.buildTransaction({'from': wallet_address})['data']

    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)

    try:
        tx_hash = web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
        print(f"Транзакция успешно отправлена. Хэш транзакции: {tx_hash.hex()}")
        return tx_hash.hex()
    except Exception as e:
        print(f"Ошибка при отправке транзакции: {e}")
        return False


def list_events(contract_obj: Contract):
    """
    Выводит список всех событий контракта.

    Args:
    contract_obj (Contract): Объект контракта.
    """
    events = contract_obj.events

    all_events = [name for name in dir(events) if not name.startswith('_') and not name == 'abi']

    return all_events


def decode_transaction_logs(contract_obj: Contract, tx_hash: str, event_names=None) -> list:
    """
    Расшифровывает логи транзакции и возвращает их в порядке logIndex.

    Args:
    contract_obj (Contract): Объект контракта.
    tx_hash (str): Хеш транзакции.
    event_names (list, optional): Список названий событий для расшифровки.
                                  Если не указан, будет получен список всех событий контракта.

    Returns:
    list: Список декодированных транзакций в порядке logIndex.
    """
    if event_names is None:
        event_names = list_events(contract_obj)

    tx_receipt = web3.eth.getTransactionReceipt(tx_hash)

    if tx_receipt is None:
        print("Транзакция не найдена")
        return []

    decoded_logs = []
    for log in tx_receipt['logs']:
        for event_name in event_names:
            try:
                event = getattr(contract_obj.events, event_name)()
                decoded_log = event.processLog(log)
                decoded_logs.append(decoded_log)
            except MismatchedABI:
                pass

    decoded_logs.sort(key=lambda x: x['logIndex'])

    return decoded_logs


def get_block_info(block_number: int) -> dict | None:
    """
    Получает информацию о блоке по его номеру.

    Args:
    block_number (int): Номер блока.

    Returns:
    dict | None: Информация о блоке в виде словаря. Возвращает None в случае ошибки.
    """
    try:
        block = web3.eth.getBlock(block_number)
        return block
    except Exception as e:
        print("Произошла ошибка:", e)
        return None


def get_transaction_info(tx_hash: str) -> dict | None:
    """
    Получает информацию о транзакции по её хешу.

    Args:
    tx_hash (str): Хеш транзакции.

    Returns:
    dict | None: Информация о транзакции в виде словаря. Возвращает None в случае ошибки.
    """
    try:
        tx = web3.eth.getTransaction(tx_hash)
        return tx
    except Exception as e:
        print("Произошла ошибка:", e)
        return None

