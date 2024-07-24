import requests


class ContractConfig:
    """
    Класс для хранения конфигурационных данных контракта.

    Attributes:
        name (str, optional): Имя конфигурации сети для удобства идентификации.
        provider (str): URL-адрес провайдера для подключения к сети Ethereum.
        url_abi (str, optional): URL-адрес для получения ABI контракта. Может быть None, если ABI загружается иначе.
        chain_id (int): Идентификатор цепочки блокчейна (chain ID) для сети Ethereum.
        url_tx_explorer (str, optional): URL-адрес проводника транзакций (explorer), используемого для отслеживания транзакций.
                                         Может быть None, если отслеживание транзакций не требуется.
    """
    all_configs = []

    def __init__(self, provider, chain_id, url_abi=None, url_tx_explorer=None, name=None):
        """
        Инициализирует объект класса ContractConfig с данными для подключения и взаимодействия с блокчейн-сетью.

        Args:
            provider (str): URL-адрес провайдера для подключения к сети Ethereum.
            chain_id (int): Идентификатор цепочки блокчейна (chain ID) для сети Ethereum.
            url_abi (str, optional): URL-адрес для получения ABI контракта. Может быть None, если ABI загружается иначе.
            url_tx_explorer (str, optional): URL-адрес проводника транзакций (explorer), используемого для отслеживания транзакций.
            name (str, optional): Имя конфигурации сети.
        """
        self.provider = provider
        self.url_abi = url_abi
        self.chain_id = chain_id
        self.url_tx_explorer = url_tx_explorer
        self.name = name

        self.all_configs.append(self)

    @staticmethod
    def check_provider(provider: str) -> tuple[bool, int] | tuple[bool, None]:
        """
        Проверяет доступность провайдера Ethereum и возвращает его идентификатор сети.

        Этот метод выполняет POST-запрос к указанному провайдеру с целью получения его идентификатора сети (chain ID).
        Возвращает кортеж, содержащий статус доступности провайдера и его идентификатор сети, если доступен.

        Args:
            provider (str): URL-адрес провайдера для проверки доступности и получения идентификатора сети.

        Returns:
            tuple[bool, int | None]: Кортеж, где первый элемент - булево значение, указывающее на доступность провайдера.
                                     Второй элемент - целочисленный идентификатор сети, если провайдер доступен и идентификатор сети
                                     успешно получен, в противном случае - None.
        """
        data = '{"jsonrpc":"2.0","method":"net_version","params":[],"id":1}'

        try:
            response = requests.post(url=provider, data=data)
            if response.status_code == 200:
                try:
                    chain_id = int(response.json()['result'])
                    return True, chain_id
                except:
                    return True, None
            else:
                return False, None
        except:
            return False, None


ethereum_holesky_config = ContractConfig(
    name='Ethereum Holesky',
    provider='https://ethereum-holesky.blockpi.network/v1/rpc/public',
    url_abi='https://api-holesky.etherscan.io/api?module=contract&action=getabi&address=',
    chain_id=17000,
    url_tx_explorer='https://holesky.etherscan.io/tx/'
)

ethereum_goerli_config = ContractConfig(
    name='Ethereum Goerli',
    provider='https://sepolia.infura.io/v3/0d6408dc0e754ca884f3b60a54de3228',
    url_abi='https://api-goerli.etherscan.io/api?module=contract&action=getabi&address=',
    chain_id=5,
    url_tx_explorer='https://goerli.etherscan.io/tx/'
)

ethereum_sepolia_config = ContractConfig(
    name='Ethereum Sepolia',
    provider='https://sepolia.infura.io/v3/0d6408dc0e754ca884f3b60a54de3228',
    url_abi='https://api-sepolia.etherscan.io/api?module=contract&action=getabi&address=',
    chain_id=11155111,
    url_tx_explorer='https://sepolia.etherscan.io/tx/'
)

bsc_testnet_config = ContractConfig(
    name='BSC Testnet',
    provider='https://bsc-testnet.nodereal.io/v1/8f87841ec0744b58800f17e1832bee38',
    url_abi='https://api-testnet.bscscan.com/api?module=contract&action=getabi&address=',
    chain_id=97,
    url_tx_explorer='https://testnet.bscscan.com/tx/'
)

shibarium_puppy_config = ContractConfig(
    name='Shibarium Puppy',
    provider='https://puppynet.shibrpc.com',
    chain_id=157,
    url_tx_explorer='https://puppyscan.shib.io/tx/'
)

base_sepolia_config = ContractConfig(
    name='Base Sepolia',
    provider='https://sepolia.base.org',
    url_abi='https://api-sepolia.basescan.org/api?module=contract&action=getabi&address=',
    chain_id=84532,
    url_tx_explorer='https://sepolia.basescan.org/tx/'
)

polygon_mumbai_config = ContractConfig(
    name='Polygon Mumbai',
    provider='https://polygon-mumbai.infura.io/v3/0d6408dc0e754ca884f3b60a54de3228',
    url_abi='https://api-testnet.polygonscan.com/api?module=contract&action=getabi&address=',
    chain_id=80001,
    url_tx_explorer='https://mumbai.polygonscan.com/tx/'
)

ethereum_config = ContractConfig(
    name='Ethereum Mainnet',
    provider='https://eth.llamarpc.com',
    url_abi='https://api.etherscan.io/api?module=contract&action=getabi&address=',
    chain_id=1,
    url_tx_explorer='https://etherscan.io/tx/'
)

okx_testnet = ContractConfig(
    name='OKX Testnet',
    provider='https://xlayertestrpc.okx.com',
    chain_id=195,
    url_tx_explorer='https://www.okx.com/web3/explorer/xlayer-test/tx/'
)

haven1_devnet = ContractConfig(
    name='Haven1 Devnet',
    provider='https://rpc.staging.haven1.org',
    chain_id=8110,
    url_tx_explorer='https://explorer.staging.haven1.org/tx/'
)

haustnetwork_devnet = ContractConfig(
    name='haustnetwork-devnet',
    provider='https://haustnetwork-devnet-rpc.eu-north-2.gateway.fm',
    chain_id=2079172751,
    url_tx_explorer='https://haustnetwork-devnet-blockscout.eu-north-2.gateway.fm:443/'
)