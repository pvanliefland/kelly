import re

ERROR_INVALID = 'invalid'
ERROR_REQUIRED = 'required'


def choices(allowed_choices):
    """Choice validator"""

    def validator(value):
        assert value in allowed_choices, ERROR_INVALID

    return validator


def min_length(length):
    """Min length validator"""

    def validator(value):
        assert len(value) >= length, ERROR_INVALID

    return validator


def max_length(length):
    """Max length validator"""

    def validator(value):
        assert len(value) <= length, ERROR_INVALID

    return validator


def regex(pattern):
    """Regex validator"""

    def validator(value):
        assert re.match(pattern, value) is not None, ERROR_INVALID

    return validator
