"""A valid boolean argument."""


def valid_boolean(boolean_as_hopefully_int) -> int:
    """Use this to parse an argument as if it were boolean, and get back an int 0 or 1.
    In sqlite a 'boolean' is actually an int which takes the value 1 or 0, with 1 representing True.
    Raises ValueError if passed an un-parse-able value.
    """
    try:
        # This handles cases where the argument was an int or literal True or False
        my_boolean = int(boolean_as_hopefully_int)
        if my_boolean > 1 or my_boolean < 0:
            raise ValueError("Value out of range for a valid (sqlite) boolean argument.")
        else:
            return my_boolean
    except TypeError:
        raise ValueError("Could not parse value as into a valid (sqlite) boolean argument (invalid type).")
    except ValueError:
        # This tries to parse the argument as textual true or false.
        if str(boolean_as_hopefully_int).lower() == "true":
            return 1
        if str(boolean_as_hopefully_int).lower() == "false":
            return 0
        raise ValueError("Could not parse value as into a valid (sqlite) boolean argument.")
