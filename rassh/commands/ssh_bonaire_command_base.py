from abc import abstractmethod
from rassh.datatypes.well_formed_command import WellFormedCommand
from rassh.commands.expect_command_base import ExpectCommandBase
from rassh.exceptions.exception_with_status import ExceptionWithStatus


class SSHBonaireCommandBase(ExpectCommandBase):
    """This is the command processing class for the Bonaire API. It includes a small sanity measure, namely an attempt
    to exit back to the "enable" (base) state by running 'end' twice before running any further command. Of course,
    we should *be* in the 'enable' state anyway, if all previous commands have behaved themselves. Better safe than
    sorry, running 'end' twice is pretty much a free operation here, and has no effect unless we were in a bad state."""

    def request_command(self, cmd: WellFormedCommand):
        """Run this SSH command only when matching this request"""
        if cmd.part_name is not None and self.command_name == cmd.part_name:
            try:
                # This is the sanity measure mentioned in the docstring.
                _ = self.expect_command(self.ssh_manager.master_controller, "end", cmd)
                _ = self.expect_command(self.ssh_manager.master_controller, "end", cmd)
                return self.request_command_by_type(cmd)
            except ExceptionWithStatus as e:
                return e.message, e.status
        # "We return None values here to show that this command did not match, and the next command should be tried.
        return None, None

    @abstractmethod
    def run_get_command(self, cmd: WellFormedCommand) -> (object, int):
        # Returns response, http_status
        return None, None

    @abstractmethod
    def run_put_command(self, cmd: WellFormedCommand) -> (str, int):
        # Returns response, http_status
        return None, None
