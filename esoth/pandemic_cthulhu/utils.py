import os

SEAL_GATE_BASE_COST = 5
SANITY_BASE = 4
DEFEAT_SHOGGOTH_COST = 3
ACTIONS_BASE = 4
SKIP_SUMMON = 'Skip summon'
SKIP_SANITY_CHECKS = 'Skip sanity checks'
REDUCE_SEAL_COST = 'Reduce seal cost by 1'
INCREASE_SEAL_COST = 'Seal requires connected town card'
ACTIVE_PLAYER_ONLY = 'Only active player can play relics'
REDUCED_CULTIST_RESERVE = 'Reduced cultist reserve'
MOVEMENT_RESTRICTION = 'Must defeat cultists to move if 2 or more'
DISALLOW_GATE = 'Can no longer use gates'
AUTOMATE_INPUT = 'Automate input'

DETECTIVE = 'Detective'
MAGICIAN = 'Magician'
DOCTOR = 'Doctor'
DRIVER = 'Driver'
HUNTER = 'Hunter'
OCCULTIST = 'Occultist'
REPORTER = 'Reporter'


def automate():
    return os.environ.get(AUTOMATE_INPUT)


class PandemicObject(object):
    name = ''

    def __init__(self, name=''):
        if name:
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


def get_input(options, attr, prompt, force=False):
    """ Prompt the user for a selection
    
    :param options: actual python objects to be chosen
    :param attr: when displaying options, use this attribute of an element in options
    :param prompt: prompt text
    :param force: if there's only one option, it will just be returned unless this is true
    :return: 
    """
    if automate():
        return options[0]
    if not force:
        if len(options) == 1:
            return options[0]
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


def confirm(pre=''):
    # if pre:
    #     input(pre + ' Hit any key to continue')
    # else:
    #     input('Hit any key to continue')
    return


def get_num_players(game):
    if not game.num_players:
        if game.mode == 'cli':
            num_players = input('Number of players [2/3/4]: ')
            while num_players not in map(str, range(1, 5)):
                num_players = input('Invalid number. Number of players [2/3/4]:')
            num_players = int(num_players)
        else:
            num_players = 2
        game.num_players = num_players
