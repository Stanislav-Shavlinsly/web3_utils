from Web3_Utils import Web3Utils, config, UserWallet
import json

user_wallet = UserWallet('Подставить свой адрес',
                         'Подставить свой приватный ключ')

# Чтение ABI из файла
with open('abi_test_erc20.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)

# Чтение байт-кода из файла
with open('byte_test_erc20.txt', 'r') as bytecode_file:
    contract_bytecode = bytecode_file.read().strip()

# Инициализация Web3Utils
web3_utils = Web3Utils(config.ethereum_sepolia_config)

# Деплой контракта
tx_hash = web3_utils.deploy_contract(contract_abi, contract_bytecode, user_wallet=user_wallet, constructor_args=['name', 'symbol', 9])

# Получаем адрес контракта
contract_address = web3_utils.get_contract_address(tx_hash)
