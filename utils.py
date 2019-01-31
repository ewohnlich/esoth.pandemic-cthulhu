SEAL_GATE_BASE_COST = 5
SANITY_BASE = 4
DEFEAT_SHOGGOTH_COST = 3
ACTIONS_BASE = 4
AUTO_ASSIGNMENT = True  # automatically set roles if true, easier for testing


class PandemicObject(object):
    name = ''

    def __init__(self, name=''):
        self.name = name

    def __repr__(self):
        name = self.name
        if callable(name):
            name = name()
        return '<{}: {}>'.format(self.__class__.__name__, name)

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
            element = opt
            if attr:
                if hasattr(opt, attr):
                    element = getattr(opt, attr)
                if isinstance(opt, dict):
                    element = opt[attr]
            if callable(element):
                element = element()
            opts.append('({}) {}'.format(idx + 1, element))
        opts = ' '.join(opts)

        raw = input('{}: {}: '.format(prompt, opts))
        try:
            selection = options[int(raw) - 1]
        except ValueError:
            print('Not a valid option')
        except IndexError:
            print('Not a valid option')
    return selection
