import requests
import json
from web3 import Web3
from web3.contract import Contract
from web3.middleware import geth_poa_middleware
from web3.exceptions import MismatchedABI

from config import ethereum_holesky_config, ethereum_goerli_config, ethereum_sepolia_config, bsc_testnet_config


class Web3Utils:
    """
    Обеспечивает удобный интерфейс для взаимодействия с Ethereum-совместимыми блокчейнами, позволяя создавать
    и взаимодействовать с объектами контрактов, отправлять транзакции, читать методы и события контрактов,
    а также получать информацию о блоках и транзакциях.

    Атрибуты:
        provider (str): URL провайдера для подключения к блокчейну.
        url_abi (str): Базовый URL для доступа к ABI контракта.
        chain_id (int): Идентификатор цепочки для выполнения транзакций.
        web3 (Web3): Экземпляр Web3 для взаимодействия с блокчейном.
        contract_obj (Contract): Объект контракта для взаимодействия.

    Аргументы:
        contract_config: Конфигурация подключения к блокчейну и контракту.
        contract_address (str): Адрес контракта в блокчейне.
    """

    def __init__(self, contract_config, contract_address):
        self.provider = contract_config.provider
        self.url_abi = contract_config.url_abi
        self.chain_id = contract_config.chain_id
        self.web3 = Web3(Web3.HTTPProvider(self.provider))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.contract_obj = Web3Utils.new_contract(self, contract_address)

    def new_contract(self, contract_address: str) -> Contract:
        """
        Создает и возвращает объект контракта по указанному адресу, используя ABI, полученное через HTTP-запрос.

        Args:
            contract_address (str): Адрес контракта в сети.

        Returns:
            Contract: Объект контракта для взаимодействия.
        """
        url = self.url_abi + contract_address
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).text
        abi = json.loads(response)['result']
        return self.web3.eth.contract(address=contract_address, abi=abi)

    def read_method(self, method_name: str, *args) -> str | int | bool:
        """
        Выполняет вызов метода чтения контракта без отправки транзакции и возвращает результат.

        Args:
            method_name (str): Название метода контракта для вызова.
            *args: Переменное количество аргументов, передаваемых в метод.

        Returns:
            Union[str, int, bool]: Результат выполнения метода контракта.
        """
        method = self.contract_obj.functions[method_name](*args)
        return method.call()

    def send_transaction(self, method_name: str,
                         *args, user_wallet=None, wallet_address=None, private_key=None) -> str | bool:
        """
        Отправляет транзакцию для вызова метода контракта, используя кошелек и приватный ключ. Параметры кошелька и ключа
        могут быть предоставлены либо через объект user_wallet класса UserWallet, либо через прямое указание
        wallet_address и private_key.

        Args:
            method_name (str): Название метода контракта для вызова.
            *args: Аргументы метода.
            user_wallet (UserWallet, optional): Объект кошелька пользователя.
            wallet_address (str, optional): Адрес кошелька отправителя.
            private_key (str, optional): Приватный ключ кошелька отправителя.

        Returns:
            Union[str, bool]: Хэш транзакции в случае успеха или False в случае ошибки.

        Raises:
            ValueError: Если не предоставлены ни user_wallet, ни wallet_address с private_key.
        """
        if user_wallet:
            wallet_address = user_wallet.public_key
            private_key = user_wallet.private_key
        elif not wallet_address or not private_key:
            raise ValueError("Необходимо предоставить user_wallet или wallet_address и private_key.")

        if not self.web3.isConnected():
            print("Не удалось подключиться к сети Ethereum.")
            return False

        method = self.contract_obj.functions[method_name](*args)

        transaction = {
            'to': self.contract_obj.address,
            'value': 0,
            'gas': 400000,
            'gasPrice': self.web3.eth.gasPrice,
            'nonce': self.web3.eth.getTransactionCount(wallet_address),
            'chainId': self.chain_id,
        }
        transaction['data'] = method.buildTransaction({'from': wallet_address})['data']

        signed_transaction = self.web3.eth.account.sign_transaction(transaction, private_key)

        try:
            tx_hash = self.web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
            print(f"Транзакция успешно отправлена. Хэш транзакции: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            print(f"Ошибка при отправке транзакции: {e}")
            return False

    def list_events(self):
        """
        Возвращает список имен всех событий, определенных в контракте.

        Returns:
            List[str]: Список имен событий контракта.
        """
        events = self.contract_obj.events

        all_events = [name for name in dir(events) if not name.startswith('_') and not name == 'abi']

        return all_events

    def decode_transaction_logs(self, tx_hash: str, event_names=None) -> list:
        """
        Расшифровывает и возвращает логи указанной транзакции, фильтруя по заданным событиям.

        Args:
            tx_hash (str): Хеш транзакции для анализа логов.
            event_names (List[str], optional): Список названий событий для фильтрации логов.
                                               Если None, используются все события контракта.

        Returns:
            List[dict]: Список декодированных логов событий в порядке их появления.
        """
        if event_names is None:
            event_names = self.list_events()

        tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)

        if tx_receipt is None:
            print("Транзакция не найдена")
            return []

        decoded_logs = []
        for log in tx_receipt['logs']:
            for event_name in event_names:
                try:
                    event = getattr(self.contract_obj.events, event_name)()
                    decoded_log = event.processLog(log)
                    decoded_logs.append(decoded_log)
                except MismatchedABI:
                    pass

        decoded_logs.sort(key=lambda x: x['logIndex'])

        return decoded_logs

    def get_block_info(self, block_number: int) -> dict | None:
        """
        Получает и возвращает информацию о блоке по его номеру.

        Args:
            block_number (int): Номер блока для получения информации.

        Returns:
            dict | None: Информация о блоке или None в случае ошибки.
        """
        try:
            block = self.web3.eth.getBlock(block_number)
            return block
        except Exception as e:
            print("Произошла ошибка:", e)
            return None

    def get_transaction_info(self, tx_hash: str) -> dict | None:
        """
        Получает и возвращает информацию о транзакции по ее хешу.

        Args:
            tx_hash (str): Хеш транзакции для получения информации.

        Returns:
            dict | None: Информация о транзакции или None в случае ошибки.
        """
        try:
            tx = self.web3.eth.getTransaction(tx_hash)
            return tx
        except Exception as e:
            print("Произошла ошибка:", e)
            return None


class UserWallet:
    """
    Представляет кошелек пользователя, содержащий публичный и приватный ключи для взаимодействия с блокчейном.

    Атрибуты:
        username (str, optional): Имя пользователя, ассоциированное с кошельком.
        public_key (str): Публичный ключ кошелька, используемый как адрес в блокчейне.
        private_key (str): Приватный ключ кошелька, используемый для подписи транзакций.

    Аргументы:
        public_key (str): Публичный ключ кошелька.
        private_key (str): Приватный ключ кошелька.
        username (str, optional): Имя пользователя.
    """
    def __init__(self, public_key: str, private_key: str, username=None):
        self.username = username
        self.public_key = public_key
        self.private_key = private_key
