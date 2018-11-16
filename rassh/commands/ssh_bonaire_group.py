from rassh.commands.ssh_bonaire_command_base import SSHBonaireCommandBase
from rassh.commands import bonaire_functions
from rassh.datatypes.well_formed_command import WellFormedCommand


class SSHBonaireGroup(SSHBonaireCommandBase):
    def __init__(self, expect_manager):
        SSHBonaireCommandBase.__init__(self, expect_manager)
        self.object_type = 'ap'
        self.command_name = 'group'
        self.payload = ['ap_group', ]

    def run_get_command(self, cmd: WellFormedCommand):
        group = bonaire_functions.get_group(self, cmd.request_dict['target'], cmd)
        return group, 200

    def run_put_command(self, cmd: WellFormedCommand):
        length = len(cmd.request_dict['params']['ap_group'])
        if length < 1 or length > 30:
            # I don't know if this is the limit on the Bonaire system, but we enforce this limit in our databases.
            return "Error: group name must be between 1 and 30 characters (check failed).", 400

        # Check that we really need to run this, as it will cause the AP to reboot.
        group = bonaire_functions.get_group(self, cmd.request_dict['target'], cmd)
        if group != cmd.request_dict['params']['ap_group']:
            bonaire_functions.set_group(self, cmd.request_dict['target'], cmd.request_dict['params']['ap_group'], cmd)

        return cmd.request_dict['params']['ap_group'], 204
