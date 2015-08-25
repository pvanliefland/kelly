from errors import ERROR_EXTRA, InvalidModelError
from properties import InvalidPropertyError, Property
from base import Model as BaseModel
from validators import ModelValidator


class ModelMeta(type):
    """Model metaclass"""

    def __new__(mcs, name, bases, dct):
        cls = type.__new__(mcs, name, bases, dct)
        if BaseModel not in bases:  # We don't want to call __model_init__ when building Model itself
            cls.__model_init__.im_func(cls, dct)

        return cls


class Model(BaseModel):
    """Base model class"""

    __metaclass__ = ModelMeta

    @classmethod
    def __model_init__(cls, dct):
        """Initialize the model class"""

        cls._model_properties = {}
        cls._model_validators = []

        for member_name, member_value in dct.items():
            if isinstance(member_value, Property):  # Properties setup
                cls._model_properties[member_name] = member_value
                del dct[member_name]
            elif isinstance(member_value, ModelValidator):  # Model validators setup
                cls._model_validators.append(member_value)

    def __new__(cls, **kwargs):
        """Provide a default constructor to model classes"""

        model_instance = super(Model, cls).__new__(cls)

        # Loop over properties and fetch a value (provided or default)
        for property_name in cls._model_properties:
            if property_name in kwargs:
                property_value = kwargs.pop(property_name)
            else:
                property_value = cls._model_properties[property_name].default_value

            setattr(model_instance, property_name, property_value)

        # If anything left in kwargs, invalid
        if len(kwargs) > 0:
            raise InvalidModelError(errors={extra_property_name: ERROR_EXTRA for extra_property_name in kwargs})

        return model_instance

    def validate(self):
        """Validate the model"""

        errors = {}

        # Call validate() on Property instances
        for property_name, property_instance in self._model_properties.iteritems():
            property_value = getattr(self, property_name)

            try:
                property_instance.validate(property_value)
            except InvalidPropertyError as e:
                error_key = property_instance.error_key if property_instance.error_key is not None else property_name
                errors[error_key] = e.error

        # Call model validators
        for validator in self._model_validators:
            if not validator.error_key in errors:
                try:
                    validator(self)
                except AssertionError as e:
                    errors[validator.error_key] = e.message

        if len(errors) > 0:
            raise InvalidModelError(errors)
