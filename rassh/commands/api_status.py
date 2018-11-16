from rassh.commands.command_base import CommandBase
from rassh.datatypes.well_formed_command import WellFormedCommand


class APIStatus(CommandBase):
    def __init__(self, expect_manager):
        CommandBase.__init__(self, expect_manager)
        self.object_type = 'status'
        self.command_name = 'status'
        self.payload = ['api', ]
        self.default = True
        self.no_target = True

    def run_get_command(self, cmd: WellFormedCommand):
        return "Ready", 200

    def run_put_command(self, cmd: WellFormedCommand):
        # Not implemented by the host system.
        return "Not implemented.", 501
