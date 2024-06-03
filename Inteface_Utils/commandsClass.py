class Command:
    all_command = []

    def __init__(self, data):
        self.name = data['name']
        self.after_name = data['after_name']
        self.function = data['function']
        self.arguments = Arguments.init_args(data['arguments'])
        self.description = data['description']

        self.all_command.append(self)

    @classmethod
    def init_commands(cls, data):
        for command in data:
            cls(command)


class Arguments:
    def __init__(self, data):
        self.name = data['name']
        self.after_name = data['after_name']
        self.is_input = data['is_input']
        self.type = data['type']
        self.description = data['description']

    @classmethod
    def init_args(cls, data):
        arguments = []
        for arg in data:
            arguments.append(cls(arg))

        return arguments


commands_data = [
    {
        'name': 'help',
        'after_name': '-h',
        'function': 'help_command',
        'arguments': [],
        'description': 'Справка'
    },
    {
        'name': 'init',
        'after_name': '-i',
        'function': 'init_command',
        'arguments': [
            {
                'name': '--network',
                'after_name': '-n',
                'is_input': True,
                'type': int,
                'description': '(chain_id) Аргумент для указания chain_id сети'
            },
            {
                'name': '--contract',
                'after_name': '-c',
                'is_input': True,
                'type': str,
                'description': '(contract_address) Аргумент для указания адреса контракта'
            },
            {
                'name': '--path_abi',
                'after_name': '-pa',
                'is_input': True,
                'type': str,
                'description': '(path_abi, optional) Аргумент для указания пути к файлу с abi'
            }
        ],
        'description': 'Метод инициализации объекта web3'
    },
    {
        'name': 'read',
        'after_name': '-r',
        'function': 'read_method_command',
        'arguments': [
            {
                'name': '--method',
                'after_name': '-m',
                'is_input': True,
                'type': [str, int],
                'description': '(mid or method_name) Метод контракта'
            },
            {
                'name': '--args',
                'after_name': '-a',
                'is_input': True,
                'type': list,
                'description': '(список аргументов, optional) Аргументы метода'
            }
        ],
        'description': 'Функция для методов чтения контракт'
    },
    {
        'name': 'command_story',
        'after_name': '-cs',
        'function': 'command_story_command',
        'arguments': [
            {
                'name': '--doubles',
                'after_name': '-d',
                'is_input': False,
                'type': None,
                'description': 'Отображает дубли команд'
            }
        ],
        'description': 'Функция выводит историю команд с аргументами'
    }
]


Command.init_commands(commands_data)








