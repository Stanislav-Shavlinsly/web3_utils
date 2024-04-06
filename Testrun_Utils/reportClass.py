from enum import Enum, auto
from Web3_Utils.classWeb3Utils import Web3Utils
import json


class TestResult(Enum):
    TOTAL_FAILURE = auto()
    PARTIAL_FAILURE = auto()
    SUCCESS = auto()
    NOT_REPRODUCIBLE = auto()


class TestStep:
    def __init__(self, name, description, expected_result=None, actual_result=None, result=None):
        self.name = name
        self.description = description
        self.expected_result = expected_result
        self.actual_result = actual_result
        self.result: TestResult | None = result

    # Метод для установки фактического результата и результата шага
    def set_results(self, expected_result, actual_result):
        self.expected_result = expected_result
        self.actual_result = actual_result

        # Автоматическая установка результата на основе сравнения ожидаемого и фактического
        if self.expected_result == self.actual_result:
            self.result = TestResult.SUCCESS
        else:
            self.result = TestResult.TOTAL_FAILURE


class TestCase:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.steps = []
        self.transactions = []
        self.result: TestResult | None = None

    def add_step(self, name, description):
        teststep = TestStep(name, description)
        self.steps.append(teststep)
        return teststep

    def add_transaction(self, tx_hash: str, description: str, web3_utils: Web3Utils):
        tx_url = web3_utils.give_url_tx(tx_hash)
        tx_status = web3_utils.get_transaction_status(tx_hash)
        self.transactions.append({"url": tx_url, "description": description, 'tx_status': tx_status})

    def set_result(self):
        count = 0
        for step in self.steps:
            if step.result == TestResult.SUCCESS:
                count += 1

        if count == len(self.steps):
            self.result = TestResult.SUCCESS
        elif 0 < count < len(self.steps):
            self.result = TestResult.PARTIAL_FAILURE
        elif count == 0:
            self.result = TestResult.TOTAL_FAILURE


from datetime import datetime


class TestRun:
    def __init__(self, description, date_time=None):
        self.description = description
        self.date_time = date_time if date_time else datetime.now()
        self.test_cases = []
        self.result = {
            'success': 0,
            'partial_failures': 0,
            'total_failures': 0,
            'not_reproducible': 0
        }

    def add_test_case(self, name, description):
        testcase = TestCase(name, description)
        self.test_cases.append(testcase)
        return testcase

    def calculate_results(self):
        for case in self.test_cases:
            if case.result == TestResult.SUCCESS:
                self.result['success'] += 1
            elif case.result == TestResult.PARTIAL_FAILURE:
                self.result['partial_failures'] += 1
            elif case.result == TestResult.TOTAL_FAILURE:
                self.result['total_failures'] += 1
            elif self.result == TestResult.NOT_REPRODUCIBLE:
                self.result['not_reproducible'] += 1

    def view_results(self):
        print(f"Отчет по тест-рану: {self.description}")
        print(f"Дата и время выполнения: {self.date_time.strftime('%Y-%m-%d %H:%M:%S')}")
        for case in self.test_cases:
            print(f"\nТест-кейс: {case.name} - {case.description}")
            print(f"Результат тест-кейса: {case.result.name if case.result else 'Не определен'}")
            for step in case.steps:
                print(f"    Шаг: {step.name} - {step.description}")
                print(f"    Ожидаемый результат: {step.expected_result}")
                print(f"    Фактический результат: {step.actual_result}")
                print(f"    Результат шага: {step.result.name if step.result else 'Не определен'}")
            if case.transactions:
                print("Список транзакций:")
            for tx in case.transactions:
                print(f"    Транзакция: {tx['description']}")
                print(f"    URL: {tx['url']}")
        print("\nИтоговая статистика:")
        for key, value in self.result.items():
            print(f"{key.replace('_', ' ').capitalize()}: {value}")

    def save_json(self):
        """
        Сохраняет отчет о тестировании в формате JSON, используя английские ключи.
        """
        report_data = {
            "testRunDescription": self.description,
            "dateTime": self.date_time.strftime('%Y-%m-%d %H:%M:%S'),
            "testCases": []
        }

        for case in self.test_cases:
            case_data = {
                "testCaseName": case.name,
                "description": case.description,
                "steps": [],
                "transactions": [],
                "result": case.result.name if case.result else "Undefined"
            }

            for step in case.steps:
                step_data = {
                    "stepName": step.name,
                    "description": step.description,
                    "expectedResult": step.expected_result,
                    "actualResult": step.actual_result,
                    "result": step.result.name if step.result else "Undefined"
                }
                case_data["steps"].append(step_data)

            for tx in case.transactions:
                tx_data = {
                    "transactionDescription": tx['description'],
                    "url": tx['url']
                }
                case_data["transactions"].append(tx_data)

            report_data["testCases"].append(case_data)

        report_data["summary"] = self.result

        with open("test_report.json", "w", encoding="utf-8") as json_file:
            json.dump(report_data, json_file, ensure_ascii=False, indent=4)

        return report_data
