import unittest

from rassh.datatypes.grammar import Grammar


class TestGrammar(unittest.TestCase):
    """Tests for `grammar.py`."""

    def test_new_grammar_has_variables(self):
        a_grammar = Grammar()
        self.assertEqual({}, a_grammar.parameters)
        self.assertEqual({}, a_grammar.object_type_to_key_name)


if __name__ == '__main__':
    unittest.main()
