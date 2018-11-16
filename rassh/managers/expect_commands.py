from rassh.datatypes import Grammar

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExpectCommands(object):
    """This is in a separate class to ExpectManager because we want to be able to access the (auto-generated) Grammar
    without instantiating an ExpectManager object (for example, when starting a feedback API on the application server).
    That's important because an ExpectManager would try and start up expect connections, which we don't want if we just
    need to read the Grammar. The intention is to be able to compose and read the grammar in a lightweight way."""

    def __init__(self, expect_manager):
        self.expect_manager = expect_manager
        self.grammar = self._my_grammar()
        self.supported_commands = []
        self._get_supported_commands()
        for command in self.supported_commands:
            self.grammar.parameters[command.command_name] = {'object_type': command.object_type,
                                                             'payload': command.payload}

            if hasattr(command, 'default'):
                if command.default:
                    self.grammar.parameters[command.command_name]['default'] = True
                else:
                    self.grammar.parameters[command.command_name]['default'] = False
            else:
                self.grammar.parameters[command.command_name]['default'] = False

            if hasattr(command, 'no_target'):
                if command.no_target:
                    self.grammar.parameters[command.command_name]['no_target'] = True
                else:
                    self.grammar.parameters[command.command_name]['no_target'] = False
            else:
                self.grammar.parameters[command.command_name]['no_target'] = False

            if self.grammar.parameters[command.command_name]['default']:
                if self.grammar.parameters[command.command_name]['no_target']:
                    if self.grammar.parameters[command.command_name]['object_type']:
                        url = self.grammar.parameters[command.command_name]['object_type'] + '/'
                    else:
                        url = ''
                else:
                    if self.grammar.parameters[command.command_name]['object_type']:
                        url = self.grammar.parameters[command.command_name]['object_type'] + '/<target>/'
                    else:
                        url = '<target>'
            else:
                if self.grammar.parameters[command.command_name]['no_target']:
                    if self.grammar.parameters[command.command_name]['object_type']:
                        url = self.grammar.parameters[command.command_name]['object_type'] + '/'\
                                   + command.command_name
                    else:
                        url = command.command_name
                else:
                    if self.grammar.parameters[command.command_name]['object_type']:
                        url = self.grammar.parameters[command.command_name]['object_type'] + '/<target>/'\
                              + command.command_name
                    else:
                        url = '<target>/' + command.command_name
            self.grammar.parameters[command.command_name]['url'] = url

    def _my_grammar(self) -> Grammar:
        grammar = Grammar()
        grammar.object_type_to_key_name = {}
        return grammar

    def _get_supported_commands(self):
        """Commands added here will be recognised and automatically added when generating the grammar, and will also be
        used for processing requests."""
        logger.info("Default unconfigured API, not adding any commands!")
        pass
