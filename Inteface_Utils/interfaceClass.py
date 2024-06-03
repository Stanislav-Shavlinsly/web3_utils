from Web3_Utils import Web3Utils, UserWallet, config

from Inteface_Utils.commandsClass import Command, Arguments




class CommandContext:
    command_story = []
    def __init__(self):
        self.id = 0 if self.command_story == [] else self.command_story[-1].id + 1
        self.command_name = None
        self.arguments = {}

        self.save_story()

    def save_story(self):
        for command in self.command_story:
            if command.command_name == self.command_name:
                return

        self.command_story.append(self)

    @classmethod
    def list_story(cls, doubles=False):
        answer_command_story = []
        if doubles:
            answer_command_story = cls.command_story
        else:
            for command in cls.command_story:
                if command.arguments == {}:
                    continue

                doubles_command = False
                for answer_command in answer_command_story:
                    if command.command_name == answer_command.command_name and command.arguments == answer_command.arguments:
                        doubles_command = True
                        break
                if not doubles_command:
                    answer_command_story.append(command)

        return answer_command_story


class Interface:
    interface_version = '0.2'

    commands = {
        '-h': 'help',
        'help': 'help',
        '-r': 'read',
        'read': 'read',
        '-i': 'init',
        'init': 'init',
        '-cs': 'command_story',
        'command_story': 'command_story',
        '-w': 'wallets_list',
        'wallets': 'wallets_list',
    }

    arguments = {
        '-n': 'network',
        '--network': 'network',
        '-c': 'contract',
        '--contract': 'contract',
        '-pa': 'path_abi',
        '--path_abi': 'path_abi',
        '-m': 'method',
        '--method': 'method',
        '-a': 'args',
        '--args': 'args',
        '-d': 'doubles',
        '--doubles': 'doubles'
    }

    def __init__(self):
        self.web3 = None
        self.wallets = None
        self.command_context = None

    def run(self):
        print(f'Interface v.{self.interface_version} started')
        command_handlers = {
            '-h': self.help_command,
            'help': self.help_command,
            '-r': self.read_method_command,
            'read': self.read_method_command,
            '-i': self.init_command,
            'init': self.init_command,
            '-cs': self.command_story_command,
            'command_story': self.command_story_command
        }

        while True:
            request_text = input('Enter command_name:\n')
            result = self.parse_text_to_dict(request_text)
            if not result:
                print('Incorrect command_name or input. \n[h], [help]: Справка')
                continue

            handler = command_handlers.get(self.command_context.command_name)
            if handler:
                handler()
            else:
                print('Unknown command_name, type [-h] or [help] for instructions')

    def help_command(self):
        for command in Command.all_command:
            print(f'[{command.name}], [{command.after_name}]: {command.description}')

            for arg in command.arguments:
                print(f'\t[{arg.name}], [{arg.after_name}]: {arg.description}')

            print()

    def read_method_command(self):
        def answer_read_contract(args=None):
            if args is None:
                answer_contract = self.web3.read_method(method['name'])
            else:
                answer_contract = self.web3.read_method(method['name'], *args)
            if len(method['outputs']) == 1:
                if method['outputs'][0]['type'] == 'uint256':
                    print(f'{method["outputs"][0]["name"]}: {answer_contract}    ({round(answer_contract / 10 ** 18, 2)}) [18d]')
                else:
                    print(f'{method["outputs"][0]["name"]}: {answer_contract}')
            else:
                print(f'{answer_contract}')
            return

        if self.web3 is None:
            print('Не заданы конфигурационные методы сети и контракта\n'
                  '')
            return

        method = None
        read_methods = self.web3.list_methods()['read_methods']

        if '-m' in self.command_context.arguments or '--method' in self.command_context.arguments:
            if '-m' in self.command_context.arguments:
                method_name = self.command_context.arguments['-m']
            else:
                method_name = self.command_context.arguments['--method']
        else:
            print('Выберете один из методов контрактов из представленных сетей:\n'
                  f'{"[mid]":5} {"method_name":30} {"(inputs[name: type])":80} {"(outputs[name: type])"}\n')
            method_id = 0

            for read_method in read_methods:
                method_id += 1
                inputs_method = ''
                outputs_method = ''
                for inputs in read_method['inputs']:
                    if inputs_method != '':
                        inputs_method += ', '
                    inputs_method += f"{inputs['name']}: {inputs['type']}"
                for outputs in read_method['outputs']:
                    if outputs_method != '':
                        inputs_method += ', '
                    outputs_method += f"{outputs['name']}: {outputs['type']}"
                print(f'{f"[{method_id}]":5} {read_method["name"]:30} {f"({inputs_method})":80} ({outputs_method})')
            method_name = input('Введите method_name или mid: ')
        if method_name.isdigit():
            method_id = int(method_name)
            method = read_methods[method_id - 1]
        else:
            for read_method in read_methods:
                if read_method['name'] == method_name:
                    method = read_method
                    break

        if method is None:
            print('Incorrect method_name')
            return
        inputs_method = ''
        outputs_method = ''
        for inputs in method['inputs']:
            if inputs_method != '':
                inputs_method += ', '
            inputs_method += f"{inputs['name']}: {inputs['type']}"
        for outputs in method['outputs']:
            if outputs_method != '':
                outputs_method += ', '
            outputs_method += f"{outputs['name']}: {outputs['type']}"
        print(f'{method["name"]}\t\t({inputs_method})\t\t({outputs_method})\n')

        args = None
        if len(method['inputs']) == 0:
            answer_read_contract()
            return

        else:
            if '-a' in self.command_context.arguments or '--args' in self.command_context.arguments:
                if '-a' in self.command_context.arguments:
                    args = self.command_context.arguments['-a']
                else:
                    args = self.command_context.arguments['--args']

                if len(method['inputs']) == 1:
                    if type(args) is not str:
                        print(f'Incorrect argument: inputs in method {len(method["inputs"])}, you entered {len(args)}')
                        return
                    else:
                        args = [args]
                elif len(method['inputs']) > 1:
                    if type(args) is not list:
                        print(f'Incorrect argument: inputs in method {len(method["inputs"])}, you entered 1')
                        return
                    elif len(method['inputs']) != len(args):
                        print(f'Incorrect argument: inputs in method {len(method["inputs"])}, you entered {len(args)}')
                        return

                number_input = 0

                for arg, input_method in zip(args, method['inputs']):
                    if input_method['type'] == 'uint256':
                        if arg.isdigit():
                            arg = int(arg)
                            args[number_input] = arg
                        else:
                            print(f'Incorrect argument {number_input + 1} {input_method["name"]}: uint256')
                            return

                    number_input += 1

                answer_read_contract(args)
                return


            else:
                args = []
                number_input = 0
                for input_method in method['inputs']:

                    arg = input(f'Please enter: {input_method["name"]} ({input_method["type"]}): ')
                    if input_method['type'] == 'uint256':
                        if arg.isdigit():
                            arg = int(arg)
                        else:
                            print(f'Incorrect argument {number_input + 1}: uint256')
                            return
                    args.append(arg)
                    number_input += 1

                answer_read_contract(args)
                return

    def init_command(self):
        network = None

        if '-n' in self.command_context.arguments or '--network' in self.command_context.arguments:
            if '-n' in self.command_context.arguments:
                chain_id = self.command_context.arguments['-n']
            else:
                chain_id = self.command_context.arguments['--network']
        else:
            print('Выберете одну из представленных сетей:\n'
                  '[chain_id] name\n')
            for network_config in config.ContractConfig.all_configs:
                print(f'[{network_config.chain_id}] {network_config.name}')
            chain_id = input('Введите chain_id: ')

        if chain_id.isdigit():
            chain_id = int(chain_id)

        for network_config in config.ContractConfig.all_configs:
            if network_config.chain_id == chain_id:
                network = network_config
                break

        if network is None:
            print('Incorrect chain_id')
            return

        if '-c' in self.command_context.arguments or '--contract' in self.command_context.arguments:
            if '-c' in self.command_context.arguments:
                contract_address = self.command_context.arguments['-c']
            else:
                contract_address = self.command_context.arguments['--contract']
        else:
            contract_address = input('Введите contract_address: ')

        if contract_address is None or len(contract_address) != 42:
            print('Incorrect contract_address')
            return

        if '-pa' in self.command_context.arguments or '--path_abi' in self.command_context.arguments:
            if '-pa' in self.command_context.arguments:
                path_abi = self.command_context.arguments['-pa']
            else:
                path_abi = self.command_context.arguments['--path_abi']
        else:
            path_abi = input('Введите path_abi или пропустите: ')

        self.web3 = Web3Utils(contract_config=network,
                              contract_address=contract_address,
                              path_abi=path_abi)

        print('Web3Utils initialized')

    def command_story_command(self):
        doubles = False
        if '-d' in self.command_context.arguments or '--doubles' in self.command_context.arguments:
            if '-d' in self.command_context.arguments:
                arg = self.command_context.arguments['-d']
            else:
                arg = self.command_context.arguments['--doubles']

            if arg in ['True', 'true', '1']:
                doubles = True

        command_story = CommandContext.list_story(doubles)

        for command in command_story:
            print(f'{f"[{command.id}]":5}'
                  f'{self.commands[command.command_name]}')
            for arg, value in command.arguments.items():
                print(f'\t\t{self.arguments[arg]}   {value}')


    def parse_text_to_dict(self, text):
        try:
            command_context = CommandContext()
            parts = text.split(' ')
            cleaned_parts = [part.strip() for part in parts if part.strip() != '']

            # Первое слово — это команда, не идет в словарь аргументов
            command_context.command_name = cleaned_parts[0]
            cleaned_parts.pop(0)

            dictionary = {}
            key = None
            for part in cleaned_parts:
                if part.startswith('-'):  # Проверяем, является ли часть ключом
                    if key:
                        # Присваиваем предыдущему ключу собранные значения (как строку или список)
                        dictionary[key] = values if len(values.split(',')) == 1 else values.split(',')
                    key = part
                    values = ''
                else:
                    # Собираем значения, относящиеся к ключу
                    values += (',' if values else '') + part

            # Не забываем добавить последний набор данных
            if key and values:
                dictionary[key] = values if len(values.split(',')) == 1 else values.split(',')

            command_context.arguments = dictionary
            print(dictionary)
            self.command_context = command_context
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False


interface = Interface()
interface.run()
