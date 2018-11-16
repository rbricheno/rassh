"""A valid Bonaire antenna gain argument."""


def valid_gain(gain):
    """
    Use this parse an argument as if it were a float and get back a valid gain as a float.
    Raises ValueError if passed an un-parse-able value.
    """
    try:
        my_gain = round(float(gain), 1)
    except TypeError:
        raise ValueError("Could not parse value as into a valid float argument (invalid type).")
    except ValueError:
        raise ValueError("Could not parse value as into a valid float argument.")
    if my_gain > 63.5 or my_gain < 0:
        raise ValueError("Gain outside allowed range of 0 to 63.5")
    return my_gain


def valid_gain_as_string(gain):
    """
    In case it isn't abundantly clear from the beautiful and readable syntax of the lovely format command,
    this returns a number with arbitrary digits before the decimal point and one digit after the decimal point,
    as a string.
    """
    return "{0:.1f}".format(valid_gain(gain))
