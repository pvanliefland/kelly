ERROR_INVALID = 'invalid'
ERROR_REQUIRED = 'required'
ERROR_EXTRA = 'extra'


class InvalidModelError(Exception):
    def __init__(self, errors):
        self.errors = errors


class InvalidPropertyError(Exception):
    """Exception raised whenever an attempt is made to validate an invalid value"""

    def __init__(self, error):
        self.error = error
