﻿from collections import defaultdict

# TODO: Alternatively, simply scan the directory for all modules
COMMAND_MODULES = [
    'account',
    'login',
    'logout',
    'network',
    'resource',
    'storage',
    'vm',
]

COMMON_PARAMETERS = {
    'resource_group_name': {
        'name': '--resourcegroup --rg',
        'metavar': 'RESOURCE GROUP',
        'help': 'Name of resource group',
        'required': True
    },
    'location': {
        'name': '--location -l',
        'metavar': 'LOCATION',
        'help': 'Location',
        'required': True
    }
}


class CommandTable(defaultdict):
    """A command table is a dictionary of func -> {name,
                                                   func,
                                                   **kwargs}
    objects.

    The `name` is the space separated name - i.e. 'az vm list'
    `func` represents the handler for the method, and will be called with the parsed
    args from argparse.ArgumentParser. The remaining keyword arguments will be passed to
    ArgumentParser.add_parser.
    """
    def __init__(self):
        super(CommandTable, self).__init__(lambda: {'options': []})

    def command(self, name, **kwargs):
        def wrapper(func):
            self[func]['name'] = name
            self[func].update(kwargs)
            return func
        return wrapper

    def description(self, description):
        def wrapper(func):
            self[func]['description'] = description
            return func
        return wrapper

    def option(self, name, **kwargs):
        def wrapper(func):
            opt = dict(kwargs)
            opt['name'] = name
            self[func]['options'].append(opt)
            return func
        return wrapper

def get_command_table(command_name):
    module = __import__('azure.cli.commands.' + command_name)
    for part in ('cli.commands.' + command_name).split('.'):
        module = getattr(module, part)

    return module.get_command_table()

def add_to_parser(parser, session, module_name=None):
    '''Loads commands into the parser

    When `module_name` is specified, only commands from that module will be loaded.
    If the module is not found, all commands are loaded.
    '''
    loaded = False
    if module_name:
        try:
            parser.load_command_table(session, get_command_table(module_name))
            loaded = True
        except ImportError:
            # Unknown command - we'll load all below
            pass

    if not loaded:
        for mod in COMMAND_MODULES:
            parser.load_command_table(session, get_command_table(mod))
        loaded = True
