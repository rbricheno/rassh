import unittest
import logging
from rassh.datatypes.grammar import Grammar
from rassh.datatypes.well_formed_command import WellFormedCommand

# This is populated in setUp()
test_grammar = Grammar()

group_and_rap_test_command = {'command': 'put_group_and_rap',
                              'object_type': 'ap',
                              'target': '00:11:22:AA:BB:CC',
                              'params': {'ap_group': 'regrouped_aps', 'remote_ap': '0'}}
group_and_rap_test_command_string = "{'command': 'put_group_and_rap', 'target': '00:11:22:AA:BB:CC', "\
                                    + "'params': {'ap_group': 'regrouped_aps', 'remote_ap': '0'}}"

group_test_command = {'command': 'put_group',
                      'object_type': 'ap',
                      'target': '00:11:22:AA:BB:CC',
                      'params': {'ap_group': 'regrouped_aps'}}
group_test_command_string = "{'command': 'put_group', 'target': '00:11:22:AA:BB:CC', "\
                            + "'params': {'ap_group': 'regrouped_aps'}}"


class TestWellFormedCommand(unittest.TestCase):
    """Tests for `well_formed_command.py`."""
    def setUp(self):
        test_grammar.object_type_to_key_name['ap'] = 'ap_wiredmac'
        test_grammar.parameters['group_and_rap'] = {}
        test_grammar.parameters['group_and_rap']['object_type'] = 'ap'
        test_grammar.parameters['group_and_rap']['payload'] = ['ap_group', 'remote_ap']
        test_grammar.parameters['group_and_rap']['no_target'] = False
        test_grammar.parameters['group'] = {}
        test_grammar.parameters['group']['object_type'] = 'ap'
        test_grammar.parameters['group']['payload'] = ['ap_group', ]
        test_grammar.parameters['group']['no_target'] = False

    def test_valid_dictionary_is_valid(self):
        self.assertEqual(group_and_rap_test_command,
                         WellFormedCommand.get_validated_request_dict(group_and_rap_test_command, grammar=test_grammar))

    def test_invalid_dictionary_is_none(self):
        logging.disable(logging.CRITICAL)
        self.assertEqual(None,
                         WellFormedCommand.get_validated_request_dict({'chicken': 'Mavis'}, grammar=test_grammar))

    # TODO more tests!!!


if __name__ == '__main__':
    unittest.main()
