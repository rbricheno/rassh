from flask_restful import Resource, reqparse

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_dynamic_resources(api, expect_manager):
    """This creates new flask_restful Resource classes for every supported command, dynamically, and adds them to the
    API. Default URLs are named after the commands."""
    logger.info("Adding resources...")
    if expect_manager.commands.grammar.parameters:
        for command_name, command_options in expect_manager.commands.grammar.parameters.items():

            command_name_parts = command_name.split('_')
            class_name = "RestAPI"

            if command_options['default']:
                class_name += "Default"

            for part in command_name_parts:
                class_name += part.capitalize()

            new_class = type(class_name, (Resource,), {})

            setattr(new_class, 'ssh', expect_manager)

            parser = reqparse.RequestParser()
            if command_options['payload']:
                for our_payload_item in command_options['payload']:
                    parser.add_argument(our_payload_item)
            setattr(new_class, 'parser', parser)

            setattr(new_class, 'get_command', 'get_' + command_name)
            setattr(new_class, 'put_command', 'put_' + command_name)
            setattr(new_class, 'object_type', command_options['object_type'])

            key_name = expect_manager.commands.grammar.object_type_to_key_name[command_options['object_type']]
            setattr(new_class, 'key_name', key_name)

            setattr(new_class, 'payload_items', command_options['payload'])

            def api_get(cls, target=None):
                request_dict = {'command':cls.get_command}
                request_dict['object_type'] = cls.object_type
                request_dict['target'] = target
                response = cls.ssh.request(request_dict=request_dict)
                return response.get_response(), response.get_code()

            def api_put(cls, target=None):
                args = cls.parser.parse_args()
                request_dict = {'command':cls.put_command}
                request_dict['object_type'] = cls.object_type
                request_dict['target'] = target
                request_dict['params'] = {}
                if cls.payload_items:
                    for payload_item in cls.payload_items:
                        request_dict['params'][payload_item] = args[payload_item]
                response = cls.ssh.request(request_dict=request_dict)
                return response.get_response(), response.get_code()

            setattr(new_class, 'get', classmethod(api_get))
            setattr(new_class, 'put', classmethod(api_put))

            # api.add_resource(new_class, '/' + url)
            # Note: we want to do the above, but it doesn't work for some reason.
            # I think this is something to do with the fact we are stringing this together dynamically, but I haven't
            # yet debugged it all properly.
            # Fortunately, the "methods" keyword argument, while not documented, is still valid in flask_restful
            # and this makes everything work as it should.
            api.add_resource(new_class, '/' + command_options['url'], methods = ['GET', 'PUT'])

            logger.info("Added resource " + class_name + " at /" + command_options['url'])
    else:
        logger.info("No resources found!")