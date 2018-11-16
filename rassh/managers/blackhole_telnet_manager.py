import pexpect
from pexpect import exceptions
import time

from rassh.managers.expect_manager import ExpectManager
from rassh.managers.expect_commands import ExpectCommands
from rassh.managers.blackhole_telnet_commands import BlackholeTelnetCommands

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlackholeTelnetManager(ExpectManager):

    @staticmethod
    def get_new_expect_connection(controller_ip):
        try:
            new_ssh_connection = pexpect.spawn("telnet " + controller_ip)
            # PROMPT is a regular expression which will match the prompt on the remote system.
            # This matches the Bonaire "Enable" prompt, and the "conf t" prompt.
            new_ssh_connection.PROMPT = "\S+#"
            new_ssh_connection.expect(":")
            time.sleep(1)
            new_ssh_connection.sendline(ExpectManager.config['api_ssh_password'] + "\r")
            new_ssh_connection.expect(">")
            time.sleep(1)
            new_ssh_connection.sendline("enable \r")
            new_ssh_connection.expect("#")
            time.sleep(1)
            return new_ssh_connection
        except exceptions.EOF as e:
            logger.error("EOF Exception when getting a new telnet connection." +
                         " Is the destination host rejecting connections?" +
                         " Was this a login with bad username / password?")
            logger.error(e.get_trace())
            return None
        except exceptions.TIMEOUT as e:
            logger.error("Timeout Exception when getting a new telnet connection. Is the destination host accessible?")
            logger.error(e.get_trace())
            return None
        except pexpect.ExceptionPexpect as e:
            logger.error("Unknown exception when getting a new telnet connection.")
            logger.error(e.get_trace())
            return None

    def _my_commands(self) -> ExpectCommands:
        return BlackholeTelnetCommands(self)
