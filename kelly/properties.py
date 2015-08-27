from datetime import datetime
from errors import ERROR_INVALID, ERROR_REQUIRED, InvalidPropertyError
from validators import regex
from base import Model


class Property(object):
    """Base property class"""

    def __init__(self, required=True, default=None, validators=None, error_key=None):
        """Class constructor

        :param required
        :param default
        :param validators
        :param error_key
        """

        self.required = required
        self.default = default
        self.validators = validators if validators is not None else []
        self.error_key = error_key

    def validate(self, value):
        """Validate the property against the provided value

        :param value
        """

        try:
            if value is None and self.required:
                assert value is not None, ERROR_REQUIRED
            elif value is not None:
                self._do_validate(value)
                for validator in self.validators:
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
    def default_value(self):
        try:
            default_value = self.default()
        except TypeError:
            default_value = self.default

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
    """DateTime property"""

    def _do_validate(self, value):
        assert isinstance(value, datetime), ERROR_INVALID


class Uuid(String):
    """UUID property"""

    def __init__(self, required=True, default=None, validators=None):
        super(Uuid, self).__init__(required, default, validators)

        self.validators.append(regex(r'\A[0-9a-f-]{36}\Z'))

    @property
    def default_value(self):
        return None if self.default is None else unicode(super(Uuid, self).default_value)


class List(Property):
    """String property"""

    def __init__(self, property_class=None, **kwargs):
        super(List, self).__init__(**kwargs)

        self.property_class = property_class

    def _do_validate(self, value):
        assert isinstance(value, list), ERROR_INVALID

        if self.property_class is not None:
            try:
                for single_value in value:
                    self.property_class.validate(single_value)
            except AssertionError:
                raise AssertionError(ERROR_INVALID)

    def to_dict(self, value):
        if value is None or self.property_class is None:
            return value

        return [dict(item) if isinstance(item, Model) else item for item in value]

    def from_dict(self, value):
        if value is None or self.property_class is None:
            return value

        return [self.property_class.model_class(**item) if isinstance(item, dict) else item for item in value]


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

        if isinstance(value, Model):
            value.validate()

    def to_dict(self, value):
        if value is None:
            return None

        return dict(value)

    def from_dict(self, value):
        if value is None:
            return None

        return self.model_class(**value)
