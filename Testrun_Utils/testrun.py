from Web3_Utils.config import *
from Web3_Utils.userClass import *
from Testrun_Utils.reportClass import *

address = '0x8101FFFCF909c7B8CC3B6b42B9dd45CD38104Bd2'

web3_obj = Web3Utils(ethereum_sepolia_config, address)

owner = UserWallet('0x828FaAb125BE76c8F9d3D551F86a052Bdf28A209',
                   '0xc0824ba28eeacae062fb21ba9951b088f68f1f899cd2c214546ac41b83670a2a',
                   'owner')

user1 = UserWallet('0x34829AFe060AF59569225b009caCd1184cE0510a',
                   '0x8248a4ff875b032ae2f4b2f5f46a18a8a346642112e2407a3dc261814724aed3',
                   'user1')

user2 = UserWallet('0x9a7d7f2136fA9f134bb2168b95a819c476D14Ca4',
                   '0xe986cec6444ec32843153502cf94267a2ecd9e8e429fbddd40f96d7105253cad',
                   'user2')


def test_mint(testrun: TestRun):
    testcase = testrun.add_test_case('Mint', 'Тестирование функции mint токена')

    amount = 1 * 10 ** web3_obj.read_method('decimals')
    before_balance_owner = web3_obj.read_method('balanceOf', owner.public_key)
    before_balance_user1 = web3_obj.read_method('balanceOf', user1.public_key)
    before_totalSupply = web3_obj.read_method('totalSupply')

    tx_hash_owner = web3_obj.send_transaction('mint', owner.public_key, amount, user_wallet=owner)
    testcase.add_transaction(tx_hash=tx_hash_owner, description="Минтинг овнером себе", web3_utils=web3_obj)
    web3_obj.wait_transaction_receipt(tx_hash_owner)

    after_balance_owner = web3_obj.read_method('balanceOf', owner.public_key)
    step = testcase.add_step(name='Проверка увеличения баланса владельца',
                             description='Минтинг токенов владельцем себе')
    expected_balance_owner = before_balance_owner + amount
    step.set_results(expected_balance_owner, after_balance_owner)

    tx_hash_user1 = web3_obj.send_transaction('mint', user1.public_key, amount, user_wallet=owner)
    testcase.add_transaction(tx_hash=tx_hash_user1, description="Минтинг овнером пользователю User1",
                             web3_utils=web3_obj)
    web3_obj.wait_transaction_receipt(tx_hash_user1)

    after_balance_user1 = web3_obj.read_method('balanceOf', user1.public_key)
    step = testcase.add_step(name='Проверка увеличения баланса пользователя User1',
                             description='Минтинг токенов владельцем пользователю User1')
    expected_balance_user1 = before_balance_user1 + amount
    step.set_results(expected_balance_user1, after_balance_user1)

    after_totalSupply = web3_obj.read_method('totalSupply')
    step = testcase.add_step(name='Проверка увеличения общего предложения токенов',
                             description='Проверка общего предложения токенов после минтинга')
    expected_totalSupply = before_totalSupply + amount * 2
    step.set_results(expected_totalSupply, after_totalSupply)

    testcase.set_result()


def test_mint_single_arg(testrun: TestRun):
    testcase = testrun.add_test_case('MintSingleArg', 'Тестирование функции mint с одним аргументом amount')

    amount = 1 * 10 ** web3_obj.read_method('decimals')

    before_balance_owner = web3_obj.read_method('balanceOf', owner.public_key)
    before_totalSupply = web3_obj.read_method('totalSupply')

    tx_hash = web3_obj.send_transaction('mint', amount, user_wallet=owner)
    testcase.add_transaction(tx_hash=tx_hash, description="Минтинг токенов владельцем", web3_utils=web3_obj)
    web3_obj.wait_transaction_receipt(tx_hash)

    after_balance_owner = web3_obj.read_method('balanceOf', owner.public_key)
    after_totalSupply = web3_obj.read_method('totalSupply')

    step = testcase.add_step(name='Проверка увеличения баланса владельца', description='Минтинг токенов владельцем')
    expected_balance_owner = before_balance_owner + amount
    step.set_results(expected_balance_owner, after_balance_owner)

    step = testcase.add_step(name='Проверка увеличения общего предложения токенов',
                             description='Проверка общего предложения токенов после минтинга')
    expected_totalSupply = before_totalSupply + amount
    step.set_results(expected_totalSupply, after_totalSupply)

    testcase.set_result()


