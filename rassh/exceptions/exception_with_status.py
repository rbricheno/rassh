class ExceptionWithStatus(Exception):
    def __init__(self, message: str, status: int):
        super(ExceptionWithStatus, self).__init__(message)
        self.message = message
        self.status = status
