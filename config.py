class ContractConfig:
    """
    Класс для хранения конфигурационных данных контракта.

    Attributes:
        provider (str): URL-адрес провайдера для подключения к сети Ethereum.
        url_abi (str): URL-адрес для получения ABI контракта.
        chain_id (int): Идентификатор цепочки блокчейна (chain ID) для сети Ethereum.
    """
    def __init__(self, provider, url_abi, chain_id):
        """
        Инициализирует объект класса ContractConfig.

        Args:
            provider (str): URL-адрес провайдера для подключения к сети Ethereum.
            url_abi (str): URL-адрес для получения ABI контракта.
            chain_id (int): Идентификатор цепочки блокчейна (chain ID) для сети Ethereum.
        """
        self.provider = provider
        self.url_abi = url_abi
        self.chain_id = chain_id


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
