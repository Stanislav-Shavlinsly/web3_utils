from config import *
from classWeb3Utils import *
from userClass import *
import time

web3_test = Web3Utils(shibarium_puppy_config,
                      contract_address='0x845e4145F7de2822d16FE233Ecd0181c61f1d65F',
                      path_abi='exemple_abi.txt') # Путь до файла с аби
print(web3_test.read_method('totalSupply'))






web3_test2 = Web3Utils(ethereum_sepolia_config, contract_address='0x8101FFFCF909c7B8CC3B6b42B9dd45CD38104Bd2')

user1 = UserWallet('0x34829AFe060AF59569225b009caCd1184cE0510a', '0x8248a4ff875b032ae2f4b2f5f46a18a8a346642112e2407a3dc261814724aed3', 'user1')
user2 = UserWallet('0x9a7d7f2136fA9f134bb2168b95a819c476D14Ca4', '0xe986cec6444ec32843153502cf94267a2ecd9e8e429fbddd40f96d7105253cad', 'user2')

decimals = web3_test2.read_method('decimals')
amount = 1 * 10 ** decimals

tx_hash = web3_test2.send_transaction('approve', user2.public_key, amount, user_wallet=user1) # Проводим транзакцию
web3_test2.wait_transaction_receipt(tx_hash) # Ждём пока транзакция запишется в блокчейн
allowance = web3_test2.read_method('allowance', user1.public_key, user2.public_key) # Теперь можем проверять изменения в блокчейне


# Создание нового кошелька
new_wallet = UserWallet.generate_ethereum_wallet()
print(new_wallet.__dict__)

# Отправка нативной валюты
public_key = '0xA9a78a9840C0972D3620855D692735f86eFE97Db'
private_key = '0xefebf0aa55ba97ab0694ea541b1cf64079dc0d01d5d348ed0b9c32a6e6d0f3f5'
user = UserWallet(public_key, private_key)

web3_test = Web3Utils(ethereum_sepolia_config)
tx_hash = web3_test.send_native_currency('0xE05085117ce04E6E0798fA5737752d16476EDe20', value=1, user_wallet=user)
# Вывод урла на транзакцию
print(web3_test.give_url_tx(tx_hash))