import json

from rassh.api.resources import ExpectFeedbackResource
from rassh.api.postgres_functions import PostgresFunctions
from rassh.managers.expect_commands import ExpectCommands

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgresFeedback(ExpectFeedbackResource):
    """This resource is a generic endpoint for expect APIs to post feedback. It supports updating a PostgreSQL database
    with details of the requested commands and their results."""
    commands = ExpectCommands(None)

    def post(self):
        args = type(self).parser.parse_args()
        request = args['request']
        response = args['response']
        status = args['status']
        postgres = PostgresFunctions()

        logger.debug("Feedback processing command: " + request)

        if str(status) == "202":
            completed = False
        else:
            completed = True

        request_obj = json.loads(request)

        command_type_parts = request_obj['command'].split('_')
        command_type = command_type_parts[0]
        part_name = '_'.join(command_type_parts[1:])

        if command_type == 'put':
            try:
                table_name = type(self).commands.grammar.parameters[part_name]['object_type']
                key_name = type(self).commands.grammar.object_type_to_key_name[table_name]
                result = postgres.completed_config(table_name, key_name, request_obj['target'], request, response, status, completed)
                logger.debug("Feedback received and logged for command: " + request)
            except KeyError:
                logger.error("Key error when handling feedback.")
                result = False
        else:
            # We aren't interested in feedback about anything else (e.g. the "get" commands).
            result = True

        if result:
            return request + " " + str(response) + " " + str(status) + " OK", 204
        else:
            return request + " " + str(response) + " " + str(status) + " Failed", 500
