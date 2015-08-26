class Model(object):
    """Base model class - only used to provide a signature"""

    def __new__(cls, **kwargs):
        return super(Model, cls).__new__(cls)

    def __init__(self, **kwargs):
        super(Model, self).__init__()

    def validate(self):
        pass
