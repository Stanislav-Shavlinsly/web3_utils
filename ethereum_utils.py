import requests
import json
from web3 import Web3, contract
from web3.contract import Contract
from web3.middleware import geth_poa_middleware

# Определение констант для различных провайдеров и адресов ABI
PROVIDERS = {
    'ethereum_holesky': 'https://ethereum-holesky.blockpi.network/v1/rpc/public',
    'ethereum_goerli': 'https://sepolia.infura.io/v3/0d6408dc0e754ca884f3b60a54de3228',
    'ethereum_sepolia': 'https://sepolia.infura.io/v3/0d6408dc0e754ca884f3b60a54de3228',
    'linea_goerli': 'https://linea-goerli.infura.io/v3/0d6408dc0e754ca884f3b60a54de3228',
    'polygon_amoy': 'https://polygon-amoy.infura.io/v3/0d6408dc0e754ca884f3b60a54de3228',
    'polygon_mumbai': 'https://polygon-mumbai.infura.io/v3/0d6408dc0e754ca884f3b60a54de3228',
    'arbitrum_sepolia': 'https://arbitrum-sepolia.infura.io/v3/0d6408dc0e754ca884f3b60a54de3228',
    'bsc_testnet': 'https://bsc-testnet.nodereal.io/v1/8f87841ec0744b58800f17e1832bee38'
}

URL_ABIS = {
    'ethereum_holesky': 'https://api-holesky.etherscan.io/api?module=contract&action=getabi&address=',
    'ethereum_goerli': 'https://api-goerli.etherscan.io/api?module=contract&action=getabi&address=',
    'ethereum_sepolia': 'https://api-sepolia.etherscan.io/api?module=contract&action=getabi&address=',
    'bsc_testnet': 'https://api-testnet.bscscan.com/api?module=contract&action=getabi&address='
}

CHAIN_IDS = {
    'ethereum_holesky': 17000,
    'ethereum_goerli': 5,
    'ethereum_sepolia': 11155111,
    'bsc_testnet': 97
}

# Используемый провайдер по умолчанию
PROVIDER = PROVIDERS['ethereum_holesky']
URL_ABI = URL_ABIS['ethereum_holesky']
CHAIN_ID = CHAIN_IDS['ethereum_holesky']

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

def send_transaction(contract_obj: Contract, wallet_address: str, private_key: str, method_name: str, *args) -> str | bool:
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