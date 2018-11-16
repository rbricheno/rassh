import unittest

from rassh.datatypes.response_with_code import ResponseWithCode


class TestResponseWithCode(unittest.TestCase):
    """Tests for `response_with_code.py`."""

    def test_new_response_with_code_has_variables(self):
        a_response_with_code = ResponseWithCode("cassowary", 200)
        self.assertEqual("cassowary", a_response_with_code.get_response())
        self.assertEqual(200, a_response_with_code.get_code())

    def test_cannot_create_with_invalid_code(self):
        self.assertRaises(ValueError, ResponseWithCode, "chips", "salt")

    def test_cannot_create_with_nones(self):
        self.assertRaises(ValueError, ResponseWithCode, None, None)


if __name__ == '__main__':
    unittest.main()