def test_transfer(testrun: TestRun):
    testcase = testrun.add_test_case('Transfer', 'Тестирование функции transfer токенов')

    # Устанавливаем количество токенов для передачи
    amount = 1 * 10 ** web3_obj.read_method('decimals')

    # Запоминаем начальные балансы отправителя и получателя
    before_balance_owner = web3_obj.read_method('balanceOf', owner.public_key)
    before_balance_user1 = web3_obj.read_method('balanceOf', user1.public_key)

    # Выполняем передачу токенов от owner к user1
    tx_hash = web3_obj.send_transaction('transfer', user1.public_key, amount, user_wallet=owner)
    testcase.add_transaction(tx_hash=tx_hash, description="Передача токенов от Owner к User1", web3_utils=web3_obj)
    web3_obj.wait_transaction_receipt(tx_hash)

    # Проверяем изменение балансов после передачи
    after_balance_owner = web3_obj.read_method('balanceOf', owner.public_key)
    after_balance_user1 = web3_obj.read_method('balanceOf', user1.public_key)

    # Добавляем шаги в тест-кейс для проверки результата передачи
    step = testcase.add_step(name='Проверка уменьшения баланса отправителя',
                             description='Баланс Owner должен уменьшиться на amount')
    expected_balance_owner = before_balance_owner - amount
    step.set_results(expected_balance_owner, after_balance_owner)

    step = testcase.add_step(name='Проверка увеличения баланса получателя',
                             description='Баланс User1 должен увеличиться на amount')
    expected_balance_user1 = before_balance_user1 + amount
    step.set_results(expected_balance_user1, after_balance_user1)

    # Устанавливаем итоговый результат тест-кейса на основе результатов шагов
    testcase.set_result()


def test_approve(testrun: TestRun):
    testcase = testrun.add_test_case('Approve', 'Тестирование функции approve контракта токенов')

    # Определяем количество токенов для теста
    amount = 1 * 10 ** web3_obj.read_method('decimals')

    # Получаем текущее разрешение для user1 от owner
    current_allowance = web3_obj.read_method('allowance', owner.public_key, user1.public_key)

    # Устанавливаем новое разрешение: текущее разрешение + 1 токен
    new_allowance = current_allowance + amount
    tx_hash_approve = web3_obj.send_transaction('approve', user1.public_key, new_allowance, user_wallet=owner)
    testcase.add_transaction(tx_hash=tx_hash_approve, description="Установка нового разрешения для User1",
                             web3_utils=web3_obj)
    web3_obj.wait_transaction_receipt(tx_hash_approve)

    # Проверяем, что разрешение успешно установлено
    updated_allowance = web3_obj.read_method('allowance', owner.public_key, user1.public_key)
    step = testcase.add_step(name='Проверка установки нового разрешения',
                             description='Разрешение должно быть увеличено')
    step.set_results(new_allowance, updated_allowance)

    # Обнуляем разрешение
    tx_hash_revoke = web3_obj.send_transaction('approve', user1.public_key, 0, user_wallet=owner)
    testcase.add_transaction(tx_hash=tx_hash_revoke, description="Обнуление разрешения для User1", web3_utils=web3_obj)
    web3_obj.wait_transaction_receipt(tx_hash_revoke)

    # Проверяем, что разрешение успешно обнулено
    final_allowance = web3_obj.read_method('allowance', owner.public_key, user1.public_key)
    step = testcase.add_step(name='Проверка обнуления разрешения', description='Разрешение должно быть обнулено')
    step.set_results(0, final_allowance)

    # Устанавливаем итоговый результат тест-кейса на основе результатов шагов
    testcase.set_result()


def test_burn(testrun: TestRun):
    testcase = testrun.add_test_case('Burn', 'Тестирование функции burn контракта токенов')

    amount = 1 * 10 ** web3_obj.read_method('decimals')

    # Получаем начальный баланс owner
    before_balance_owner = web3_obj.read_method('balanceOf', owner.public_key)

    # Если начальный баланс меньше 1 токена, выполняем минтинг на 1 токен
    if before_balance_owner < amount:
        tx_hash_mint = web3_obj.send_transaction('mint', owner.public_key, amount, user_wallet=owner)
        testcase.add_transaction(tx_hash=tx_hash_mint, description="Увелечение баланса Owner",
                                 web3_utils=web3_obj)
        web3_obj.wait_transaction_receipt(tx_hash_mint)

    # Запрашиваем обновленный баланс owner и общее предложение токенов
    before_balance_owner = web3_obj.read_method('balanceOf', owner.public_key)
    before_totalSupply = web3_obj.read_method('totalSupply')

    # Выполняем сжигание токенов
    tx_hash_burn = web3_obj.send_transaction('burn', amount, user_wallet=owner)
    testcase.add_transaction(tx_hash=tx_hash_burn, description="Сжигание токенов owner", web3_utils=web3_obj)
    web3_obj.wait_transaction_receipt(tx_hash_burn)

    # Получаем конечный баланс owner и общее предложение токенов после сжигания
    after_balance_owner = web3_obj.read_method('balanceOf', owner.public_key)
    after_totalSupply = web3_obj.read_method('totalSupply')

    # Добавляем шаги в тест-кейс для проверки результата сжигания
    step = testcase.add_step(name='Проверка уменьшения баланса owner',
                             description='Баланс Owner должен уменьшиться на amount')
    step.set_results(before_balance_owner - amount, after_balance_owner)

    step = testcase.add_step(name='Проверка уменьшения общего предложения токенов',
                             description='Общее предложение токенов должно уменьшиться на amount')
    step.set_results(before_totalSupply - amount, after_totalSupply)

    # Устанавливаем итоговый результат тест-кейса
    testcase.set_result()


