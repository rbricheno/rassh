import atexit
from threading import Lock
from pexpect import pxssh, exceptions

from rassh.config.config import Config
from rassh.datatypes import ResponseWithCode
from rassh.queue.request_queue import RequestQueue
from rassh.datatypes import WellFormedCommand
from rassh.managers.expect_commands import ExpectCommands

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExpectManager:
    """This class manages all of the expect connections to the managed system(s). It processes requests that come in via
    the HTTP API, and it also manages the queue of outstanding requests.

    The commands available to the ExpectManager are individually imported by the ExpectCommands class referred to as
    self.commands, as commands.supported_commands. This is also where the current 'Grammar' is found (commands.grammar).

    ExpectManager can only process one request at a time per instance. A lock must be obtained for each request.
    The request method will block until the previous request has released the lock. It will eventually time out if the
    lock cannot be obtained fast enough."""

    config_instance = Config()
    config = config_instance.data
    # TODO: There's a terrible and evil problem here. You *must not* use the VRRP address or a set of Aruba
    # TODO: master controllers, otherwise they end up thinking that their real address is an LMS and establishing
    # TODO: multiple SSH connections to the controller with the VRRP address. That quickly exhasts SSH connections
    # TODO: which results in various unexpected behaviors.

    _default_master = config.get('master_controller')
    # Please use the get_instance method to access this variable!
    _expect_managers = {}

    def __init__(self, controller_ip):
        logger.info("Setting up command list for controller " + controller_ip + "...")
        self.commands = self._my_commands()

        self.__lock = Lock()
        self.master_controller = controller_ip
        logger.info("Getting expect connection...")
        master_expect_connection = self.get_new_expect_connection(self.master_controller)

        self.all_expect_connections = {self.master_controller: master_expect_connection}

        self._get_managed_children()
        logger.info("Setting up request queue...")
        self.queue = RequestQueue(self)

        atexit.register(self.__cleanup)

    @classmethod
    def get_instance(cls, controller_ip=None):
        """Please be polite and use this method to get instances of ExpectManager for a given controller, so the API
        only takes up one expect connection per controller."""
        if controller_ip is None:
            controller_ip = cls._default_master

        if controller_ip in cls._expect_managers:
            return cls._expect_managers[controller_ip]
        else:
            expect_manager = cls(controller_ip)
            cls._expect_managers[controller_ip] = expect_manager
            return expect_manager

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__cleanup()

    def __cleanup(self):
        for ip, expect_connection in self.all_expect_connections.items():
            try:
                expect_connection.logout()
            except (pxssh.ExceptionPxssh, exceptions.EOF, OSError):
                pass

    @staticmethod
    def get_new_expect_connection(controller_ip):
        try:
            new_expect_connection = pxssh.pxssh()
            # PROMPT is a regular expression which will match the prompt on the remote system.
            # This matches the Bonaire "Enable" prompt, and the "conf t" prompt.
            new_expect_connection.PROMPT = "\([a-zA-Z0-9_\-\\\"\s]*\) #"
            new_expect_connection.login(controller_ip,
                                        ExpectManager.config.get('api_ssh_user'),
                                        ExpectManager.config.get('api_ssh_password'),
                                        auto_prompt_reset=False)
            # Prevent the Bonaire pager from kicking in when running commands with long outputs.
            # Disabled here, but left as an example of the sort of thing you can do when getting a connection.
            # new_expect_connection.sendline("no paging")
            if not new_expect_connection.prompt():
                raise exceptions.TIMEOUT("Prompt timed out!")
            return new_expect_connection
        except exceptions.EOF as e:
            logger.error("EOF Exception when getting a new expect connection." +
                         " Is the destination host rejecting connections?" +
                         " Was this a login with bad username / password?")
            logger.error(e.get_trace())
            return None
        except exceptions.TIMEOUT as e:
            logger.error("Timeout Exception when getting a new expect connection. Is the destination host accessible?")
            logger.error(e.get_trace())
            return None
        except pxssh.ExceptionPxssh as e:
            logger.error("Unknown exception when getting a new expect connection.")
            logger.error(e.get_trace())
            return None

    def _get_managed_children(self):
        self.switches = []

    def _my_commands(self) -> ExpectCommands:
        return ExpectCommands(self)

    def request(self, request_dict=None, request=None) -> ResponseWithCode:
        """The main public method used to run expect commands. Called by add_dynamic_resources with request_dict=dict
        and by RequestQueue with request=string"""
        cmd = WellFormedCommand(self.commands.grammar, request_dict=request_dict, request=request)
        response = self.__run_request_command(cmd)
        return response

    def __run_request_command(self, cmd: WellFormedCommand) -> ResponseWithCode:
        """The private method used to run expect commands, which must obtain a lock before running."""

        with self.__lock:

            response = None
            http_status = None

            if cmd is None:
                http_status = 400
            else:
                for command_to_run in self.commands.supported_commands:
                    response, http_status = command_to_run.request_command(cmd)
                    if http_status:
                        logger.info("Got status " + str(http_status) + " for command: " + command_to_run.command_name)
                        logger.debug("Response was: " + str(response))
                        if ExpectManager.config.get('feedback') and http_status != 202:
                            # 2xx feedback is sent, but handled differently from other statuses atr the remote end.
                            # No feedback is sent while we are still waiting to try something (i.e. in the 408 case
                            # above) to prevent filling our logs on the remote end if this system is too busy).
                            # 202 feedback is not sent here, but when we first do queue.enqueue_request, to prevent
                            # it from being resent every time the queue is run.
                            if self.queue.enqueue_feedback(cmd.request, response, http_status):
                                logger.debug("Feedback sent or enqueued.")
                            else:
                                logger.warning("Error when enqueueing feedback.")
                        break

            return ResponseWithCode(response, http_status)
