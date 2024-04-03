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
