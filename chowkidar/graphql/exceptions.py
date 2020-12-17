
class APIException(Exception):
    def __init__(self, message, code=None):
        self.code = 'API_EXCEPTION'
        if code is not None:
            self.code = code
        self.message = message
        super().__init__(message)
