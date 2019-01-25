from random import shuffle
from collections import deque
import inspect

from utils import PandemicObject


class PandemicCard(PandemicObject):
    name = ''
    text = ''
    action = None

    def __init__(self, name='', text='', action=None):
        super(PandemicCard, self).__init__(name=name)
        self.text = text
        self.action = action

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.name)

    def activate(self, board, player):
        if inspect.isfunction(self.action):
            self.action(board, player)


class OldGod(PandemicCard):
    revealed = False
    recurring = True

    def __init__(self, name, text, action=None, recurring=False):
        super(OldGod, self).__init__(name, text, action)
        self.recurring = recurring

    def activate(self, board, player=None):
        print('** {} has been revealed! {} **'.format(self.name, self.text))
        super(OldGod, self).activate(board, player)
        if self.recurring:
            board.effects.append(self.name)


class Relic(PandemicCard):
    """ relic """


def azathoth_action(board, player=None):
    board.cultist_reserve -= 3


def hastor_action(board, player=None):
    board.summon_shoggoth()
    board.move_shoggoths()


def dagon_action(board, player=None):
    for location in board.locations.values():
        if location.gate:
            board.add_cultist(location.name)


def tsathaggua_action(board, player=None):
    raise NotImplementedError


def shubniggurath_action(board, player=None):
    for i in range(4):
        board.draw_summon()


def shudmell_action(board, player=None):
    pool = len(board.players) + 1
    sane_players = [player for player in board.players if player.sanity]
    while sane_players and pool:
        try:
            opts = ' '.join(
                ['({}) {}[{}]'.format(idx + 1, player.name, player.sanity) for idx, player in enumerate(sane_players)])
            choice = input(
                'You must collectively lose {} more sanity. Which player should lose the next one? {}: '.format(pool,
                                                                                                                opts))
            player = sane_players[int(choice) - 1]
            player.sanity -= 1
            pool -= 1
        except ValueError:
            print('Not a valid option')
        except IndexError:
            print('Not a valid option')
    if pool and not sane_players:
        print('No more players can afford to lose a sanity point')


def alien_carving(board, player):
    board.sanity_roll(player)
    player.effects.append('Alien Carving')


def relic_action(board, player):
    raise NotImplementedError


def get_old_gods():
    gods = [
        OldGod('Ithaqua', 'To walk out of a location with 2 or more cultists, a player must first defeat a Cultist at '
                          'that location', recurring=True),
        OldGod('Azathoth', 'Remove 3 cultists from the unused supply', action=azathoth_action, recurring=True),
        OldGod('Atlatch-Nacha', 'Each investigator puts 1 cultist on their location unless they choose to lose 1 '
                                'sanity. An investigator may not lose their last sanity token to prevent this cultist '
                                'placement.'),
        OldGod('Shud\'Mell', 'All players collectively lose 3/4/5 sanity tokens [with 2/3/4 players].',
               action=shudmell_action),
        OldGod('Yog-Sothoth', 'Playing Relic cards can only be done by the active player.', recurring=True),
        OldGod('Hastor', 'Draw the bottom card from the Summoning deck. Place 1 Shoggoth on that location.'
                         'Discard that card to the Summoning discard pile. Then move each Shoggoth 1 location closer '
                         'to the nearest open gate.', action=hastor_action),
        OldGod('Yigg', 'Sealing gates requires 1 additional Clue card from a connected town.', recurring=True),
        OldGod('Dagon', 'Place 1 cultist on each gate location.', action=dagon_action),
        OldGod('Tsathaggua', 'All players collectively discard 2/3/4 cards [with 2/3/4 players].',
               action=tsathaggua_action),
        OldGod('Nyarlothep', 'Investigators may no longer do the Use a Gate action.'),
        OldGod('Shub-Niggurath', 'Draw 4 cards from the bottom of the Summoning.', action=shubniggurath_action),
    ]
    shuffle(gods)
    cthulhu = OldGod('Cthulhu', 'The world is plunged into an age of madness, chaos, and destruction. You have lost',
                     recurring=True)
    return gods[:5] + [cthulhu]


