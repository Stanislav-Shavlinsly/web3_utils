import os
import logging
import json
from colorama import Fore, Style, init

init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """
    Класс для форматирования логов с использованием цветного вывода.

    Методы:
    format(record):
        Форматирует сообщение лога, добавляя цвет в зависимости от уровня лога и содержания сообщения.
    """

    def format(self, record):
        """
        Форматирует запись лога, добавляя цвет в зависимости от уровня лога и содержания сообщения.

        Параметры:
        record (logging.LogRecord): Запись лога, которую нужно форматировать.

        Возвращаемое значение:
        str: Отформатированное сообщение лога.
        """
        level_color = {
            logging.DEBUG: Fore.BLUE,
            logging.INFO: Fore.WHITE,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.MAGENTA,
        }
        levelname = record.levelname
        if record.levelno in level_color:
            levelname_color = level_color[record.levelno] + levelname + Style.RESET_ALL
        else:
            levelname_color = levelname

        if record.levelno == logging.ERROR:
            record.msg = Fore.RED + record.msg + Style.RESET_ALL
        elif record.levelno == logging.WARNING:
            record.msg = Fore.YELLOW + record.msg + Style.RESET_ALL
        elif record.levelno == logging.INFO:
            record.msg = Fore.WHITE + record.msg + Style.RESET_ALL

        if 'arguments:' in record.msg:
            parts = record.msg.split('arguments:')
            arguments = parts[1]
            record.msg = parts[0] + 'arguments:' + Fore.YELLOW + arguments + Style.RESET_ALL

        if 'returned a single value:' in record.msg:
            parts = record.msg.split('returned a single value:')
            returned_value = parts[1]
            record.msg = parts[0] + 'returned a single value:' + Fore.YELLOW + returned_value + Style.RESET_ALL

        lines = record.msg.split('\n')
        for i in range(len(lines)):
            if 'Struct' in lines[i]:
                continue
            if ': ' in lines[i]:
                key_value = lines[i].split(': ', 1)
                key = key_value[0]
                value = ': '.join(key_value[1:])
                lines[i] = f"{key}: {Fore.YELLOW}{value}{Style.RESET_ALL}"
        record.msg = '\n'.join(lines)

        record.levelname = levelname_color
        return super(ColoredFormatter, self).format(record)


logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
original_print = print


def colored_print(*args, **kwargs):
    """
    Выводит текст в консоль с использованием желтого цвета для аргументов.

    Параметры:
    *args: Аргументы, которые нужно вывести.
    **kwargs: Дополнительные аргументы, передаваемые в функцию print.

    Логика:
    1. Формирует список colored_args, в котором каждый аргумент оборачивается в желтый цвет с использованием Fore.YELLOW и сбрасывается стиль с помощью Style.RESET_ALL.
    2. Вызывает оригинальную функцию print с измененными аргументами colored_args и дополнительными параметрами kwargs.
    3. Переопределяет стандартную функцию print функцией colored_print для вывода текста в цвете.
    """
    colored_args = [Fore.YELLOW + str(arg) + Style.RESET_ALL for arg in args]
    original_print(*colored_args, **kwargs)


print = colored_print


