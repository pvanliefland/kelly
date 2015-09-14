# -*- coding: utf-8 -*-

"""
kelly.models
~~~~~~~~~~~~

Model class/metaclass.

"""

from errors import ERROR_EXTRA, InvalidModelError, InvalidPropertyError
from base import Model as BaseModel, Property as BaseProperty
from validators import ModelValidator


class ModelMeta(type):
    """Model metaclass"""

    def __new__(mcs, name, bases, dct):
        cls = type.__new__(mcs, name, bases, dct)
        if BaseModel not in bases:  # We don't want to call __model_init__ when building Model itself
            cls._model_properties = {}
            cls._model_validators = []

            # Parse properties for the model class itself (those do not include parent classes properties)
            cls.__model_init__.im_func(cls, bases, dct)

        return cls


class Model(BaseModel):
    """Base model class"""

    __metaclass__ = ModelMeta

    @classmethod
    def __model_init__(cls, bases, dct, delete_attr=True):
        """Initialize the model class"""

        for candidate_name, candidate_value in dct.items():
            if isinstance(candidate_value, BaseProperty):  # Properties setup
                cls._model_properties[candidate_name] = candidate_value
                if delete_attr:
                    delattr(cls, candidate_name)
            elif isinstance(candidate_value, ModelValidator):  # Model validators setup
                cls._model_validators.append(candidate_value)
                if delete_attr:
                    delattr(cls, candidate_name)

        # Parse properties for the base classes (if they are proper Kelly models)
        for base in [base for base in bases if issubclass(base, Model) and not base is Model]:
            base.__model_init__.im_func(cls, base.__bases__, base._model_properties, False)

    def __new__(cls, **kwargs):
        """Provide a default constructor to model classes"""

        model_instance = super(Model, cls).__new__(cls)

        # Loop over properties and fetch a value (provided or default)
        for property_name, property_instance in cls._model_properties.iteritems():
            if property_name in kwargs:
                property_value = kwargs.pop(property_name)
            else:
                property_value = property_instance.default

            setattr(model_instance, property_name, property_value)

        # If anything left in kwargs, invalid
        if len(kwargs) > 0:
            raise InvalidModelError(errors={extra_property_name: ERROR_EXTRA for extra_property_name in kwargs})

        return model_instance

    def validate(self, context=None):
        """Validate the model

        :param context: an arbitrary validation context (any string will do)
        """

        errors = {}

        # Call validate() on Property instances
        for property_name, property_instance in self._model_properties.iteritems():
            property_value = getattr(self, property_name)

            try:
                property_instance.validate(property_value, context)
            except InvalidPropertyError as e:
                error_key = property_instance.error_key if property_instance.error_key is not None else property_name
                errors[error_key] = e.error

        # Call model validators
        for validator in self._model_validators:
            if validator.context is None or context == validator.context or validator.error_key not in errors:
                try:
                    validator(self)
                except AssertionError as e:
                    errors[validator.error_key] = e.message

        if len(errors) > 0:
            raise InvalidModelError(errors)

    def __iter__(self):
        """Allow dict casting"""

        casted = []

        for property_name, property_instance in self._model_properties.iteritems():
            casted.append((property_name, property_instance.to_dict(getattr(self, property_name))))

        return iter(casted)

    def __setattr__(self, name, value):
        """Some properties may choose to transform the value provided to them.

        :param name
        :param value
        """

        if name in self._model_properties:
            value = self._model_properties[name].process_value(value)

        return super(Model, self).__setattr__(name, value)

    @classmethod
    def from_dict(cls, dct):
        """Factory method to handle dict model data.
        Useful to instantiate a model previously casted to dict.

        > blog_post = BlogPost(title="Hello World!")
        > blog_post_dict = dict(blog_post)
        > restored_blog_post = BlogPost.from_dict(blog_post_dict)

        :type cls: Model
        :type dct: dict
        """

        casted = {}

        for property_name, property_instance in cls._model_properties.iteritems():
            if property_name in dct:
                casted[property_name] = property_instance.from_dict(dct[property_name])

        return cls(**casted)
