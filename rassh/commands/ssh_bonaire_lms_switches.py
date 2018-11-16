import re
from rassh.commands.ssh_bonaire_command_base import SSHBonaireCommandBase
from rassh.datatypes.well_formed_command import WellFormedCommand


class SSHBonaireLMSSwitches(SSHBonaireCommandBase):

    def __init__(self, expect_manager):
        SSHBonaireCommandBase.__init__(self, expect_manager)
        self.object_type = 'ap'
        self.command_name = 'lms_switches'
        self.payload = []
        self.default = True
        self.no_target = True

    def run_get_command(self, cmd: WellFormedCommand):
        return self.run_get_command_without_args()

    def run_get_command_without_args(self):
        numeric = re.compile('[0-9]+')
        switches = []
        lines = self.expect_command(self.ssh_manager.master_controller, "show switches | include up",
                                    WellFormedCommand(request='{"command": "get_lms_switches", "object_type": "ap"}',
                                                   grammar=self.ssh_manager.commands.grammar))

        for line in lines:
            if numeric.match(line):
                parts = line.split()
                ip = parts[0]
                switches.append(ip)

        return switches, 200

    def run_put_command(self, cmd: WellFormedCommand):
        # Not implemented by the host system.
        return "Not implemented.", 501