def clear_console():
    """
    Очищает консоль, в зависимости от операционной системы.

    Логика:
    1. Определяет операционную систему:
       - Если операционная система Windows ('nt'), выполняет команду 'cls' для очистки консоли.
       - Если операционная система не Windows, выполняет команду 'clear' для очистки консоли.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def get_abi_outputs(method_name, abi_path):
    """
    Получает описания выходных параметров метода из ABI смарт-контракта, включая обработку компонентов кортежей.

    Параметры:
    method_name (str): Название метода смарт-контракта, для которого необходимо получить выходные параметры.
    abi_path (str): Путь к файлу ABI смарт-контракта.

    Возвращаемое значение:
    list: Список кортежей, содержащих имя и тип выходного параметра. Если параметр является кортежем,
          то возвращается список компонентов внутри кортежа с их именами и типами.

    Логика:
    1. Открывает файл ABI по указанному пути.
    2. Загружает содержимое ABI в формате JSON.
    3. Перебирает функции в ABI:
       - Если имя функции совпадает с заданным методом и у функции есть выходные параметры:
         - Инициализирует пустой список для выходных параметров.
         - Перебирает выходные параметры функции:
           - Если тип параметра начинается с 'tuple':
             - Инициализирует пустой список для компонентов кортежа.
             - Перебирает компоненты кортежа и добавляет их в список компонентов.
             - Добавляет кортеж (имя параметра или 'param{index}', список компонентов) в список выходных параметров.
           - Иначе добавляет кортеж (имя параметра или 'param{index}', тип параметра) в список выходных параметров.
         - Возвращает список выходных параметров.
    4. Если метод не найден или не имеет выходных параметров, возвращает пустой список.
    """
    with open(abi_path, 'r') as abi_file:
        abi = json.load(abi_file)
        for func in abi:
            if func.get('name') == method_name and func.get('outputs'):
                outputs = []
                for index, output in enumerate(func['outputs']):
                    if output['type'].startswith('tuple'):
                        components = []
                        for component in output['components']:
                            components.append({'name': component['name'], 'type': component['type']})
                        outputs.append((output.get('name', f"param{index}"), components))
                    else:
                        outputs.append((output.get('name', f"param{index}"), output['type']))
                return outputs
    return []


def safe_read_method(web3_obj, method_name, *args):
    """
    Безопасно выполняет чтение данных из блокчейна с использованием метода смарт-контракта и возвращает результат.

    Параметры:
    web3_obj (Web3): Объект Web3 для взаимодействия с блокчейном.
    method_name (str): Название метода смарт-контракта, который нужно вызвать.
    *args: Аргументы, необходимые для вызова метода смарт-контракта.

    Возвращаемое значение:
    Любое значение, возвращаемое методом смарт-контракта, если вызов был успешен.
    None: В случае ошибки при вызове метода.

    Логика:
    1. Пытается выполнить метод чтения данных с использованием метода read_method объекта web3_obj:
       - Передает метод и аргументы.
       - Получает результат выполнения метода, если вызов успешен.
    2. Если метод вызван успешно:
       - Логгирует успешное выполнение метода.
       - Возвращает результат.
    3. В случае возникновения исключения:
       - Логгирует ошибку с описанием проблемы.
       - Возвращает None.
    """
    try:
        result = web3_obj.read_method(method_name, *args)
        logging.info(f"Method {method_name} executed successfully.")
        return result
    except Exception as e:
        logging.error(f"Error when calling method {method_name}: {str(e)}")
        return None


def safe_write_method(web3_obj, wallet_address, private_key, method_name, *args):
    """
    Безопасно выполняет запись данных в блокчейн с использованием метода смарт-контракта и возвращает хеш транзакции.

    Параметры:
    web3_obj (Web3): Объект Web3 для взаимодействия с блокчейном.
    wallet_address (str): Адрес кошелька, с которого будет выполняться транзакция.
    private_key (str): Приватный ключ для подписи транзакции.
    method_name (str): Название метода смарт-контракта, который нужно вызвать.
    *args: Аргументы, необходимые для вызова метода смарт-контракта.

    Возвращаемое значение:
    str: Хеш транзакции, если транзакция была успешно отправлена.
    None: В случае ошибки при отправке транзакции.

    Логика:
    1. Формирует строку с информацией о параметрах, если они есть, иначе указывает "No arguments".
    2. Пытается отправить транзакцию с использованием метода send_transaction объекта web3_obj:
       - Передает метод, аргументы, адрес кошелька и приватный ключ.
       - Получает хеш транзакции, если отправка успешна.
    3. Если хеш транзакции получен:
       - Логгирует успешную отправку транзакции с указанием метода и параметров.
    4. Если хеш транзакции не получен:
       - Логгирует предупреждение о неудачной отправке транзакции.
    5. Возвращает хеш транзакции или None в случае ошибки.
    6. В случае возникновения исключения:
       - Логгирует ошибку с описанием проблемы.
       - Возвращает None.
    """
    try:
        param_info = ", ".join(f"{arg}" for arg in args) if args else "No arguments"
        tx_hash = web3_obj.send_transaction(method_name, *args, wallet_address=wallet_address, private_key=private_key)
        if tx_hash:
            logging.info(f"Transaction {method_name} ({param_info}) initiated with tx_hash: {tx_hash}")
        else:
            logging.warning(f"Failed to send transaction for method {method_name}")
        return tx_hash
    except Exception as e:
        logging.error(f"Error when sending transaction for method {method_name}: {str(e)}")
        return None


def wait_for_transaction_receipt(web3_obj, tx_hash):
    """
    Ожидает завершения транзакции и логгирует её результат.

    Параметры:
    web3_obj (Web3): Объект Web3 для взаимодействия с блокчейном.
    tx_hash (str): Хеш транзакции, за которой необходимо следить.

    Возвращаемое значение:
    None

    Логика:
    1. Логгирует сообщение о том, что начинается ожидание майнинга транзакции.
    2. Использует метод wait_transaction_receipt объекта web3_obj для ожидания завершения транзакции и получения квитанции.
    3. Если транзакция была успешно обработана (receipt.status == 1):
       - Логгирует успешное завершение транзакции.
    4. Если транзакция завершилась неудачно (receipt.status == 0):
       - Логгирует ошибку завершения транзакции.
    """
    logger.info(f"Waiting for transaction {tx_hash} to be mined...")
    receipt = web3_obj.wait_transaction_receipt(tx_hash)
    if receipt.status:
        logger.info(f"Transaction {tx_hash} was successfully mined.")
    else:
        logger.error(f"Transaction {tx_hash} failed.")


def detailed_log_results(method_name, result, abi_path):
    """
    Логгирует детальные результаты выполнения метода смарт-контракта, сравнивая их с ожидаемыми значениями из ABI.

    Параметры:
    method_name (str): Название метода смарт-контракта, который был вызван.
    result: Результат выполнения метода смарт-контракта.
    abi_path (str): Путь к файлу ABI смарт-контракта.

    Возвращаемое значение:
    None

    Логика:
    1. Получает параметры вывода для метода из ABI с помощью функции get_abi_outputs.
    2. Если результат является списком или кортежем:
       a. Если параметров вывода один и он является списком (проверка на наличие структур):
          - Определяет ожидаемую длину структуры.
          - Логгирует каждую структуру, проверяя соответствие длины ожидаемой.
          - Если длина структуры не совпадает с ожидаемой, логгирует ошибку.
          - Логгирует параметры и их значения внутри структуры.
       b. Если параметров вывода один и результат является списком:
          - Логгирует результат как единый список.
       c. Если количество параметров вывода не совпадает с количеством значений в результате:
          - Логгирует ошибку о несоответствии количества значений.
       d. Иначе:
          - Логгирует каждый параметр и его значение по отдельности.
    3. Если результат не является списком или кортежем:
       a. Если параметров вывода один:
          - Логгирует единственный результат.
       b. Иначе:
          - Логгирует ошибку о несоответствии количества значений.
    """
    output_params = get_abi_outputs(method_name, abi_path)

    if isinstance(result, (list, tuple)):
        if len(output_params) == 1 and isinstance(output_params[0][1], list):  # Проверка на наличие структур
            expected_length = len(output_params[0][1])
            for struct_index, struct in enumerate(result):
                if len(struct) != expected_length:
                    logging.error(
                        f"Struct {struct_index} in method {method_name} returned unexpected number of values: {len(struct)}. Expected: {expected_length}")
                else:
                    logging.info(f"Struct {struct_index}:")
                    for param, value in zip(output_params[0][1], struct):
                        logging.info(f"  {param['name']}: {value}")
        else:
            if len(output_params) == 1 and isinstance(result, list):
                logging.info(f"{output_params[0][0]}: {result}")
            else:
                if len(output_params) != len(result):
                    logging.error(
                        f"Method {method_name} returned unexpected number of values: {len(result)}. Expected: {len(output_params)}")
                else:
                    for param, value in zip(output_params, result):
                        logging.info(f"{param[0]}: {value}")
    else:
        if len(output_params) == 1:
            logging.info(f"{output_params[0][0]}: {result}")
        else:
            logging.error(
                f"Method {method_name} returned a single value, but expected multiple values: {len(output_params)}")


def read(web3_obj, method_name, *args):
    """
    Выполняет чтение данных из блокчейна с использованием заданного метода смарт-контракта.

    Параметры:
    web3_obj (Web3): Объект Web3 для взаимодействия с блокчейном.
    method_name (str): Название метода смарт-контракта, который нужно вызвать.
    *args: Аргументы, необходимые для вызова метода смарт-контракта.

    Возвращаемое значение:
    Любое значение, возвращаемое методом смарт-контракта.

    Логика:
    1. Выводит в консоль пустую строку.
    2. Логгирует запуск метода чтения с указанием его имени и аргументов.
    3. Вызывает функцию safe_read_method для выполнения чтения данных и получения результата.
    4. Логгирует подробные результаты выполнения метода с использованием detailed_log_results.
    5. Возвращает результат, полученный от safe_read_method.
    """
    print()
    logging.info(f"Running method: {method_name} with arguments: {args}")
    result = safe_read_method(web3_obj, method_name, *args)
    detailed_log_results(method_name, result, web3_obj.path_abi)
    return result


def write(web3_obj, wallet_address, private_key, method_name, *args):
    """
    Выполняет запись данных в блокчейн с использованием заданного метода смарт-контракта.

    Параметры:
    web3_obj (Web3): Объект Web3 для взаимодействия с блокчейном.
    wallet_address (str): Адрес кошелька, с которого будет выполняться транзакция.
    private_key (str): Приватный ключ для подписи транзакции.
    method_name (str): Название метода смарт-контракта, который нужно вызвать.
    *args: Аргументы, необходимые для вызова метода смарт-контракта.

    Возвращаемое значение:
    None

    Логика:
    1. Выводит в консоль пустую строку.
    2. Логгирует запуск метода записи с указанием его имени и аргументов.
    3. Вызывает функцию safe_write_method для выполнения транзакции и получения хеша транзакции.
    4. Если хеш транзакции получен:
       - Логгирует успешное выполнение метода записи и ожидание завершения транзакции.
       - Вызывает функцию wait_for_transaction_receipt для ожидания подтверждения транзакции.
    5. Если хеш транзакции не получен:
       - Логгирует ошибку выполнения метода записи.
    """
    print()
    logging.info(f"Running write method: {method_name} with arguments: {args}")
    tx_hash = safe_write_method(web3_obj, wallet_address, private_key, method_name, *args)
    if tx_hash:
        logging.info(f"Write method {method_name} executed. Waiting for completion.")
        wait_for_transaction_receipt(web3_obj, tx_hash)
    else:
        logging.error(f"Failed to execute write method {method_name}")
