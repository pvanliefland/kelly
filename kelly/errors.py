# -*- coding: utf-8 -*-

"""
kelly.errors
~~~~~~~~~~~~

Error codes & exception classes.

"""

ERROR_INVALID = 'invalid'
ERROR_REQUIRED = 'required'
ERROR_EXTRA = 'extra'


class InvalidModelError(Exception):
    """Exception raised whenever an attempt is made to validate an invalid model"""

    def __init__(self, errors):
        self.errors = errors


class InvalidPropertyError(Exception):
    """Exception raised whenever an attempt is made to validate an invalid value"""

    def __init__(self, error):
        self.error = error


class CannotSetPropertyError(Exception):
    """Exception raised whenever an attempt is made to change the value of a constant property"""

    pass