def test_transfer_from(testrun: TestRun):
    testcase = testrun.add_test_case('TransferFrom', 'Тестирование функции transferFrom контракта токенов')

    amount = 1 * 10 ** web3_obj.read_method('decimals')

    # Проверка и обновление allowance, если это необходимо
    current_allowance = web3_obj.read_method('allowance', owner.public_key, user1.public_key)
    if current_allowance < amount:
        tx_hash_approve = web3_obj.send_transaction('approve', user1.public_key, amount, user_wallet=owner)
        testcase.add_transaction(tx_hash=tx_hash_approve, description="Установка разрешения для User1",
                                 web3_utils=web3_obj)
        web3_obj.wait_transaction_receipt(tx_hash_approve)

    # Проверка и обновление баланса owner, если это необходимо
    before_balance_owner = web3_obj.read_method('balanceOf', owner.public_key)
    if before_balance_owner < amount:
        tx_hash_mint = web3_obj.send_transaction('mint', owner.public_key, amount, user_wallet=owner)
        testcase.add_transaction(tx_hash=tx_hash_mint, description="Увелечение баланса Owner",
                                 web3_utils=web3_obj)
        web3_obj.wait_transaction_receipt(tx_hash_mint)

    # Выполнение transferFrom от owner к user2 через user1
    tx_hash_transfer_from = web3_obj.send_transaction('transferFrom', owner.public_key, user2.public_key, amount,
                                                      user_wallet=user1)
    testcase.add_transaction(tx_hash=tx_hash_transfer_from, description="Передача токенов от Owner к User2 через User1",
                             web3_utils=web3_obj)
    web3_obj.wait_transaction_receipt(tx_hash_transfer_from)

    # Проверка изменений балансов после перевода
    after_balance_owner = web3_obj.read_method('balanceOf', owner.public_key)
    after_balance_user2 = web3_obj.read_method('balanceOf', user2.public_key)

    step = testcase.add_step(name='Проверка уменьшения баланса owner',
                             description='Баланс Owner должен уменьшиться на amount')
    step.set_results(before_balance_owner - amount, after_balance_owner)

    step = testcase.add_step(name='Проверка увеличения баланса User2',
                             description='Баланс User2 должен увеличиться на amount')
    step.set_results(0 + amount, after_balance_user2)  # Предполагаем, что до теста у User2 не было токенов

    # Устанавливаем итоговый результат тест-кейса
    testcase.set_result()

def test_burn_from(testrun: TestRun):
    testcase = testrun.add_test_case('BurnFrom', 'Тестирование функции burnFrom контракта токенов')

    amount = 1 * 10 ** web3_obj.read_method('decimals')
    before_totalSupply = web3_obj.read_method('totalSupply')

    # Проверка и обновление allowance, если необходимо
    current_allowance = web3_obj.read_method('allowance', owner.public_key, user1.public_key)
    if current_allowance < amount:
        tx_hash_approve = web3_obj.send_transaction('approve', user1.public_key, amount, user_wallet=owner)
        testcase.add_transaction(tx_hash=tx_hash_approve, description="Установка разрешения для User1 на сжигание", web3_utils=web3_obj)
        web3_obj.wait_transaction_receipt(tx_hash_approve)

    # Проверка и обновление баланса owner, если необходимо
    before_balance_owner = web3_obj.read_method('balanceOf', owner.public_key)
    if before_balance_owner < amount:
        tx_hash_mint = web3_obj.send_transaction('mint', owner.public_key, amount, user_wallet=owner)
        testcase.add_transaction(tx_hash=tx_hash_mint, description="Минтинг токенов владельцу для теста сжигания", web3_utils=web3_obj)
        web3_obj.wait_transaction_receipt(tx_hash_mint)

    # Сжигание токенов с баланса owner через user1
    tx_hash_burn_from = web3_obj.send_transaction('burnFrom', owner.public_key, amount, user_wallet=user1)
    testcase.add_transaction(tx_hash=tx_hash_burn_from, description="Сжигание токенов с баланса Owner через User1", web3_utils=web3_obj)
    web3_obj.wait_transaction_receipt(tx_hash_burn_from)

    # Проверка изменения баланса owner и общего предложения токенов
    after_balance_owner = web3_obj.read_method('balanceOf', owner.public_key)
    after_totalSupply = web3_obj.read_method('totalSupply')

    step = testcase.add_step(name='Проверка уменьшения баланса owner', description='Баланс Owner должен уменьшиться на amount')
    step.set_results(before_balance_owner - amount, after_balance_owner)

    step = testcase.add_step(name='Проверка уменьшения общего предложения токенов', description='Общее предложение токенов должно уменьшиться на amount')
    step.set_results(before_balance_owner - amount, after_totalSupply)

    # Установка итогового результата тест-кейса
    testcase.set_result()


def testrun_token():
    testrun_report = TestRun('Тестирование токена')

    test_mint(testrun_report)
    test_transfer(testrun_report)
    test_approve(testrun_report)
    test_burn(testrun_report)
    test_transfer_from(testrun_report)
    test_burn_from(testrun_report)

    testrun_report.calculate_results()
    testrun_report.view_results()

    testrun_report.save_json()


testrun_token()
