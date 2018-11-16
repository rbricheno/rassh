import time
import threading
import requests
import copy

from rassh.api.nonblocking_put_request import NonBlockingPutRequest
from rassh.config.config import Config
from rassh.datatypes import Grammar
from rassh.datatypes.well_formed_command import WellFormedCommand


class SendCommands(object):
    """This is the class you should import into your applications if you want to make requests to the rassh API in a
    standard way, without having to worry about making HTTP requests yourself. Subclasses may hook in here to do
    useful things like update your local database, e.g. to note that you are awaiting feedback from a request.

    Typically you will want to send a batch of commands all at once when putting configuration. By default, you can
    send these when instantiating a SendCommands and passing a list of request dictionaries as request_dict_list=[...].

    Alternatively, if you only want to run one command at a time, instantiate a SendCommands with no arguments, and
    call api_command to send each command individually."""

    def __init__(self, put_request_dict_list=None):
        self.grammar = self._my_grammar()
        config_instance = Config()
        self.config = config_instance.data
        self.__outstanding_api_put_commands = put_request_dict_list
        self.url_base = "http://" + self.config['api_host'] + ":" + str(self.config['api_port']) + "/"
        if put_request_dict_list:
            thread = threading.Thread(target=self.run, args=())
            thread.daemon = True
            thread.start()

    def _my_grammar(self):
        # This default Grammar is empty!
        return Grammar()

    def run(self):
        outstanding_request_dict = {}
        i = 0
        for api_command_dict in self.__outstanding_api_put_commands:
            outstanding_request_dict[i] = api_command_dict
            i += 1

        # Keep trying to send request until this dictionary is empty.
        while True:
            old_outstanding_request_dict = copy.deepcopy(outstanding_request_dict)
            for key, api_command_dict in old_outstanding_request_dict.items():
                if self.api_put_command(api_command_dict, True):
                    outstanding_request_dict.pop(key, None)
            if not outstanding_request_dict:
                break
            time.sleep(120)

    def api_get_command(self, request_dict):
        cmd = WellFormedCommand(self.grammar, request_dict=request_dict)
        send_url = self.url_base + cmd.url

        if cmd.command_name:
            try:
                response = requests.get(send_url, data=cmd.payload)
                if response.status_code == 200:
                    return response.content
            except (requests.exceptions.HTTPError, requests.exceptions.Timeout):
                return None
        return None

    def api_put_command(self, request_dict, blocking):
        cmd = WellFormedCommand(self.grammar, request_dict=request_dict)
        send_url = self.url_base + cmd.url

        if cmd.command_name:
            try:
                if self._send_put_command(send_url, cmd.payload, blocking):
                    return True
            except KeyError:
                pass
        return False

    def _send_put_command(self, url, payload, blocking):
        if blocking:
            try:
                requests.put(url, data=payload)
            except (requests.exceptions.HTTPError, requests.exceptions.Timeout):
                return False
            return True
        else:
            NonBlockingPutRequest(url, payload)
            return True
