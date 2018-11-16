from abc import ABC, abstractmethod

from rassh.datatypes.well_formed_command import WellFormedCommand
from rassh.managers.expect_manager import ExpectManager
from rassh.exceptions.exception_with_status import ExceptionWithStatus


class CommandBase(ABC):
    """This is the command processing class. Each instance is able to respond to "put" and "get" commands for a
    particular command name. The init method defines some variables used when building the request processing Grammar.
    Most notably, 'object_type' is used to locate key names in the 'object_type_to_key_name' dictionary of the Grammar,
    and 'payload' is used to define required request parameters for "put" commands.

    The entry point here is 'request_command' which is called by the ExpectManager instance when processing each
    request. All of the commands which were added to the instance's ExpectCommands.supported_commands are tried one at a
    time. If the request matches the given command, that command is run and returns a response. Once a response has been
    received, the remaining commands are ignored.

    Commands may optionally time out after a certain interval (configured in RasshConfig). If a command times out here,
    then it should enqueue the request, which will then be retried the next time the request queue runs."""

    def __init__(self, expect_manager: ExpectManager):
        self.ssh_manager = expect_manager
        self.object_type = None
        self.command_name = None
        self.payload = []

    def request_command(self, cmd: WellFormedCommand):
        """Run this expect command only when matching this request"""
        if cmd.part_name is not None and self.command_name == cmd.part_name:
            try:
                return self.request_command_by_type(cmd)
            except ExceptionWithStatus as e:
                return e.message, e.status
        # "We return None values here to show that this command did not match, and the next command should be tried.
        return None, None

    def request_command_by_type(self, cmd: WellFormedCommand):
        try:
            if cmd.command_type == 'get':
                response, http_status = self.run_get_command(cmd)
                return response, http_status
            elif cmd.command_type == 'put':
                response, http_status = self.run_put_command(cmd)
                return response, http_status
            else:
                return "Method not allowed.", 405
        except KeyError:
            return "Malformed request.", 400

    @abstractmethod
    def run_get_command(self, cmd: WellFormedCommand) -> (object, int):
        # Returns response, http_status
        return None, None

    @abstractmethod
    def run_put_command(self, cmd: WellFormedCommand) -> (str, int):
        # Returns response, http_status
        return None, None
