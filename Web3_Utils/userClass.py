import os
from eth_keys import keys
from eth_account import Account

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

    @classmethod
    def generate_ethereum_wallet(cls, username=None):
        """
        Генерирует новый кошелек Ethereum с публичным и приватным ключами.

        Этот метод использует криптографически безопасный способ генерации случайных чисел
        для создания приватного ключа, а затем получает соответствующий ему публичный ключ
        и адрес кошелька Ethereum.

        Args:
            username (str, optional): Имя пользователя, которое будет ассоциировано с новым кошельком.

        Returns:
            UserWallet: Объект класса UserWallet, содержащий новые публичный и приватный ключи,
                        а также имя пользователя, если оно было предоставлено.
        """
        private_key = keys.PrivateKey(os.urandom(32))
        public_key = private_key.public_key
        address = public_key.to_checksum_address()
        return cls(str(address), str(private_key), username)

    @classmethod
    def generate_user_from_private_key(cls, private_key, username=None):
        """
        Генерирует объект класса UserWallet на основе приватного ключа.

        Args:
            private_key (str): Приватный ключ пользователя в hex формате.
            username: (str, optional): Имя пользователя, которое будет ассоциировано с новым кошельком.

        Returns:
            UserWallet: Объект класса UserWallet с соответствующим публичным адресом и приватным ключом.
        """
        account = Account.from_key(private_key)
        public_address = account.address
        return cls(str(public_address), str(private_key), username)