def get_relics():
    relics = [
        Relic('Alien Carving', 'The active player can take 3 extra actions this turn', action=alien_carving),
        Relic('Mi-Go Eye', 'The next gate requires one fewer Clue card to seal. Put this card next to the Player '
                           'discard pile and discard it when the next gate is sealed', action=relic_action),
        Relic('Bizarre Statue', 'Skp the next Summoning step. [Do not flip over any Summoning cards.]',
              action=relic_action),
        Relic('Warded Box', 'No sanity roll required to play this card. Until the end of your next turn, players '
                            'need not do sanity rolls. Place this card in front of you as a reminder',
              action=relic_action),
        Relic('Xaos Mirror', 'You can swap one Clue card from your hand with a Clue card in another player\'s hand, '
                             'regardless of where either of you are', action=relic_action),
        Relic('Silver Key', 'The active player can instantly move to any location on the board', action=relic_action),
        Relic('Song of Kadath', 'No sanity roll required to play this card. Choose one: all players regain 1 sanity '
                                'token or one player regains full sanity.', action=relic_action),
        Relic('Book of Shadow', 'Draw, look at, and rearrange the top 4 cards of the Player deck. Put them back on top',
              action=relic_action),
        Relic('Last Hourglass', 'The active player may take any Clue card from the Player discard pile.',
              action=relic_action),
        Relic('Seal of Leng', 'You may choose a revealed <infinity> Old One and cancel it\'s effect for the rest of '
                              'the game. Cover that Old One\'s effect with this card as a reminder.',
              action=relic_action),
        Relic('Elder Sign',
              'Pick a town. If its gate has been sealed no new cultist or Shoggoth may be placed in that town. As a '
              'reminder, flip the Seal token to show the Elder Sign',
              action=relic_action),
        Relic('Alhazred\'s Flame', 'You may remove up to 4 cultists or 1 Shoggoth from anywhere on the board',
              action=relic_action),
    ]
    shuffle(relics)
    return relics


town_deck = ['Kingsport', 'Innsmouth', 'Dunwich', 'Arkham'] * 11


def get_player_relic_decks(num_players=2):
    relics = get_relics()
    player_deck = town_deck + relics[:2 + num_players]
    shuffle(player_deck)
    relics = relics[2 + num_players]
    return player_deck, relics


class SummonCard(PandemicObject):
    name = ''
    shoggoths = False

    def __init__(self, name, shoggoths=False):
        super(SummonCard, self).__init__(name=name)
        self.shoggoths = shoggoths

    def __repr__(self):
        shog = self.shoggoths and '(*)' or ''
        return '<{}: {}{}>'.format(self.__class__.__name__, self.name, shog)


def get_summon_deck():
    cards = deque([
        SummonCard('Wharf'),
        SummonCard('University', True),
        SummonCard('Old Mill'),
        SummonCard('Woods', True),
        SummonCard('Park'),
        SummonCard('Market'),
        SummonCard('Historic Inn', True),
        SummonCard('Church'),
        SummonCard('Diner'),
        SummonCard('Cafe'),
        SummonCard('Docks', True),
        SummonCard('Graveyard'),
        SummonCard('Factory'),
        SummonCard('Theater'),
        SummonCard('Swamp', True),
        SummonCard('Police Station'),
        SummonCard('Hospital'),
        SummonCard('Great Hall', True),
        SummonCard('Boardwalk'),
        SummonCard('Secret Lodge', True),
        SummonCard('Train Station'),
        SummonCard('Junkyard'),
        SummonCard('Pawn Shop', True),
        SummonCard('Farmstead'),
    ])
    shuffle(cards)
    return cards


class EvilStirs(PandemicCard):
    name = 'Evil Stirs'

    def __init__(self):
        return

    def activate(self, board, player):
        # 1. Fight the madness
        board.sanity_roll(player)

        # 2. Awakening
        board.awakening_ritual()

        # 3. A Shoggoth appears
        board.summon_shoggoth()

        # 4. Cultists regroup
        board.regroup_cultists()


class Role(PandemicObject):
    name = ''
    action_modifier = 0
    clear_all_cultists = False

    def __init__(self, name, **kwargs):
        super(Role, self).__init__(name)
        for k, v in kwargs.items():
            setattr(self, k, v)


class RoleManager(object):
    roles = []
    active_role = None

    def __init__(self):
        self.roles = [
            Role(name='Detective'),
            Role(name='Doctor', action_modifier=1),
            Role(name='Driver'),
            Role(name='Hunter', clear_all_cultists=True),
            Role(name='Magician'),
            Role(name='Occultist'),
            Role(name='Report'),
        ]
        self.shuffle()
        self.active_role = self.roles.pop()

    def shuffle(self):
        roles = self.roles
        shuffle(roles)
        self.roles = roles

    def assign_role(self, player, auto=False):
        if auto:
            self.shuffle()
            player.role = self.roles.pop()
            return

        choice = None
        choices = [self.active_role, self.roles.pop()]
        while not choice:
            try:
                choice = choices[
                    int(input('Select a role: (1) {} or (2) {}: '.format(*[role.name for role in choices]))) - 1]
                del choices[choices.index(choice)]
                self.active_role = choices[0]
            except IndexError:
                print('Not a valid option')
            except ValueError:
                print('Not a valid option')
        player.role = choice
