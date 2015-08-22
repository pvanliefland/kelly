class Model(object):
    def __new__(cls, **kwargs):
        return super(Model, cls).__new__(cls, **kwargs)

    def validate(self):
        pass
