from reportClass import TestRun
from Web3_Utils import UserWallet

class TestrunScenario:
    test_methods_config = [
        {"name": "Mint Tokens", "description": "Testing mint function", "key": "test_mint", "run": False},
        {"name": "Mint Single Argument", "description": "Testing mint function with a single argument", "key": "test_mint_single_arg", "run": False},
        {"name": "Transfer Tokens", "description": "Testing transfer function", "key": "test_transfer", "run": False},
        {"name": "Approve", "description": "Testing approve function", "key": "test_approve", "run": False},
        {"name": "Burn", "description": "Testing burn function", "key": "test_burn", "run": False},
        {"name": "Transfer From", "description": "Testing transferFrom function", "key": "test_transfer_from", "run": False},
        {"name": "Burn From", "description": "Testing burnFrom function", "key": "test_burn_from", "run": False}
    ]

    def __init__(self, web3_utils, data):
        self.web3_obj = web3_utils
        self.owner = UserWallet.generate_user_from_private_key(data["wallets"]["owner_key"], "owner")
        self.user1 = UserWallet.generate_user_from_private_key(data["wallets"]["user1_key"], "user1")
        self.user2 = UserWallet.generate_user_from_private_key(data["wallets"]["user2_key"], "user2")
        self.testrun_report = TestRun('Тестирование смартконтракта')
        self.run_cases = data['cases']

    def test_mint(self):
        testcase = self.testrun_report.add_test_case('Mint', 'Тестирование функции mint токена')

        amount = 1 * 10 ** self.web3_obj.read_method('decimals')
        before_balance_owner = self.web3_obj.read_method('balanceOf', self.owner.public_key)
        before_balance_user1 = self.web3_obj.read_method('balanceOf', self.user1.public_key)
        before_totalSupply = self.web3_obj.read_method('totalSupply')

        tx_hash_owner = self.web3_obj.send_transaction('mint', self.owner.public_key, amount, user_wallet=self.owner)
        testcase.add_transaction(tx_hash=tx_hash_owner, description="Минтинг овнером себе", web3_utils=self.web3_obj)
        self.web3_obj.wait_transaction_receipt(tx_hash_owner)

        after_balance_owner = self.web3_obj.read_method('balanceOf', self.owner.public_key)
        step = testcase.add_step(name='Проверка увеличения баланса владельца',
                                 description='Минтинг токенов владельцем себе')
        expected_balance_owner = before_balance_owner + amount
        step.set_results(expected_balance_owner, after_balance_owner)

        tx_hash_user1 = self.web3_obj.send_transaction('mint', self.user1.public_key, amount, user_wallet=self.owner)
        testcase.add_transaction(tx_hash=tx_hash_user1, description="Минтинг овнером пользователю User1",
                                 web3_utils=self.web3_obj)
        self.web3_obj.wait_transaction_receipt(tx_hash_user1)

        after_balance_user1 = self.web3_obj.read_method('balanceOf', self.user1.public_key)
        step = testcase.add_step(name='Проверка увеличения баланса пользователя User1',
                                 description='Минтинг токенов владельцем пользователю User1')
        expected_balance_user1 = before_balance_user1 + amount
        step.set_results(expected_balance_user1, after_balance_user1)

        after_totalSupply = self.web3_obj.read_method('totalSupply')
        step = testcase.add_step(name='Проверка увеличения общего предложения токенов',
                                 description='Проверка общего предложения токенов после минтинга')
        expected_totalSupply = before_totalSupply + amount * 2
        step.set_results(expected_totalSupply, after_totalSupply)

        testcase.set_result()

    def test_mint_single_arg(self):
        testcase = self.testrun_report.add_test_case('MintSingleArg', 'Тестирование функции mint с одним аргументом amount')

        amount = 1 * 10 ** self.web3_obj.read_method('decimals')

        before_balance_owner = self.web3_obj.read_method('balanceOf', self.owner.public_key)
        before_totalSupply = self.web3_obj.read_method('totalSupply')

        # В этом случае предполагаем, что метод mint модифицирован для поддержки одного аргумента (amount)
        tx_hash = self.web3_obj.send_transaction('mint', amount, user_wallet=self.owner)
        testcase.add_transaction(tx_hash=tx_hash, description="Минтинг токенов владельцем", web3_utils=self.web3_obj)
        self.web3_obj.wait_transaction_receipt(tx_hash)

        after_balance_owner = self.web3_obj.read_method('balanceOf', self.owner.public_key)
        after_totalSupply = self.web3_obj.read_method('totalSupply')

        step = testcase.add_step(name='Проверка увеличения баланса владельца', description='Минтинг токенов владельцем')
        expected_balance_owner = before_balance_owner + amount
        step.set_results(expected_balance_owner, after_balance_owner)

        step = testcase.add_step(name='Проверка увеличения общего предложения токенов',
                                 description='Проверка общего предложения токенов после минтинга')
        expected_totalSupply = before_totalSupply + amount
        step.set_results(expected_totalSupply, after_totalSupply)

        testcase.set_result()

    def test_transfer(self):
        testcase = self.testrun_report.add_test_case('Transfer', 'Тестирование функции transfer токенов')

        # Устанавливаем количество токенов для передачи
        amount = 1 * 10 ** self.web3_obj.read_method('decimals')

        # Запоминаем начальные балансы отправителя и получателя
        before_balance_owner = self.web3_obj.read_method('balanceOf', self.owner.public_key)
        before_balance_user1 = self.web3_obj.read_method('balanceOf', self.user1.public_key)

        # Выполняем передачу токенов от owner к user1
        tx_hash = self.web3_obj.send_transaction('transfer', self.user1.public_key, amount, user_wallet=self.owner)
        testcase.add_transaction(tx_hash=tx_hash, description="Передача токенов от Owner к User1", web3_utils=self.web3_obj)
        self.web3_obj.wait_transaction_receipt(tx_hash)

        # Проверяем изменение балансов после передачи
        after_balance_owner = self.web3_obj.read_method('balanceOf', self.owner.public_key)
        after_balance_user1 = self.web3_obj.read_method('balanceOf', self.user1.public_key)

        # Добавляем шаги в тест-кейс для проверки результата передачи
        step = testcase.add_step(name='Проверка уменьшения баланса отправителя', description='Баланс Owner должен уменьшиться на amount')
        expected_balance_owner = before_balance_owner - amount
        step.set_results(expected_balance_owner, after_balance_owner)

        step = testcase.add_step(name='Проверка увеличения баланса получателя', description='Баланс User1 должен увеличиться на amount')
        expected_balance_user1 = before_balance_user1 + amount
        step.set_results(expected_balance_user1, after_balance_user1)

        # Устанавливаем итоговый результат тест-кейса на основе результатов шагов
        testcase.set_result()

    def test_approve(self):
        testcase = self.testrun_report.add_test_case('Approve', 'Тестирование функции approve контракта токенов')

        # Определяем количество токенов для теста
        amount = 1 * 10 ** self.web3_obj.read_method('decimals')

        # Получаем текущее разрешение для user1 от owner
        current_allowance = self.web3_obj.read_method('allowance', self.owner.public_key, self.user1.public_key)

        # Устанавливаем новое разрешение: текущее разрешение + 1 токен
        new_allowance = current_allowance + amount
        tx_hash_approve = self.web3_obj.send_transaction('approve', self.user1.public_key, new_allowance, user_wallet=self.owner)
        testcase.add_transaction(tx_hash=tx_hash_approve, description="Установка нового разрешения для User1", web3_utils=self.web3_obj)
        self.web3_obj.wait_transaction_receipt(tx_hash_approve)

        # Проверяем, что разрешение успешно установлено
        updated_allowance = self.web3_obj.read_method('allowance', self.owner.public_key, self.user1.public_key)
        step = testcase.add_step(name='Проверка установки нового разрешения', description='Разрешение должно быть увеличено')
        step.set_results(new_allowance, updated_allowance)

        # Обнуляем разрешение
        tx_hash_revoke = self.web3_obj.send_transaction('approve', self.user1.public_key, 0, user_wallet=self.owner)
        testcase.add_transaction(tx_hash=tx_hash_revoke, description="Обнуление разрешения для User1", web3_utils=self.web3_obj)
        self.web3_obj.wait_transaction_receipt(tx_hash_revoke)

        # Проверяем, что разрешение успешно обнулено
        final_allowance = self.web3_obj.read_method('allowance', self.owner.public_key, self.user1.public_key)
        step = testcase.add_step(name='Проверка обнуления разрешения', description='Разрешение должно быть обнулено')
        step.set_results(0, final_allowance)

        # Устанавливаем итоговый результат тест-кейса на основе результатов шагов
        testcase.set_result()

    def test_burn(self):
        testcase = self.testrun_report.add_test_case('Burn', 'Тестирование функции burn контракта токенов')

        # Устанавливаем количество токенов для сжигания
        amount = 1 * 10 ** self.web3_obj.read_method('decimals')

        # Получаем начальный баланс owner
        before_balance_owner = self.web3_obj.read_method('balanceOf', self.owner.public_key)

        # Если начальный баланс меньше 1 токена, выполняем минтинг на 1 токен
        if before_balance_owner < amount:
            tx_hash_mint = self.web3_obj.send_transaction('mint', self.owner.public_key, amount, user_wallet=self.owner)
            testcase.add_transaction(tx_hash=tx_hash_mint, description="Увеличение баланса Owner", web3_utils=self.web3_obj)
            self.web3_obj.wait_transaction_receipt(tx_hash_mint)

        # Запрашиваем обновленный баланс owner и общее предложение токенов
        before_balance_owner = self.web3_obj.read_method('balanceOf', self.owner.public_key)
        before_totalSupply = self.web3_obj.read_method('totalSupply')

        # Выполняем сжигание токенов
        tx_hash_burn = self.web3_obj.send_transaction('burn', amount, user_wallet=self.owner)
        testcase.add_transaction(tx_hash=tx_hash_burn, description="Сжигание токенов Owner", web3_utils=self.web3_obj)
        self.web3_obj.wait_transaction_receipt(tx_hash_burn)

        # Получаем конечный баланс owner и общее предложение токенов после сжигания
        after_balance_owner = self.web3_obj.read_method('balanceOf', self.owner.public_key)
        after_totalSupply = self.web3_obj.read_method('totalSupply')

        # Добавляем шаги в тест-кейс для проверки результата сжигания
        step = testcase.add_step(name='Проверка уменьшения баланса owner', description='Баланс Owner должен уменьшиться на amount')
        step.set_results(before_balance_owner - amount, after_balance_owner)

        step = testcase.add_step(name='Проверка уменьшения общего предложения токенов', description='Общее предложение токенов должно уменьшиться на amount')
        step.set_results(before_totalSupply - amount, after_totalSupply)

        # Устанавливаем итоговый результат тест-кейса
        testcase.set_result()

    def test_transfer_from(self):
        testcase = self.testrun_report.add_test_case('TransferFrom', 'Тестирование функции transferFrom контракта токенов')

        # Устанавливаем количество токенов для передачи
        amount = 1 * 10 ** self.web3_obj.read_method('decimals')

        # Проверка и обновление allowance, если это необходимо
        current_allowance = self.web3_obj.read_method('allowance', self.owner.public_key, self.user1.public_key)
        if current_allowance < amount:
            tx_hash_approve = self.web3_obj.send_transaction('approve', self.user1.public_key, amount, user_wallet=self.owner)
            testcase.add_transaction(tx_hash=tx_hash_approve, description="Установка разрешения для User1 на передачу токенов", web3_utils=self.web3_obj)
            self.web3_obj.wait_transaction_receipt(tx_hash_approve)

        # Проверка и обновление баланса owner, если это необходимо
        before_balance_owner = self.web3_obj.read_method('balanceOf', self.owner.public_key)
        if before_balance_owner < amount:
            tx_hash_mint = self.web3_obj.send_transaction('mint', self.owner.public_key, amount, user_wallet=self.owner)
            testcase.add_transaction(tx_hash=tx_hash_mint, description="Увеличение баланса Owner для теста", web3_utils=self.web3_obj)
            self.web3_obj.wait_transaction_receipt(tx_hash_mint)

        # Выполнение transferFrom от owner к user2 через user1
        tx_hash_transfer_from = self.web3_obj.send_transaction('transferFrom', self.owner.public_key, self.user2.public_key, amount, user_wallet=self.user1)
        testcase.add_transaction(tx_hash=tx_hash_transfer_from, description="Передача токенов от Owner к User2 через User1", web3_utils=self.web3_obj)
        self.web3_obj.wait_transaction_receipt(tx_hash_transfer_from)

        # Проверка изменений балансов после перевода
        after_balance_owner = self.web3_obj.read_method('balanceOf', self.owner.public_key)
        after_balance_user2 = self.web3_obj.read_method('balanceOf', self.user2.public_key)

        step = testcase.add_step(name='Проверка уменьшения баланса owner', description='Баланс Owner должен уменьшиться на amount')
        step.set_results(before_balance_owner - amount, after_balance_owner)

        step = testcase.add_step(name='Проверка увеличения баланса User2', description='Баланс User2 должен увеличиться на amount')
        step.set_results(0 + amount, after_balance_user2)  # Предполагаем, что до теста у User2 не было токенов

        # Устанавливаем итоговый результат тест-кейса
        testcase.set_result()

    def test_burn_from(self):
        testcase = self.testrun_report.add_test_case('BurnFrom', 'Тестирование функции burnFrom контракта токенов')

        amount = 1 * 10 ** self.web3_obj.read_method('decimals')
        before_totalSupply = self.web3_obj.read_method('totalSupply')

        # Проверка и обновление allowance, если это необходимо
        current_allowance = self.web3_obj.read_method('allowance', self.owner.public_key, self.user1.public_key)
        if current_allowance < amount:
            tx_hash_approve = self.web3_obj.send_transaction('approve', self.user1.public_key, amount, user_wallet=self.owner)
            testcase.add_transaction(tx_hash=tx_hash_approve, description="Установка разрешения для User1 на сжигание", web3_utils=self.web3_obj)
            self.web3_obj.wait_transaction_receipt(tx_hash_approve)

        # Проверка и обновление баланса owner, если это необходимо
        before_balance_owner = self.web3_obj.read_method('balanceOf', self.owner.public_key)
        if before_balance_owner < amount:
            tx_hash_mint = self.web3_obj.send_transaction('mint', self.owner.public_key, amount, user_wallet=self.owner)
            testcase.add_transaction(tx_hash=tx_hash_mint, description="Минтинг токенов владельцу для теста сжигания", web3_utils=self.web3_obj)
            self.web3_obj.wait_transaction_receipt(tx_hash_mint)

        # Сжигание токенов с баланса owner через user1
        tx_hash_burn_from = self.web3_obj.send_transaction('burnFrom', self.owner.public_key, amount, user_wallet=self.user1)
        testcase.add_transaction(tx_hash=tx_hash_burn_from, description="Сжигание токенов с баланса Owner через User1", web3_utils=self.web3_obj)
        self.web3_obj.wait_transaction_receipt(tx_hash_burn_from)

        # Проверка изменения баланса owner и общего предложения токенов
        after_balance_owner = self.web3_obj.read_method('balanceOf', self.owner.public_key)
        after_totalSupply = self.web3_obj.read_method('totalSupply')

        step = testcase.add_step(name='Проверка уменьшения баланса owner', description='Баланс Owner должен уменьшиться на amount')
        step.set_results(before_balance_owner - amount, after_balance_owner)

        step = testcase.add_step(name='Проверка уменьшения общего предложения токенов', description='Общее предложение токенов должно уменьшиться на amount')
        step.set_results(before_totalSupply - amount, after_totalSupply)

        # Установка итогового результата тест-кейса
        testcase.set_result()

    def run_tests(self):
        """
        Запускает тестовые методы на основе конфигурации test_methods_config.
        """
        for test_method in self.run_cases:
            if test_method['run']:
                print(f"Running: {test_method['name']}")
                try:
                    test_method_func = getattr(self, test_method['key'])
                    test_method_func()
                except AttributeError as e:
                    print(f"Error: Method {test_method['key']} not found in TestunScenario class.")
            else:
                print(f"Skipping: {test_method['name']}")
