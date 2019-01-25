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


def get_input(options, attr, prompt):
    """ Prompt the user for a selection
    
    :param options: actual python objects to be chosen
    :param attr: when displaying options, use this attribute of an element in options
    :param prompt: prompt text
    :return: 
    """
    selection = None
    while not selection:
        opts = []
        for idx, opt in enumerate(options):
            element = hasattr(opt, attr) and getattr(opt, attr) or opt[attr]
            opts.append('({}) {}'.format(idx + 1, element))
        opts = ' '.join(opts)

        try:
            selection = options[int(input('{}: {}: '.format(prompt, opts))) - 1]
        except ValueError:
            print('Not a valid option')
        except IndexError:
            print('Not a valid option')
    return selection
