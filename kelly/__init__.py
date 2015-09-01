# -*- coding: utf-8 -*-

""""
kelly
~~~~~

The Kelly library allows you to model your domain objects in a declarative, pure-python fashion.

"""

from models import Model
from properties import Property, String, Integer, DateTime, Uuid, List, Dict, Boolean, Object, Constant
from validators import choices, min_length, max_length, regex, model_validator
from errors import *
