import inspect
import sys
from collections import deque
from random import shuffle

from .utils import PandemicObject, SKIP_SUMMON, SKIP_SANITY_CHECKS, REDUCE_SEAL_COST, ACTIVE_PLAYER_ONLY, \
    REDUCED_CULTIST_RESERVE, MOVEMENT_RESTRICTION, INCREASE_SEAL_COST, get_input, SANITY_BASE


class PandemicCard(PandemicObject):
    name = ''
    text = ''

    def __init__(self, name='', text=''):
        super(PandemicCard, self).__init__(name=name)
        if text:
            self.text = text

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.name)

    def activate(self, game, player):
        pass


class OldGod(PandemicCard):
    revealed = False
    effect = None  # infinity symbol ongoing effect

    def activate(self, game, player=None):
        print('** {} has been revealed! {} **'.format(self.name, self.text))
        self.revealed = True


class Ithaqua(OldGod):
    name = 'Ithaqua'
    text = 'To walk out of a location with 2 or more cultists, a player must first defeat a Cultist at that location'
    effect = MOVEMENT_RESTRICTION

    def activate(self, game, player=None):
        super(Ithaqua, self).activate(game, player)
        game.effects.append(self.effect)


class Azathoth(OldGod):
    name = 'Azathoth'
    text = 'Remove 3 cultists from the unused supply'
    effect = REDUCED_CULTIST_RESERVE

    def activate(self, game, player=None):
        super(Azathoth, self).activate(game, player)
        game.cultist_reserve -= 3
        game.effects.append(self.effect)


class AtlatchNacha(OldGod):
    name = 'Atlatch-Nacha'
    text = 'Each investigator puts 1 cultist on their location unless they choose to lose 1 sanity. An investigator ' \
           'may not lose their last sanity token to prevent this cultist placement.'

    def activate(self, game, player=None):
        super(AtlatchNacha, self).activate(game, player)
        for player in game.players:
            if player.sanity <= 1:
                game.add_cultist(player.location)
            else:
                choices = ['Lose 1 sanity', 'Put a cultist on their location']
                choice = get_input(choices, None, 'Choice for {}'.format(player.name()))
                if choices.index(choice) == 0:
                    player.sanity -= 1
                else:
                    game.add_cultist(player.location)


