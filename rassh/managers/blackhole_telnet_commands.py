from rassh.managers.expect_commands import ExpectCommands
from rassh.datatypes import Grammar
from rassh.commands.api_status import APIStatus
from rassh.commands.queue import Queue
from rassh.commands.telnet_blackholes import TelnetBlackholes
from rassh.commands.telnet_blackhole import TelnetBlackhole


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlackholeTelnetCommands(ExpectCommands):

    def _my_grammar(self) -> Grammar:
        grammar = Grammar()
        grammar.object_type_to_key_name = {'blackhole': 'cidr_location', #CIDR and location, combined, are a key.
                                           'status': 'api_id',
                                           'queue': 'id'}
        return grammar

    def _get_supported_commands(self):
        logger.info("Adding commands for Blackhole API")
        self.supported_commands.append(APIStatus(self.expect_manager))
        self.supported_commands.append(Queue(self.expect_manager))
        self.supported_commands.append(TelnetBlackholes(self.expect_manager))
        self.supported_commands.append(TelnetBlackhole(self.expect_manager))
