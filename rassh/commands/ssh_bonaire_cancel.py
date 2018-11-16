from rassh.commands.ssh_bonaire_command_base import SSHBonaireCommandBase
from rassh.datatypes.well_formed_command import WellFormedCommand


class SSHBonaireCancel(SSHBonaireCommandBase):
    def __init__(self, expect_manager):
        SSHBonaireCommandBase.__init__(self, expect_manager)
        self.object_type = 'ap'
        self.command_name = 'cancel'
        self.payload = []

    def run_get_command(self, cmd: WellFormedCommand):
        # Can't GET a "cancel" and have something meaningful returned to you.
        return "Not implemented", 501

    def run_put_command(self, cmd: WellFormedCommand):
        _ = self.expect_command(self.ssh_manager.master_controller,
                             "clear gap-db wired-mac " + cmd.request_dict['target'], cmd)

        # It does no harm running both of these, and it is probably required if the AP has been both a RAP and a CAP in
        # its life time.
        _ = self.expect_command(self.ssh_manager.master_controller, "whitelist rap del mac-address "
                                + cmd.request_dict['target'], cmd)

        _ = self.expect_command(self.ssh_manager.master_controller, "whitelist cpsec del mac-address "
                                + cmd.request_dict['target'], cmd)

        return "Cancelled " + cmd.request_dict['target'], 204
