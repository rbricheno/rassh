from pexpect import pxssh, exceptions

from rassh.managers.expect_manager import ExpectManager
from rassh.managers.expect_commands import ExpectCommands
from rassh.managers.bonaire_ssh_commands import BonaireSSHCommands
from rassh.commands.ssh_bonaire_lms_switches import SSHBonaireLMSSwitches

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BonaireSSHManager(ExpectManager):

    @staticmethod
    def get_new_expect_connection(controller_ip):
        try:
            new_ssh_connection = pxssh.pxssh()
            # PROMPT is a regular expression which will match the prompt on the remote system.
            # This matches the Bonaire "Enable" prompt, and the "conf t" prompt.
            new_ssh_connection.PROMPT = "\([a-zA-Z0-9_\-\\\"\s]*\) #"
            new_ssh_connection.login(controller_ip,
                                     BonaireSSHManager.config.get('api_ssh_user'),
                                     BonaireSSHManager.config.get('api_ssh_password'),
                                     auto_prompt_reset=False)
            # Prevent the Bonaire pager from kicking in when running commands with long outputs.
            new_ssh_connection.sendline("no paging")
            if not new_ssh_connection.prompt():
                raise exceptions.TIMEOUT("Prompt timed out!")
            return new_ssh_connection
        except exceptions.EOF as e:
            logger.error("EOF Exception when getting a new SSH connection to " + controller_ip
                         + ". Is the destination host rejecting connections?" +
                         " Was this a login with bad username / password?")
            logger.error(e.get_trace())
            return None
        except exceptions.TIMEOUT as e:
            logger.error("Timeout Exception when getting a new SSH connection to " + controller_ip
                         + ". Is the destination host accessible?")
            logger.error(e.get_trace())
            return None
        except pxssh.ExceptionPxssh as e:
            logger.error("Unknown exception when getting a new SSH connection to " + controller_ip + ".")
            logger.error(e.get_trace())
            return None

    def _my_commands(self) -> ExpectCommands:
        return BonaireSSHCommands(self)

    def _get_managed_children(self):
        ssh_lms_switches = SSHBonaireLMSSwitches(self)
        self.switches, _ = ssh_lms_switches.run_get_command_without_args()
        for switch in self.switches:
            # We already have a connection to the master controller, so don't add that.
            if switch != self.master_controller:
                self.all_expect_connections[switch] = self.get_new_expect_connection(switch)
