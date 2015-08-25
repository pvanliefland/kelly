from uuid import uuid4
from . import Model, String, Integer, Uuid, DateTime, List, Dict, Boolean, Object, InvalidModelError, \
    InvalidPropertyError, min_length, max_length, regex, choices, ERROR_REQUIRED, model_validator
from nose.tools import assert_raises
from datetime import datetime


def test_string_invalid_1():
    """Integer is not a valid value"""

    test_string = String()

    with assert_raises(InvalidPropertyError) as cm:
        test_string.validate(5)

    assert cm.exception.error == 'invalid'


def test_string_invalid_2():
    """'fo' is too short"""

    test_string = String(validators=[min_length(3)])

    with assert_raises(InvalidPropertyError) as cm:
        test_string.validate('fo')

    assert cm.exception.error == 'invalid'


def test_string_invalid_3():
    """'foobar" is too long"""

    test_string = String(validators=[max_length(5)])

    with assert_raises(InvalidPropertyError) as cm:
        test_string.validate('foobar')

    assert cm.exception.error == 'invalid'


def test_string_regex():
    """By default, a value is required"""

    test_string = String(validators=[regex(r'^([a-z]*)$')])

    test_string.validate('abc')

    with assert_raises(InvalidPropertyError) as cm:
        test_string.validate('1236580002EEEEE')

    assert cm.exception.error == 'invalid'


def test_string_choices():
    """Value can only be 'published' or 'draft'"""

    test_string = String(validators=[choices(['published', 'draft'])])

    test_string.validate('published')

    with assert_raises(InvalidPropertyError) as cm:
        test_string.validate('not_a_status')

    assert cm.exception.error == 'invalid'


def test_string_required():
    """By default, a value is required"""

    test_string = String()

    with assert_raises(InvalidPropertyError) as cm:
        test_string.validate(None)

    assert cm.exception.error == 'required'


def test_string_not_required():
    """If the property is not required, None is a valid value"""

    test_string = String(required=False)
    test_string.validate(None)

    assert True


def test_string_valid_1():
    """'foo' is a valid string"""
    test_string = String()
    test_string.validate('foo')

    assert True


def test_string_default():
    """Test property default values"""

    test_string = String(default="bar")

    assert test_string.default_value == "bar"


def test_integer_invalid_1():
    """String is not a valid value"""

    test_string = Integer()

    with assert_raises(InvalidPropertyError) as cm:
        test_string.validate('foo')

    assert cm.exception.error == 'invalid'


def test_integer_valid_1():
    """5 is a valid integer"""

    test_string = Integer()
    test_string.validate(5)

    assert True


def test_datetime_invalid():
    """A string is not a valid datetime"""

    test_datetime = DateTime()

    with assert_raises(InvalidPropertyError) as cm:
        test_datetime.validate('not a datetime')

    assert cm.exception.error == 'invalid'


def test_datetime_valid():
    """Should be ok"""

    test_datetime = DateTime()
    test_datetime.validate(datetime.now())

    assert True


def test_list_invalid_1():
    """List should be a list instance"""

    test_list = List()

    with assert_raises(InvalidPropertyError) as cm:
        test_list.validate('lol')

    assert cm.exception.error == 'invalid'


def test_list_invalid_2():
    """List contains invalid values"""

    test_list = List(inner=String())

    with assert_raises(InvalidPropertyError) as cm:
        test_list.validate([3, 5])

    assert cm.exception.error == 'invalid'


def test_list_invalid_3():
    """List is too short"""

    test_list = List(validators=[min_length(3)])

    with assert_raises(InvalidPropertyError) as cm:
        test_list.validate([3, 5])

    assert cm.exception.error == 'invalid'


def test_list_valid_1():
    """Should be ok"""

    test_list = List(validators=[min_length(3)])
    test_list.validate([3, 5, 9])

    assert True


def test_list_valid_2():
    """Should be ok"""

    test_list = List(inner=String(validators=[min_length(3)]))
    test_list.validate(['abcdef'])

    assert True


def test_dict_invalid_1():
    """Wrong type"""

    test_dict = Dict()

    with assert_raises(InvalidPropertyError) as cm:
        test_dict.validate('foo')

    assert cm.exception.error == 'invalid'


def test_dict_invalid_2():
    """Wrong type for inner value"""

    test_dict = Dict(mapping={'foo': String()})

    with assert_raises(InvalidPropertyError) as cm:
        test_dict.validate({'foo': 3})

    assert cm.exception.error == 'invalid'


def test_dict_invalid_3():
    """Not in mapping"""

    test_dict = Dict(mapping={'foo': String()})

    with assert_raises(InvalidPropertyError) as cm:
        test_dict.validate({'bar': 'baz'})

    assert cm.exception.error == 'invalid'


def test_dict_valid_1():
    """Should be ok"""

    test_dict = Dict(mapping={'foo': String()})
    test_dict.validate({'foo': 'bar'})

    assert True


def test_boolean_invalid():
    """3 is boolean"""

    test_boolean = Boolean()

    with assert_raises(InvalidPropertyError) as cm:
        test_boolean.validate(3)

    assert cm.exception.error == 'invalid'


def test_boolean_valid_1():
    """True is ok"""

    test_boolean = Boolean()
    test_boolean.validate(True)

    assert True


def test_uuid_default():
    """None should be the default"""

    test_uuid = Uuid()
    assert test_uuid.default_value is None


class Author(Model):
    name = String()


class BlogPost(Model):
    id = Uuid(default=uuid4)
    title = String(validators=[min_length(3), max_length(100), regex(r'^([A-Za-z0-9- !.]*)$')])
    body = String(default=u'Lorem ipsum', error_key='text')
    meta_data = Dict(mapping={'corrector': String(), 'reviewer': String()})
    published = Boolean()
    likes = Integer(required=False)
    category = String(required=False)
    tags = List(inner=String(validators=[min_length(3)]), error_key='category')
    author = Object(object_class=Author)
    created_on = DateTime(default=datetime.now)
    updated_on = DateTime(default=datetime.now)

    @model_validator(error_key='category')
    def category_or_tags(self):
        assert self.tags is not None or self.category is not None, ERROR_REQUIRED


def test_model_invalid():
    """Invalid model"""

    test_blog_spot = BlogPost(id=u'ZUUZU', body=False, published='foo', meta_data={'foo': 'bar'})

    with assert_raises(InvalidModelError) as cm:
        test_blog_spot.validate()

    assert isinstance(cm.exception.errors, dict)
    assert len(cm.exception.errors) == 7
    assert 'id' in cm.exception.errors
    assert cm.exception.errors['id'] == 'invalid'
    assert 'title' in cm.exception.errors
    assert cm.exception.errors['title'] == 'required'
    assert 'author' in cm.exception.errors
    assert cm.exception.errors['author'] == 'required'
    assert 'category' in cm.exception.errors
    assert cm.exception.errors['category'] == 'required'
    assert 'text' in cm.exception.errors
    assert cm.exception.errors['text'] == 'invalid'
    assert 'published' in cm.exception.errors
    assert cm.exception.errors['published'] == 'invalid'
    assert 'meta_data' in cm.exception.errors
    assert cm.exception.errors['meta_data'] == 'invalid'


def test_model_valid():
    """Valid model"""

    test_blog_spot = BlogPost(title=u'Hello world !', tags=[u'foo', u'bar'], published=True, likes=8,
                              meta_data={'corrector': 'Pierre', 'reviewer': 'Moinax'}, author=Author(name='Pierre'))
    test_blog_spot.validate()

    assert test_blog_spot.body == u'Lorem ipsum'
