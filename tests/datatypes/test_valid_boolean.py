import unittest

from rassh.datatypes import valid_boolean


class TestValidBoolean(unittest.TestCase):
    """Tests for `valid_boolean.py`."""

    def test_one_returns_one(self):
        self.assertEqual(1, valid_boolean(1))

    def test_zero_returns_zero(self):
        self.assertEqual(0, valid_boolean(0))

    def test_two_is_value_error(self):
        self.assertRaises(ValueError, valid_boolean, 2)

    def test_true_returns_one(self):
        self.assertEqual(1, valid_boolean(True))

    def test_false_returns_zero(self):
        self.assertEqual(0, valid_boolean(False))

    def test_none_is_value_error(self):
        self.assertRaises(ValueError, valid_boolean, None)

    def test_true_string_returns_one(self):
        self.assertEqual(1, valid_boolean("True"))

    def test_false_string_returns_zero(self):
        self.assertEqual(0, valid_boolean("False"))

    def test_unchecked_string_is_value_error(self):
        self.assertRaises(ValueError, valid_boolean, "Cardiff")


if __name__ == '__main__':
    unittest.main()
