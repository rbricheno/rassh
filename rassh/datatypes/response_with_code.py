class ResponseWithCode(object):
    """A response to an HTTP request, with an HTTP response code."""
    def __init__(self, response: object, code: int):
        try:
            int_code = int(code)
        except TypeError:
            raise ValueError("Code must be an integer")
        self.__response = response
        self.__code = int_code

    def get_response(self):
        return self.__response

    def get_code(self) -> int:
        return self.__code
