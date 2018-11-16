from rassh.managers.expect_commands import ExpectCommands
from rassh.datatypes import Grammar
from rassh.commands.ssh_bonaire_api_status import SSHBonaireAPIStatus
from rassh.commands.queue import Queue
from rassh.commands.ssh_bonaire_aps import SSHBonaireAPs
from rassh.commands.ssh_bonaire_lms_switches import SSHBonaireLMSSwitches
from rassh.commands.ssh_bonaire_lms_switch_ip import SSHBonaireLMSSwitchIP
from rassh.commands.ssh_bonaire_name import SSHBonaireName
from rassh.commands.ssh_bonaire_group import SSHBonaireGroup
from rassh.commands.ssh_bonaire_ble import SSHBonaireBLE
from rassh.commands.ssh_bonaire_psk import SSHBonairePSK
from rassh.commands.ssh_bonaire_essid import SSHBonaireESSID
from rassh.commands.ssh_bonaire_group_and_gains_and_rap import SSHBonaireGroupAndGainsAndRap
from rassh.commands.ssh_bonaire_group_and_gains import SSHBonaireGroupAndGains
from rassh.commands.ssh_bonaire_group_and_rap import SSHBonaireGroupAndRap
from rassh.commands.ssh_bonaire_cancel import SSHBonaireCancel

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BonaireSSHCommands(ExpectCommands):

    def _my_grammar(self) -> Grammar:
        grammar = Grammar()
        grammar.object_type_to_key_name = {'ap': 'ap_wiredmac',
                                           'ssid_profile': 'ssid_profile_name',
                                           #'controller': 'controller_ip',
                                           'status': 'api_id',
                                           'queue': 'id'}
        return grammar

    def _get_supported_commands(self):
        """ Lots of different 'group' type commands are provided here for convenience.

        For example, you don't want to run put_group and then wait for the ap to reboot before running put_gains, so
        when you need to regroup and set gains use put_group_and_gains in a single call to set both at once."""
        logger.info("Adding commands for Bonaire API")
        self.supported_commands.append(SSHBonaireAPIStatus(self.expect_manager))
        self.supported_commands.append(Queue(self.expect_manager))
        self.supported_commands.append(SSHBonaireAPs(self.expect_manager))
        self.supported_commands.append(SSHBonaireBLE(self.expect_manager))
        self.supported_commands.append(SSHBonaireCancel(self.expect_manager))
        self.supported_commands.append(SSHBonaireESSID(self.expect_manager))
        self.supported_commands.append(SSHBonaireName(self.expect_manager))
        self.supported_commands.append(SSHBonaireGroup(self.expect_manager))
        self.supported_commands.append(SSHBonaireGroupAndGains(self.expect_manager))
        self.supported_commands.append(SSHBonaireGroupAndGainsAndRap(self.expect_manager))
        self.supported_commands.append(SSHBonaireGroupAndRap(self.expect_manager))
        self.supported_commands.append(SSHBonaireLMSSwitchIP(self.expect_manager))
        self.supported_commands.append(SSHBonaireLMSSwitches(self.expect_manager))
        self.supported_commands.append(SSHBonairePSK(self.expect_manager))
