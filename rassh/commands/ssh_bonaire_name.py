from rassh.commands.ssh_bonaire_command_base import SSHBonaireCommandBase
from rassh.commands import bonaire_functions
from rassh.datatypes.well_formed_command import WellFormedCommand


class SSHBonaireName(SSHBonaireCommandBase):
    def __init__(self, expect_manager):
        SSHBonaireCommandBase.__init__(self, expect_manager)
        self.object_type = 'ap'
        self.command_name = 'name'
        self.payload = ['ap_name', ]

    def run_get_command(self, cmd: WellFormedCommand):
        ap_name = bonaire_functions.get_ap_name(self, cmd.request_dict['target'], cmd)
        return ap_name, 200

    def run_put_command(self, cmd: WellFormedCommand):
        # Not implemented by this API. May be possible; future work?
        return "Not implemented by this API.", 501
