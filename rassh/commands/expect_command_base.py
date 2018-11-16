from abc import abstractmethod
import pexpect
from pexpect import exceptions

from typing import Union

from rassh.commands.command_base import CommandBase
from rassh.datatypes.well_formed_command import WellFormedCommand
from rassh.managers.expect_manager import ExpectManager
from rassh.exceptions.exception_with_status import ExceptionWithStatus


class ExpectCommandBase(CommandBase):
    """This is the expect command processing class. It allows commands to be sent over expect connections. If an error
    occurs, 'False' is returned as the first argument indicating that the command failed and the whole request has been
    enqueued (if possible)."""

    def __init__(self, expect_manager: ExpectManager):
        super().__init__(expect_manager)

    def expect_command(self, controller, command, cmd: WellFormedCommand) -> (Union[list, str]):
        connection = self.ssh_manager.all_expect_connections.get(controller)
        if connection:
            try:
                connection.sendline(command)
                # EOF may not be thrown before calling connection.prompt() so it must be included both
                # in the try and the expect block.
                connection.expect(connection.PROMPT)
            except (pexpect.ExceptionPexpect, exceptions.EOF, OSError):
                connection = self.ssh_manager.get_new_expect_connection(controller)
                self.ssh_manager._expect_managers[controller] = connection
                connection.sendline(command)
                connection.expect(connection.PROMPT)
        else:
            try:
                connection = self.ssh_manager.get_new_expect_connection(controller)
                if connection:
                    self.ssh_manager._expect_managers[controller] = connection
                    connection.sendline(command)
                    connection.expect(connection.PROMPT)
                else:
                    if cmd.command_type == "put":
                        enqueue_status = self.ssh_manager.queue.enqueue_request(cmd.request)
                        if enqueue_status:
                            raise ExceptionWithStatus("Request could not be serviced because of an expect "
                                                      + "connection error, command has been enqueued.", 202)
                        else:
                            raise ExceptionWithStatus("Request could not be serviced because of an expect connection"
                                                      + " error "
                                                      + " and command could not be enqueued because of a queue error.",
                                                      500)
                    else:
                        raise ExceptionWithStatus("Request could not be serviced because of an expect connection error,"
                                                  + " please try again later.", 503)
            except (pexpect.ExceptionPexpect, exceptions.EOF, OSError):
                if cmd.command_type == "put":
                    enqueue_status = self.ssh_manager.queue.enqueue_request(cmd.request)
                    if enqueue_status:
                        raise ExceptionWithStatus("Request could not be serviced because of an expect "
                                                  + "connection error, command has been enqueued.", 202)
                    else:
                        raise ExceptionWithStatus("Request could not be serviced because of an expect connection error"
                                                  + " and command could not be enqueued because of a queue error.",
                                                  500)
                else:
                    raise ExceptionWithStatus("Request could not be serviced because of an expect connection error,"
                                          + " please try again later.", 503)
        try:
            return str(connection.before, 'utf-8').splitlines()
        except TypeError:
            # Raised when mocking, should not occur in normal operation.
            return ""

    @abstractmethod
    def run_get_command(self, cmd: WellFormedCommand) -> (object, int):
        # Returns response, http_status
        return None, None

    @abstractmethod
    def run_put_command(self, cmd: WellFormedCommand) -> (str, int):
        # Returns response, http_status
        return None, None
