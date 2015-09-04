# -*- coding: utf-8 -*-

"""
kelly.properties
~~~~~~~~~~~~~~~~

Property classes.

"""

from datetime import datetime
from errors import ERROR_INVALID, ERROR_REQUIRED, InvalidPropertyError
from kelly.errors import CannotSetPropertyError, InvalidModelError
from validators import regex
from base import Model as BaseModel, Property as BaseProperty
from copy import copy


class Property(BaseProperty):
    """Base property class"""

    def __init__(self, required=True, default_value=None, validators=None, error_key=None):
        """Class constructor

        :param required
        :param default
        :param validators
        :param error_key
        """

        self.required = required
        self.default_value = default_value if callable(default_value) else copy(default_value)
        self.validators = validators if validators is not None else []
        self.error_key = error_key

    def process_value(self, value):
        """Override this method in a child class to process values.
        This processing is done when setting a property on a model.

        :param value
        """

        return value

    def validate(self, value, context=None):
        """Validate the property against the provided value

        :param value
        :param context: an arbitrary validation context (any string will do)
        """

        try:
            if value is None and self.required:
                assert value is not None, ERROR_REQUIRED
            elif value is not None:
                self._do_validate(value)
                for validator in filter(lambda v: v.context is None or v.context == context, self.validators):
                    validator(value)
        except AssertionError as e:
            raise InvalidPropertyError(e.message)

    def _do_validate(self, value):
        """This method should be implemented in child classes and perform the type-specific validation

        :param value
        """

        raise NotImplementedError()

    def to_dict(self, value):
        """Prepare the value for a model dict representation

        :param value
        """

        return value

    def from_dict(self, value):
        """Prepare the value from a model dict representation

        :param value
        """

        return value

    @property
    def default(self):
        try:
            default_value = self.default_value()
        except TypeError:
            default_value = copy(self.default_value)

        return default_value


class String(Property):
    """String property"""

    def _do_validate(self, value):
        assert isinstance(value, basestring), ERROR_INVALID


class Integer(Property):
    """String property"""

    def _do_validate(self, value):
        assert isinstance(value, int), ERROR_INVALID


class DateTime(Property):
    def __init__(self, include_microseconds=True, **kwargs):
        """Class constructor

        :param include_microseconds: whether to keep track of microseconds or not
        """

        super(DateTime, self).__init__(**kwargs)

        self.include_microseconds = include_microseconds

    def process_value(self, value):
        if value is None:
            return None

        return value.replace(microsecond=0) if not self.include_microseconds else value

    def _do_validate(self, value):
        assert isinstance(value, datetime), ERROR_INVALID


class Uuid(String):
    """UUID property"""

    def __init__(self, required=True, default_value=None, validators=None):
        super(Uuid, self).__init__(required, default_value, validators)

        self.validators.append(regex(r'\A[0-9a-f-]{36}\Z'))

    @property
    def default(self):
        return None if self.default_value is None else unicode(super(Uuid, self).default)


class List(Property):
    """String property"""

    def __init__(self, property=None, **kwargs):
        super(List, self).__init__(**kwargs)

        self.property = property

    def _do_validate(self, value):
        assert isinstance(value, list), ERROR_INVALID

        if self.property is not None:
            try:
                for single_value in value:
                    self.property.validate(single_value)
            except AssertionError:
                raise AssertionError(ERROR_INVALID)

    def to_dict(self, value):
        if value is None or self.property is None:
            return value

        return [dict(item) if isinstance(item, BaseModel) else item for item in value]

    def from_dict(self, value):
        if value is None or self.property is None:
            return value

        return [self.property.from_dict(item) if isinstance(item, dict) else item for item in value]


class Dict(Property):
    """Dict property"""

    def __init__(self, mapping=None, **kwargs):
        super(Dict, self).__init__(**kwargs)

        self.mapping = mapping

    def _do_validate(self, value):
        assert isinstance(value, dict), ERROR_INVALID

        if self.mapping is not None:
            try:
                for inner_key in self.mapping:
                    inner_value = value.get(inner_key)
                    self.mapping[inner_key].validate(inner_value)
                for provided_key in value:
                    assert provided_key in self.mapping, ERROR_INVALID
            except (AssertionError, InvalidPropertyError):
                raise AssertionError(ERROR_INVALID)


class Boolean(Property):
    """Boolean property"""

    def _do_validate(self, value):
        assert value in [True, False], ERROR_INVALID


class Object(Property):
    """Object property"""

    def __init__(self, model_class, **kwargs):
        super(Object, self).__init__(**kwargs)

        self.model_class = model_class

    def _do_validate(self, value):
        assert isinstance(value, self.model_class), ERROR_INVALID

        if isinstance(value, BaseModel):
            try:
                value.validate()
            except InvalidModelError:
                raise AssertionError(ERROR_INVALID)

    def to_dict(self, value):
        if value is None:
            return None

        return dict(value)

    def from_dict(self, value):
        if value is None:
            return None

        return self.model_class(**value)


class Constant(Property):
    """Constant property"""

    def __init__(self, value, **kwargs):
        super(Constant, self).__init__(required=False, **kwargs)

        self.value = value

    def process_value(self, value):
        """Constant values are... constant

        :param value
        """

        if value != self.value:
            raise CannotSetPropertyError('Cannot set value of Constant properties')

        return value

    @property
    def default(self):
        return self.value

    def _do_validate(self, value):
        assert value == self.value, ERROR_INVALID