class ShudMell(OldGod):
    name = 'Shud\'Mell'
    text = 'All players collectively lose 3/4/5 sanity tokens [with 2/3/4 players].'

    def activate(self, game, player=None):
        super(ShudMell, self).activate(game, player)
        pool = len(game.players) + 1
        sane_players = [player for player in game.players if player.sanity]
        while sane_players and pool:
            try:
                opts = ' '.join(
                    ['({}) {}[{}]'.format(idx + 1, player.name(), player.sanity) for idx, player in
                     enumerate(sane_players)])
                choice = input(
                    'You must collectively lose {} more sanity. Which player should lose the next one? {}: '.format(
                        pool,
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


class YogSothoth(OldGod):
    name = 'Yog-Sothoth'
    text = 'Playing Relic cards can only be done by the active player.'
    effect = ACTIVE_PLAYER_ONLY

    def activate(self, game, player=None):
        super(YogSothoth, self).activate(game, player)
        game.effects.append(self.effect)


class Hastor(OldGod):
    name = 'Hastor'
    text = 'Draw the bottom card from the Summoning deck. Place 1 Shoggoth on that location. Discard that card to ' \
           'the Summoning discard pile. Then move each Shoggoth 1 location closer to the nearest open gate.'

    def activate(self, game, player=None):
        super(Hastor, self).activate(game, player)
        game.summon_shoggoth()
        game.move_shoggoths()


class Yigg(OldGod):
    name = 'Yigg'
    text = 'Sealing gates requires 1 additional Clue card from a connected town.'
    effect = INCREASE_SEAL_COST

    def activate(self, game, player=None):
        super(Yigg, self).activate(game, player)
        game.effects.append(self.effect)


class Dagon(OldGod):
    name = 'Dagon'
    text = 'Place 1 cultist on each gate location.'

    def activate(self, game, player=None):
        super(Dagon, self).activate(game, player)
        for location in game.locations.values():
            if location.gate:
                game.add_cultist(location.name)


class Tsathaggua(OldGod):
    name = 'Tsathaggua'
    text = 'All players collectively discard 2/3/4 cards [with 2/3/4 players].'

    def activate(self, game, player=None):
        super(Tsathaggua, self).activate(game, player)
        pool = len(game.players)
        while pool:
            player = get_input(game.players, 'name',
                               'You must collectively lose {} more card(s). Which player '
                               'should lose the next one?: '.format(pool))
            discard = get_input(player.hand, None, 'Pick a card to discard')
            player.hand.remove(discard)
            game.discard(discard)
            player.sanity -= 1
            pool -= 1


class Nyarlothep(OldGod):
    name = 'Nyarlothep'
    text = 'Investigators may no longer do the Use a Gate action.'
    effect = MOVEMENT_RESTRICTION

    def activate(self, game, player=None):
        super(Nyarlothep, self).activate(game, player)
        game.effects.append(self.effect)


class ShubNiggurath(OldGod):
    name = 'Shub-Niggurath'
    text = 'Draw 4 cards from the bottom of the Summoning.'

    def activate(self, game, player=None):
        super(ShubNiggurath, self).activate(game, player)
        for i in range(4):
            game.draw_summon()


class Relic(PandemicCard):
    """ relic. Relics subclass this instead of providing an action """
    name = 'Relic'
    text = 'NYI'

    def __init__(self):
        pass

    def playable(self, game):
        return True

    def play(self, game, player):
        """ play the card

        :param game: game
        :param player: player using the card, not necessarily the active player
        :return: action cost
        """
        game.sanity_roll(player)
        return 0

    def __repr__(self):
        return 'Relic: {}'.format(self.name)


class AlienCarving(Relic):
    name = 'Alien Carving'
    text = 'The active player can take 3 extra actions this turn'

    def play(self, game, player):
        super(AlienCarving, self).play(game, player)
        game.sanity_roll(player)
        return -3


class BizarreStatue(Relic):
    name = 'Bizarre Statue'
    text = 'Skip the next Summoning step. [Do not flip over any Summoning cards.]'

    def play(self, game, player):
        super(BizarreStatue, self).play(game, player)
        game.effects.append(SKIP_SUMMON)
        return 0


class MiGoEye(Relic):
    name = 'Mi-Go Eye'
    text = 'The next gate requires one fewer Clue card to seal. Put this card next to the Player discard pile and ' \
           'discard it when the next gate is sealed'

    def play(self, game, player):
        super(MiGoEye, self).play(game, player)
        game.effects.append(REDUCE_SEAL_COST)
        return 0


class WardedBox(Relic):
    name = 'Warded Box'
    text = 'No sanity roll required to play this card. Until the end of your next turn, players need not do ' \
           'sanity rolls. Place this card in front of you as a reminder'

    def play(self, game, player):
        game.effects.append(SKIP_SANITY_CHECKS)
        game.effect_tracker[SKIP_SANITY_CHECKS] = len(game.players) + 1


class XaosMirror(Relic):
    name = 'Xaos Mirror'
    text = 'You can swap one Clue card from your hand with a Clue card in another player\'s hand regardless of where ' \
           'either of you are'

    def play(self, game, player):
        super(XaosMirror, self).play(game, player)
        teammate = get_input([p for p in game.players if p is not player], 'name', 'Who do you want to swap with?')
        curr_discard = get_input([card for card in player.hand if card != self], None, 'Which card are you swapping?')
        their_discard = get_input([card for card in teammate.hand if card != self], None,
                                  'Which card are you taking from them?')
        player.hand.append(their_discard)
        player.hand.remove(curr_discard)
        teammate.hand.append(curr_discard)
        teammate.hand.remove(their_discard)
        return 0


class SilverKey(Relic):
    name = 'Silver Key'
    text = 'The active player can instantly move to any location on the board'

    def play(self, game, player):
        super(SilverKey, self).play(game, player)
        town = get_input(game.towns, 'name', 'You can move anywhere. First, select a town')
        destination = get_input([l for l in town.locations], 'name', 'Select a location within {}'.format(town.name))
        game.move_player(destination.name)
        return 0


class SongOfKadath(Relic):
    name = 'Song of Kadath'
    text = 'No sanity roll required to play this card. Choose one: all players regain 1 sanity token ' \
           'or one player regains full sanity.'

    def play(self, game, player):
        """ no super, no sanity roll """
        choices = ['All players regain 1 sanity', 'One player regains full sanity']
        choice = get_input(choices, None, 'Choose one')
        if choices.index(choice) == 0:
            for player in game.players:
                player.sanity = min(SANITY_BASE, player.sanity + 1)
        else:
            player = get_input(game.players, 'name', 'Who gets this privilege?')
            player.sanity = SANITY_BASE
        return 0


class ElderSign(Relic):
    name = 'Elder Sign'
    text = 'Pick a town. If its gate has been sealed no new cultist or Shoggoth may be placed in that town. As a ' \
           'reminder, flip the Seal token to show the Elder Sign'

    def playable(self, game):
        return [town for town in game.towns if town.sealed]

    def play(self, game, player):
        town = get_input(self.playable(game), 'name', 'Which town will you seal?')
        town.elder_sign = True


class BookOfShadow(Relic):
    name = 'Book of Shadow'
    text = 'Draw, look at, and rearrange the top 4 cards of the Player deck. Put them back on top'

    def play(self, game, player):
        raise NotImplementedError  # lots of input, ugh


class LastHourglass(Relic):
    name = 'Last Hourglass'
    text = 'The active player may take any Clue card from the Player discard pile.'

    def playable(self, game):
        return sorted({card for card in game.player_discards if not isinstance(card, Relic)})

    def play(self, game, player):
        clue = get_input(self.playable(game), None, 'Select a Clue card')
        game.player_discards.remove(clue)
        game.current_player.hand.append(clue)
        game.current_player.limit_hand(game)


class SealOfLeng(Relic):
    name = 'Seal of Leng'
    text = 'You may choose a revealed <infinity> Old One and cancel it\'s effect for the rest of the game. ' \
           'Cover that Old One\'s effect with this card as a reminder.'

    def play(self, game, player):
        raise NotImplementedError


class AlhazredsFlame(Relic):
    name = 'Alhazred\'s Flame'
    text = 'You may remove up to 4 cultists or 1 Shoggoth from anywhere on the board'

    def play(self, game, player):
        raise NotImplementedError


def get_old_gods():
    def is_god_class(value):
        return inspect.isclass(value) and issubclass(value, OldGod) and value is not OldGod

    # don't initialize god class until we've shuffeld and got five randos
    gods = [god_class for name, god_class in inspect.getmembers(sys.modules[__name__], is_god_class)]
    shuffle(gods)
    cthulhu = OldGod('Cthulhu', 'The world is plunged into an age of madness, chaos, and destruction. You have lost')
    return [god() for god in gods[:5]] + [cthulhu]


def get_relics():
    def is_relic_class(value):
        return inspect.isclass(value) and issubclass(value, Relic) and value is not Relic

    relics = [relic_class() for name, relic_class in inspect.getmembers(sys.modules[__name__], is_relic_class)]
    shuffle(relics)
    return relics


town_deck = ['Kingsport', 'Innsmouth', 'Dunwich', 'Arkham'] * 11


def get_player_relic_decks(num_players=2):
    relics = get_relics()
    player_deck = town_deck + relics[:2 + num_players]
    shuffle(player_deck)
    relics = relics[2 + num_players:]
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

    def activate(self, game, player):
        # 1. Fight the madness
        game.sanity_roll(player)

        # 2. Awakening
        game.awakening_ritual()

        # 3. A Shoggoth appears
        game.summon_shoggoth()

        # 4. Cultists regroup
        game.regroup_cultists()


class Role(PandemicObject):
    name = ''
    action_modifier = 0
    seal_modifier = 0
    clear_all_cultists = False
    move_modifier = False

    def __init__(self, name, **kwargs):
        super(Role, self).__init__(name)
        for k, v in kwargs.items():
            setattr(self, k, v)


class RoleManager(object):
    roles = []
    active_role = None

    def __init__(self):
        self.roles = [
            Role(name='Detective', seal_modifier=1),
            Role(name='Doctor', action_modifier=1),
            Role(name='Driver', move_modifier=True),
            Role(name='Hunter', clear_all_cultists=True),
            Role(name='Magician'),
            Role(name='Occultist'),
            Role(name='Reporter'),
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
