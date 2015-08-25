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


class ModelValidator(object):
    """Model validators decorate model methods so that they are automatically called when validating the model."""

    def __init__(self, validator_function, error_key):
        self.validator_function = validator_function
        self.error_key = error_key

    def __call__(self, *args, **kwargs):
        return self.validator_function(*args, **kwargs)


def model_validator(error_key):
    """Model validator decorator

    :param error_key
    """

    def decorator(f):
        return ModelValidator(f, error_key)

    return decorator
