"""Calling this regularly will have the effect of keeping the SSH connections alive."""
from rassh.commands.expect_command_base import ExpectCommandBase
from rassh.datatypes.well_formed_command import WellFormedCommand
from rassh.exceptions.exception_with_status import ExceptionWithStatus


class SSHBonaireAPIStatus(ExpectCommandBase):
    def __init__(self, expect_manager):
        ExpectCommandBase.__init__(self, expect_manager)
        self.object_type = 'status'
        self.command_name = 'status'
        self.payload = ['api', ]
        self.default = True
        self.no_target = True

    def run_get_command(self, cmd: WellFormedCommand):
        output = {}
        result = "Ok"
        try:
            _ = self.expect_command(self.ssh_manager.master_controller, "end", cmd)
            _ = self.expect_command(self.ssh_manager.master_controller, "end", cmd)
        except ExceptionWithStatus:
            result = "Error"
        output['Master'] = {}
        output['Master'][self.ssh_manager.master_controller] = result
        output['LMS'] = {}
        for switch in self.ssh_manager.switches:
            result = "Ok"
            try:
                _ = self.expect_command(switch, "end", cmd)
                _ = self.expect_command(switch, "end", cmd)
            except ExceptionWithStatus:
                result = "Error"
            output['LMS'][switch] = result
        return output, 200

    def run_put_command(self, cmd: WellFormedCommand):
        # Not implemented by the host system.
        return "Not implemented.", 501
