import unittest

from rassh.datatypes.valid_antenna_gain import valid_gain, valid_gain_as_string


class TestValidAntennaGain(unittest.TestCase):
    """Tests for `valid_antenna_gain.py`."""

    def test_one_returns_one(self):
        self.assertEqual(1, valid_gain(1))

    def test_zero_returns_zero(self):
        self.assertEqual(0, valid_gain(0))

    def test_sixty_point_five_returns_sixty_point_five(self):
        self.assertEqual(60.5, valid_gain(60.5))

    def test_none_is_type_error(self):
        self.assertRaises(ValueError, valid_gain, None)

    def test_cheese_is_value_error(self):
        self.assertRaises(ValueError, valid_gain, "Cheese")

    def test_sixty_four_is_value_error(self):
        self.assertRaises(ValueError, valid_gain, 64)

    def test_minus_one_is_value_error(self):
        self.assertRaises(ValueError, valid_gain, -1)

    def test_sixty_point_five_returns_sixty_point_fife_as_string(self):
        self.assertEqual("60.5", valid_gain_as_string(60.5))

    def test_one_returns_one_point_zero_as_string(self):
        self.assertEqual("1.0", valid_gain_as_string(1))

    def test_two_point_zero_zero_one_returns_two_point_zero_as_string(self):
        self.assertEqual("2.0", valid_gain_as_string(2.001))


if __name__ == '__main__':
    unittest.main()
