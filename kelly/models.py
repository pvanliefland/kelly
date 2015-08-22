from properties import Property, InvalidPropertyError

ERROR_EXTRA = 'extra'


def model(model_cls):
    """Model class decorator"""

    model_properties = {}
    model_validators = []

    for member_name, member_value in model_cls.__dict__.items():
        if isinstance(member_value, Property):  # Properties setup
            model_properties[member_name] = member_value
            delattr(model_cls, member_name)
        elif isinstance(member_value, ModelValidator):  # Model validators setup
            model_validators.append(member_value)

    class Model(model_cls):
        """Dynamic base model class"""

        def __new__(cls, **kwargs):
            model_instance = super(Model, cls).__new__(cls)

            # Loop over properties and fetch a valud (provided or default)
            for property_name in model_properties:
                if property_name in kwargs:
                    property_value = kwargs.pop(property_name)
                else:
                    property_value = model_properties[property_name].default_value

                setattr(model_instance, property_name, property_value)

            # If anything left in kwargs, invalid
            if len(kwargs) > 0:
                raise InvalidModelError(errors={extra_property_name: ERROR_EXTRA for extra_property_name in kwargs})

            return model_instance

        def validate(self):
            """Validate the model"""

            errors = {}

            # Call validate() on Property instances
            for property_name, property_instance in model_properties.iteritems():
                property_value = getattr(self, property_name)

                try:
                    property_instance.validate(property_value)
                except InvalidPropertyError as e:
                    error_key = property_instance.error_key if property_instance.error_key is not None else property_name
                    errors[error_key] = e.error

            # Call model validators
            for validator in model_validators:
                try:
                    validator(self)
                except AssertionError as e:
                    errors[validator.error_key] = e.message

            if len(errors) > 0:
                raise InvalidModelError(errors)

    return Model


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


class InvalidModelError(Exception):
    def __init__(self, errors):
        self.errors = errors
