import requests
import json
from web3 import Web3
from web3.contract import Contract
from web3.middleware import geth_poa_middleware
from web3.exceptions import MismatchedABI, TransactionNotFound


class Web3Utils:
    """
    Обеспечивает удобный интерфейс для взаимодействия с Ethereum-совместимыми блокчейнами, позволяя создавать
    и взаимодействовать с объектами контрактов, отправлять транзакции, читать методы и события контрактов,
    а также получать информацию о блоках и транзакциях. Позволяет также получать URL для отслеживания
    транзакций в блокчейн-эксплорере и загружать ABI из локального файла.

    Атрибуты:
        provider (str): URL провайдера для подключения к блокчейну.
        url_abi (str): Базовый URL для доступа к ABI контракта.
        chain_id (int): Идентификатор цепочки для выполнения транзакций.
        web3 (Web3): Экземпляр Web3 для взаимодействия с блокчейном.
        contract_obj (Contract, optional): Объект контракта для взаимодействия, может быть None.
        url_tx_explorer (str, optional): URL-адрес проводника транзакций, может быть None.
        path_abi (str, optional): Путь к локальному файлу с ABI контракта, может быть None.

    Аргументы:
        contract_config: Конфигурация подключения к блокчейну и контракту.
        contract_address (str, optional): Адрес контракта в блокчейне. Может быть None.
        abi (list, optional): ABI контракта. Если не указан, ABI будет загружено через HTTP-запрос или из локального файла.
        path_abi (str, optional): Путь к локальному файлу с ABI контракта.
    """

    def __init__(self, contract_config, contract_address=None, abi=None, path_abi=None, proxy_address=None):
        self.provider = contract_config.provider
        self.url_abi = contract_config.url_abi
        self.abi = abi
        self.path_abi = path_abi
        self.proxy_address = proxy_address
        self.chain_id = contract_config.chain_id
        self.web3 = Web3(Web3.HTTPProvider(self.provider))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.contract_obj = None if contract_address is None else self.new_contract(contract_address)
        self.url_tx_explorer = contract_config.url_tx_explorer

    def new_contract(self, contract_address: str) -> Contract:
        """
        Создает и возвращает объект контракта по указанному адресу, используя ABI.
        Если ABI не было предоставлено в конструкторе, оно получается через HTTP-запрос
        к указанному URL-адресу ABI или из локального файла, если был предоставлен путь к файлу.

        Args:
            contract_address (str): Адрес контракта в сети.

        Returns:
            Contract: Объект контракта для взаимодействия с ним.
        """
        if self.path_abi:
            with open(self.path_abi, 'r') as abi_file:
                abi = json.load(abi_file)
        elif self.url_abi:
            if self.proxy_address:
                url = self.url_abi + self.proxy_address
            else:
                url = self.url_abi + contract_address
            headers = {'User-Agent': 'Mozilla/5.0'}
            while True:
                response = requests.get(url, headers=headers).text
                abi = json.loads(response)['result']
                if abi != 'Max rate limit reached, please use API Key for higher rate limit':
                    break

        else:
            abi = self.abi
        if type(abi) is str:
            abi = json.loads(abi)
        self.abi = abi
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
                         *args, user_wallet=None, wallet_address=None, private_key=None, value=0, gas=1000000, gasPriceMultiplier=1) -> str | bool:
        """
        Отправляет транзакцию для вызова метода контракта, используя кошелек и приватный ключ. Параметры кошелька и ключа
        могут быть предоставлены либо через объект user_wallet класса UserWallet, либо через прямое указание
        wallet_address и private_key.

        Args:
            gas (int): Количество газа для транзакции
            value (int): Количество нативной валюты в транзакции
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
            'value': value,
            'gas': gas,
            'gasPrice': int(self.web3.eth.gasPrice * gasPriceMultiplier),
            'nonce': self.web3.eth.getTransactionCount(wallet_address),
            'chainId': self.chain_id
        }

        transaction['data'] = method.buildTransaction({'from': wallet_address, 'gas': 285000})['data']

        signed_transaction = self.web3.eth.account.sign_transaction(transaction, private_key)

        try:
            tx_hash = self.web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
            print(f"Транзакция успешно отправлена. Хэш транзакции: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            print(f"Ошибка при отправке транзакции: {e}")
            return False

    def send_transaction2(self, data_trans, user_wallet=None, wallet_address=None, private_key=None) -> str | bool:
        """
        Отправляет транзакцию для вызова метода контракта, используя кошелек и приватный ключ. Параметры кошелька и ключа
        могут быть предоставлены либо через объект user_wallet класса UserWallet, либо через прямое указание
        wallet_address и private_key.

        Args:
            gas (int): Количество газа для транзакции
            value (int): Количество нативной валюты в транзакции
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

        data = {
          "value": 0,
          "nonce": 1,
          "chainId": 157,
            "gas": 4000000000,
            'gasPrice': self.web3.eth.gasPrice,
          "from": "0xBC68A15DEec05e79A6C0D831C2265687D64302bc",
          "to": "0x5486B21977203C3b4Da633a2729E62902B122fcB",
          "data": f"{data_trans}"
        }
        signed_transaction = self.web3.eth.account.sign_transaction(data, private_key)

        try:
            tx_hash = self.web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
            print(f"Транзакция успешно отправлена. Хэш транзакции: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            print(f"Ошибка при отправке транзакции: {e}")
            return False

    def deploy_contract(self, abi: str, bytecode: str, constructor_args: list = None, user_wallet=None,
                        wallet_address=None, private_key=None) -> str:
        """
        Деплоит новый смарт-контракт в блокчейн.

        Args:
            abi (str): ABI контракта.
            bytecode (str): Байт-код контракта.
            constructor_args (list, optional): Аргументы конструктора контракта.
            user_wallet (UserWallet, optional): Объект кошелька пользователя.
            wallet_address (str, optional): Адрес кошелька отправителя.
            private_key (str, optional): Приватный ключ кошелька отправителя.

        Returns:
            str: Хэш транзакции деплоя контракта.
        """
        if user_wallet:
            wallet_address = user_wallet.public_key
            private_key = user_wallet.private_key
        elif not wallet_address or not private_key:
            raise ValueError("Необходимо предоставить user_wallet или wallet_address и private_key.")

        if not self.web3.isConnected():
            print("Не удалось подключиться к сети Ethereum.")
            return False

        Contract = self.web3.eth.contract(abi=abi, bytecode=bytecode)
        if constructor_args:
            transaction = Contract.constructor(*constructor_args).buildTransaction({
                'from': wallet_address,
                'nonce': self.web3.eth.getTransactionCount(wallet_address),
                'gas': 4000000,
                'gasPrice': self.web3.eth.gasPrice,
                'chainId': self.chain_id
            })
        else:
            transaction = Contract.constructor().buildTransaction({
                'from': wallet_address,
                'nonce': self.web3.eth.getTransactionCount(wallet_address),
                'gas': 4000000,
                'gasPrice': self.web3.eth.gasPrice,
                'chainId': self.chain_id
            })

        signed_transaction = self.web3.eth.account.sign_transaction(transaction, private_key)

        try:
            tx_hash = self.web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
            print(f"Контракт успешно деплоен. Хэш транзакции: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            print(f"Ошибка при деплое контракта: {e}")
            return False

    def send_native_currency(self, to_address: str, value: int, user_wallet=None, private_key=None) -> str | bool:
        """
        Отправляет транзакцию, переводя нативную валюту на указанный адрес. Параметры кошелька и ключа
        могут быть предоставлены либо через объект user_wallet класса UserWallet, либо через прямое указание
        private_key.

        Args:
            to_address (str): Адрес кошелька получателя.
            value (int): Количество нативной валюты в wei для отправки.
            user_wallet (UserWallet, optional): Объект кошелька пользователя для отправки.
            private_key (str, optional): Приватный ключ кошелька отправителя.

        Returns:
            Union[str, bool]: Хэш транзакции в случае успеха или False в случае ошибки.

        Raises:
            ValueError: Если не предоставлены ни user_wallet, ни private_key.
        """
        if user_wallet:
            wallet_address = user_wallet.public_key
            private_key = user_wallet.private_key
        elif not private_key:
            raise ValueError("Необходимо предоставить user_wallet или private_key.")

        if not self.web3.isConnected():
            print("Не удалось подключиться к сети Ethereum.")
            return False

        transaction = {
            'to': to_address,
            'value': value,
            'gas': 21000,
            'gasPrice': self.web3.eth.gasPrice,
            'nonce': self.web3.eth.getTransactionCount(wallet_address),
            'chainId': self.chain_id,
        }

        signed_transaction = self.web3.eth.account.sign_transaction(transaction, private_key)

        try:
            tx_hash = self.web3.eth.sendRawTransaction(signed_transaction.rawTransaction)
            print(f"Транзакция успешно отправлена. Хэш транзакции: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            print(f"Ошибка при отправке транзакции: {e}")
            return False

    def wait_transaction_receipt(self, tx_hash):
        """
        Ожидает подтверждения транзакции.

        Параметры:
            tx_hash (str): Хеш транзакции для ожидания.

        Возвращает:
            TransactionReceipt: Получает квитанцию транзакции после ее подтверждения.
        """
        return self.web3.eth.waitForTransactionReceipt(tx_hash)

    def list_methods(self) -> dict:
        """
        Возвращает словарь с методами контракта, разделёнными на категории чтения и записи.

        Этот метод позволяет легко идентифицировать, какие методы контракта предназначены для чтения данных
        и какие предназначены для выполнения транзакций (запись). Это особенно полезно для интерфейсов,
        которые требуют разделения методов на те, что могут изменять состояние блокчейна, и те, что не изменяют его.

        Returns:
            dict: Словарь с ключами 'read_methods' и 'write_methods', каждый из которых содержит список строк.
                  Каждая строка в списках представляет название метода контракта соответствующей категории.
        """
        read_methods = []
        write_methods = []
        for method in self.abi:
            if method["type"] == "function":
                if method['stateMutability'] == 'view':
                    inputs_method = []
                    outputs_method = []

                    for inputs in method["inputs"]:
                        inputs_method.append({
                            "name": inputs["name"],
                            "type": inputs["type"]
                        })
                    for outputs in method["outputs"]:
                        outputs_method.append({
                            "name": outputs["name"],
                            "type": outputs["type"]
                        })
                    read_methods.append({
                        'name': method['name'],
                        'inputs': inputs_method,
                        "outputs": outputs_method
                    })
                elif method['stateMutability'] == 'nonpayable' or method['stateMutability'] == 'payable':
                    write_methods.append({
                        'name': method['name'],
                        'inputs': method['inputs'],
                        "payable": False if method['stateMutability'] == 'nonpayable' else True,
                    })
        list_methods = {
            'read_methods': read_methods,
            'write_methods': write_methods
        }
        return list_methods

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
        В случае отсутствия транзакции, функция ожидает ее появления с использованием метода
        wait_transaction_receipt.

        Args:
            tx_hash (str): Хеш транзакции для анализа логов.
            event_names (List[str], optional): Список названий событий для фильтрации логов.
                                               Если None, используются все события контракта.

        Returns:
            List[dict]: Список декодированных логов событий в порядке их появления.
        """
        if event_names is None:
            event_names = self.list_events()

        try:
            tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
        except TransactionNotFound:
            print("Ожидание появления транзакции...")
            tx_receipt = self.wait_transaction_receipt(tx_hash)
        except Exception as e:
            print(f"Произошла ошибка при получении квитанции транзакции: {e}")
            return []

        if tx_receipt is None:
            print("Транзакция не найдена после ожидания.")
            return []

        decoded_logs = []
        for log in tx_receipt['logs']:
            for event_name in event_names:
                try:
                    event = getattr(self.contract_obj.events, event_name)()
                    decoded_log = event.processLog(log)
                    decoded_logs.append(decoded_log)
                except MismatchedABI:
                    continue

        decoded_logs.sort(key=lambda x: x['logIndex'])

        return decoded_logs

    def get_block_info(self, block_number: int, full_transactions: bool=False) -> dict | None:
        """
        Получает и возвращает информацию о блоке по его номеру.

        Args:
            block_number (int): Номер блока для получения информации.

        Returns:
            dict | None: Информация о блоке или None в случае ошибки.
        """
        try:
            block = self.web3.eth.getBlock(block_number, full_transactions)
            return block
        except Exception as e:
            print("Произошла ошибка:", e)
            return None

    def get_transaction_info(self, tx_hash: str) -> dict | None:
        """
        Получает и возвращает информацию о транзакции по ее хешу. В случае отсутствия транзакции,
        функция ожидает ее появления с использованием метода wait_transaction_receipt.

        Args:
            tx_hash (str): Хеш транзакции для получения информации.

        Returns:
            dict | None: Информация о транзакции или None в случае ошибки.
        """
        try:
            return self.web3.eth.getTransaction(tx_hash)
        except TransactionNotFound:
            print("Ожидание появления транзакции...")
            self.wait_transaction_receipt(tx_hash)
            return self.web3.eth.getTransaction(tx_hash)
        except Exception as e:
            print(f"Произошла ошибка при получении информации о транзакции: {e}")
            return None

    def give_url_tx(self, tx_hash: str) -> bool | None:
        """
        Генерирует полный URL для отслеживания транзакции в блокчейн-эксплорере на основе переданного хеша транзакции.

        Args:
            tx_hash (str): Хеш транзакции, для которой требуется получить URL.

        Returns:
            str: Полный URL-адрес для просмотра транзакции в блокчейн-эксплорере.
        """
        return self.url_tx_explorer + tx_hash if self.url_tx_explorer else None

    def get_transaction_status(self, tx_hash: str) -> bool | None:
        """
        Получает статус транзакции по ее хешу. В случае отсутствия транзакции,
        функция ожидает ее подтверждения с использованием метода wait_transaction_receipt.

        Args:
            tx_hash (str): Хеш транзакции для проверки статуса.

        Returns:
            bool | None: True, если транзакция успешно выполнена, False, если
            транзакция не выполнена, или None, если возникла ошибка при попытке получить статус.

        Raises:
            TransactionNotFound: Если транзакция не найдена в блокчейне после ожидания.
            Exception: Если произошла ошибка при получении информации о транзакции.
        """
        try:
            return bool(self.web3.eth.getTransactionReceipt(tx_hash).status)
        except TransactionNotFound:
            print("Ожидание появления транзакции...")
            self.wait_transaction_receipt(tx_hash)
            return bool(self.web3.eth.getTransactionReceipt(tx_hash).status)
        except Exception as e:
            print(f"Произошла ошибка при получении информации о статусе транзакции: {e}")
            return None

    def get_contract_address(self, tx_hash: str) -> str:
        """
        Извлекает адрес задеплоенного контракта из хеша транзакции.

        Args:
            tx_hash (str): Хэш транзакции деплоя контракта.

        Returns:
            str: Адрес задеплоенного контракта.
        """
        try:
            # Получаем квитанцию транзакции
            receipt = self.wait_transaction_receipt(tx_hash)

            # Извлекаем адрес контракта из квитанции
            contract_address = receipt['contractAddress']
            return contract_address
        except Exception as e:
            print(f"Ошибка при получении адреса контракта: {e}")
            return None
