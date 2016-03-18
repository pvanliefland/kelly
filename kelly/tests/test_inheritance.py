# -*- coding: utf-8 -*-

"""
kelly.tests.test_inheritance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specific tests related to model inheritance.

"""

import kelly as k


class Person(k.Model):
    name = k.String(required=False)
    nickname = k.String(required=False)
    gender = k.String(required=False)

    @k.model_validator('message')
    def name_or_nickname(self):
        assert self.name is not None or self.nickname is not None, k.ERROR_REQUIRED


class Friend(Person):
    age = k.Integer()
    gender = k.String(required=True)


class BestFriend(Friend):
    secrets = k.List(property=k.String())

    @k.model_validator('secrets')
    def has_a_secret_or_is_too_young(self):
        assert len(self.secrets) > 0 or self.age < 10


def test_inheritance():
    """Make sure that model properties and validators are properly inherited"""

    # Check model properties
    assert len(Person._model_properties) == 3
    assert len(Friend._model_properties) == 4
    assert Friend._model_properties['gender'].required is True
    assert len(BestFriend._model_properties) == 5

    # Check model validators
    assert len(Person._model_validators) == 1
    assert len(Friend._model_validators) == 1
    assert len(BestFriend._model_validators) == 2
