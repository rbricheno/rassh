import json

from rassh.datatypes.grammar import Grammar

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WellFormedCommand(object):
    """This class is used to massage requests between dictionaries and strings. We anticipate that programmers will
    want to use dictionaries in their own code to better keep track of request parameters. However, we may pass these
    around internally as json strings, which are easier to store in a generic queue amongst other advantages.

    Using WellFormedCommand you an take either a dictionary or a string, and get back both (in instance variables).
    It will also helpfully populate more instance variables with some other useful information about the command.

    Commands are "well formed" because they comply with a 'Grammar' which is defined elsewhere. Based on the Grammar we
    can quickly tell if a dictionary of parameters is valid for a particular command."""

    def __init__(self, grammar: Grammar, request_dict=None, request=None):
        if request_dict is None and request is None:
            raise ValueError("Must initialise with either a request or a request_dict.")

        # Using both is also probably not a great idea. Hold the user's hand a bit here.
        if request_dict is not None and request is not None:
            raise ValueError("Must initialise with either a request or a request_dict.")

        if request_dict is None:
            valid_request_dict, valid_request = WellFormedCommand.request_and_dict_from_request(str(request), grammar)
        else:
            valid_request_dict, valid_request = WellFormedCommand.request_and_dict_from_dict(request_dict, grammar)

        if valid_request_dict is None or valid_request is None:
            raise ValueError("Invalid request received.")

        self.request_dict = valid_request_dict
        self.request = valid_request
        self.payload = {}

        self.command_name = valid_request_dict['command']

        command_type_parts = valid_request_dict['command'].split('_')
        self.command_type = command_type_parts[0]
        self.part_name = '_'.join(command_type_parts[1:])

        self.object_type = grammar.parameters[self.part_name]['object_type']

        self.key_name = grammar.object_type_to_key_name[self.object_type]

        self.target = valid_request_dict['target']

        self.default = grammar.parameters[self.part_name]['default']
        self.no_target = grammar.parameters[self.part_name]['no_target']
        self.url = grammar.parameters[self.part_name]['url']

        if self.target and not self.no_target:
            self.url = self.url.replace('<target>', self.target)

        if grammar.parameters[self.part_name]['payload'] and self.command_type == 'put':
            for payload_item in grammar.parameters[self.part_name]['payload']:
                self.payload[payload_item] = valid_request_dict['params'][payload_item]

        if self.object_type is None or self.url is None:
            raise ValueError("Error interpreting request.")

    @staticmethod
    def get_validated_request_dict(request_dict, grammar: Grammar):
        valid_request_dict = {}
        try:
            valid_request_dict['command'] = request_dict['command']
            valid_request_dict['params'] = {}
            command_type_parts = valid_request_dict['command'].split('_')
            command_type = command_type_parts[0]
            part_name = '_'.join(command_type_parts[1:])
        except KeyError:
            logger.warning("Command missing when validating request dictionary.")
            return None

        try:
            valid_request_dict['object_type'] = request_dict['object_type']
        except KeyError:
            logger.warning("Object type missing when validating request dictionary.")
            return None

        if not grammar.parameters[part_name]['no_target']:
            try:
                valid_request_dict['target'] = request_dict['target']
            except KeyError:
                logger.warning("Target missing when validating request dictionary.")
                return None
        else:
            valid_request_dict['target'] = None

        try:
            if grammar.parameters[part_name]['payload'] and command_type == 'put':
                for payload_item in grammar.parameters[part_name]['payload']:
                    try:
                        # Coerce everything into a string, to prevent feedback from breaking unexpectedly.
                        if isinstance(request_dict['params'][payload_item], str):
                            valid_request_dict['params'][payload_item] = request_dict['params'][payload_item]
                        else:
                            valid_request_dict['params'][payload_item] = str(request_dict['params'][payload_item])
                    except KeyError:
                        logger.warning("Payload key missing when validating request dictionary: " + str(payload_item))
                        return None
        except KeyError:
            logger.warning("Bad grammar when validating request dictionary.")
            return None
        return valid_request_dict

    @staticmethod
    def request_and_dict_from_request(request, grammar: Grammar):
        if request == 'None':
            return None, None

        request_dict = json.loads(request)
        valid_request_dict = WellFormedCommand.get_validated_request_dict(request_dict, grammar)
        if not valid_request_dict:
            return None, None

        # sort_keys=True forces this output to be deterministic for a given input object.
        validated_request = json.dumps(valid_request_dict, sort_keys=True)
        return valid_request_dict, validated_request

    @staticmethod
    def request_and_dict_from_dict(request_dict, grammar: Grammar):
        valid_request_dict = WellFormedCommand.get_validated_request_dict(request_dict, grammar)
        if not valid_request_dict:
            return None, None

        # sort_keys=True forces this output to be deterministic for a given input object.
        validated_request = json.dumps(valid_request_dict, sort_keys=True)
        return valid_request_dict, validated_request
