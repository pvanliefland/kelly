# -*- coding: utf-8 -*-

"""
kelly.validators
~~~~~~~~~~~~~~~~

Property/model validators.

"""

import re

ERROR_INVALID = 'invalid'
ERROR_REQUIRED = 'required'


class Validator(object):
    """Validator callable class - keeps track of context"""

    def __init__(self, validation_function, context=None):
        self.validation_function = validation_function
        self.context = context

    def __call__(self, *args, **kwargs):
        return self.validation_function(*args, **kwargs)


def choices(allowed_choices, context=None):
    """Choice validator"""

    def validator(value):
        assert value in allowed_choices, ERROR_INVALID

    return Validator(validator, context)


def min_length(length, context=None):
    """Min length validator"""

    def validator(value):
        assert len(value) >= length, ERROR_INVALID

    return Validator(validator, context)


def max_length(length, context=None):
    """Max length validator"""

    def validator(value):
        assert len(value) <= length, ERROR_INVALID

    return Validator(validator, context)


def regex(pattern, context=None):
    """Regex validator"""

    def validator(value):
        assert re.match(pattern, value) is not None, ERROR_INVALID

    return Validator(validator, context)


class ModelValidator(object):
    """Model validators decorate model methods so that they are automatically called when validating the model."""

    def __init__(self, validator_function, error_key, context=None):
        self.validator_function = validator_function
        self.error_key = error_key
        self.context = context

    def __call__(self, *args, **kwargs):
        return self.validator_function(*args, **kwargs)


def model_validator(error_key):
    """Model validator decorator

    :param error_key
    """

    def decorator(f):
        return ModelValidator(f, error_key)

    return decorator
