class PandemicObject(object):
    name = ''

    def __init__(self, name=''):
        self.name = name

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.name)

    def __lt__(self, other):
        if isinstance(other, PandemicObject):
            other = other.__repr__()
        return self.__repr__() < other

    def __gt__(self, other):
        if isinstance(other, PandemicObject):
            other = other.__repr__()
        return self.__repr__() > other
