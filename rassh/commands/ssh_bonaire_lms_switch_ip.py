from rassh.commands.ssh_bonaire_command_base import SSHBonaireCommandBase
from rassh.datatypes.well_formed_command import WellFormedCommand
from rassh.commands import bonaire_functions


class SSHBonaireLMSSwitchIP(SSHBonaireCommandBase):

    def __init__(self, expect_manager):
        SSHBonaireCommandBase.__init__(self, expect_manager)
        self.object_type = 'ap'
        self.command_name = 'lms_switch_ip'
        self.payload = ['switch_ip', ]

    def run_get_command(self, cmd: WellFormedCommand):
        lms, _ = bonaire_functions.get_lms_ip_and_ap_status(self, cmd.request_dict['target'], cmd)
        return lms, 200

    def run_put_command(self, cmd: WellFormedCommand):
        # TODO - Not yet implemented, is it even possible?
        return "Not implemented.", 501
