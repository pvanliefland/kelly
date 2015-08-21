from datetime import datetime
from properties import Property, String, DateTime, InvalidPropertyError


class ModelMeta(type):
    def __init__(cls, what, bases=None, dct=None):
        super(ModelMeta, cls).__init__(what, bases, dct)
        cls._model_properties = {}

        if '_model_properties' in dct:
            raise ValueError('Cannot use _model_properties')

        for member_name, member_value in dct.iteritems():
            if isinstance(member_value, Property):
                cls._model_properties[member_name] = member_value
                delattr(cls, member_name)


class Model(object):
    __metaclass__ = ModelMeta

    ERROR_EXTRA = 'extra'

    def __new__(cls, **kwargs):
        model = super(Model, cls).__new__(cls)

        for property_name in cls._model_properties:
            if property_name in kwargs:
                property_value = kwargs.pop(property_name)
            else:
                property_value = cls._model_properties[property_name].default_value

            setattr(model, property_name, property_value)

        if len(kwargs) > 0:
            raise InvalidModelError(errors={extra_property_name: cls.ERROR_EXTRA for extra_property_name in kwargs})

        return model

    def validate(self):
        """Validate the model"""

        errors = {}
        for property_name, property_instance in self._model_properties.iteritems():
            property_value = getattr(self, property_name)

            try:
                property_instance.validate(property_value)
            except InvalidPropertyError as e:
                error_key = property_instance.error_key if property_instance.error_key is not None else property_name
                errors[error_key] = e.error

        if len(errors) > 0:
            raise InvalidModelError(errors)


class InvalidModelError(Exception):
    def __init__(self, errors):
        self.errors = errors
