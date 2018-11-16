from rassh.commands.ssh_bonaire_command_base import SSHBonaireCommandBase
from rassh.datatypes import valid_boolean
from rassh.commands import bonaire_functions
from rassh.datatypes.well_formed_command import WellFormedCommand
from rassh.exceptions.exception_with_status import ExceptionWithStatus


class SSHBonaireGroupAndRap(SSHBonaireCommandBase):
    def __init__(self, expect_manager):
        SSHBonaireCommandBase.__init__(self, expect_manager)
        self.object_type = 'ap'
        self.command_name = 'group_and_rap'
        self.payload = ['ap_group', 'remote_ap']

    def run_get_command(self, cmd: WellFormedCommand):
        group = bonaire_functions.get_group(self, cmd.request_dict['target'], cmd)

        try:
            remote_ap = bonaire_functions.get_remote_ap(self, cmd.request_dict['target'], cmd)
        except ExceptionWithStatus as e:
            if e.status == 412:
                return {"group": group, "remote_ap": "Down"}, 206
            elif e.status == 404:
                return {"group": group, "remote_ap": "Error"}, 206
            else:
                raise e

        return {"group": group, "remote_ap": remote_ap}, 200

    def run_put_command(self, cmd: WellFormedCommand):
        length = len(cmd.request_dict['params']['ap_group'])
        if length < 1 or length > 30:
            # I don't know if this is the limit on the Bonaire system, but we enforce this limit in our databases,
            # including in the local sqlite queue database.
            return "Error: group name must be between 1 and 30 characters (check failed).", 400

        try:
            real_remote_ap = valid_boolean(cmd.request_dict['params']['remote_ap'])
        except ValueError:
            return "Error: remote AP must be boolean.", 400

        group = bonaire_functions.get_group(self, cmd.request_dict['target'], cmd)

        try:
            remote_ap = bonaire_functions.get_remote_ap(self, cmd.request_dict['target'], cmd)
            if remote_ap != real_remote_ap:
                bonaire_functions.enter_provisioning_mode(self, cmd)

                bonaire_functions.reprovision_or_enqueue(self, cmd.request, cmd.request_dict['target'], cmd)

                bonaire_functions.reprovision_remote(self, real_remote_ap, cmd)

                _ = self.expect_command(self.ssh_manager.master_controller, "reprovision wired-mac "
                                        + cmd.request_dict['target'], cmd)

                bonaire_functions.end_end(self, cmd)
        except ExceptionWithStatus as e:
            if e.status == 412:
                return {"group": group, "remote_ap": "Down"}, 206
            elif e.status == 404:
                return {"group": group, "remote_ap": "Error"}, 206
            else:
                raise e

        # Regroup last, otherwise provisioning will fail.
        # Check that we really need to run this, as it will cause the AP to reboot.
        if group != cmd.request_dict['params']['ap_group']:
            bonaire_functions.set_group(self, cmd.request_dict['target'], cmd.request_dict['params']['ap_group'], cmd)

        return cmd.request_dict['params']['ap_group'], 204
