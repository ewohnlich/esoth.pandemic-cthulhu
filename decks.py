from random import shuffle
import inspect
import sys


class OldGod(object):
    text = ''
    revealed = False

    @property
    def name(self):
        return self.__class__.__name__

    def activate(self, board):
        pass


class Ithaqua(OldGod):
    text = 'To walk out of a location 2 or more cultists, a player must first defeat a Cultist at that location'

    def activate(self, board):
        board.effects.append(self.name)


class Azathoth(OldGod):
    text = 'Remove 3 cultists from the unused supply'

    def activate(self, board):
        board.effects.append(self.name)
        board.cultist_reserve -= 3


class ShuddeMell(OldGod):
    text = 'All players collectively lose 3/4/5 sanity tokens [with 2/3/4 players].'

    @property
    def name(self):
        return 'Shudd\'Mell'

    def activate(self, board):
        raise NotImplementedError
        # needs player input


class AtlatchNacha(OldGod):
    text = 'Each investigator puts 1 cultist on their location unless they choose to lose 1 sanity. An investigator ' \
           'may not lose their last sanity token to prevent this cultist placement.'

    @property
    def name(self):
        return 'Atlatch-Nada'

    def activate(self, board):
        raise NotImplementedError
        # needs player input


class YogSothoth(OldGod):
    text = 'Playing Relic cards can only be done by the active player.'

    @property
    def name(self):
        return 'Yog-Sothoth'

    def activate(self, board):
        board.effects.append(self.name)


class Hastor(OldGod):
    text = 'Draw the bottom card from the Summoning deck. Place 1 Shoggoth on that location. Discard that card to ' \
           'the Summoning discard pile. Then move each Shoggoth 1 location closer to the nearest open gate.'

    def activate(self, board):
        raise NotImplementedError


class Yig(OldGod):
    text = 'Sealing gates requires 1 additional Clue card from a connected town.'

    def activate(self, board):
        board.effects.append(self.name)


class Dagon(OldGod):
    text = 'Place 1 cultist on each gate location.'

    def activate(self, board):
        raise NotImplementedError


class Tsathoggua(OldGod):
    text = 'All players collectively discard 2/3/4 cards [with 2/3/4 players].'

    def activate(self, board):
        raise NotImplementedError


class Nyarlathotep(OldGod):
    text = 'Investigators may no longer do the Use a Gate action.'

    def activate(self, board):
        board.effects.append(self.name)


class ShubNiggurath(OldGod):
    text = 'Draw 4 cards from the bottom of the Summoning.'

    @property
    def name(self):
        return 'Shub-Niggurath'

    def activate(self, board):
        raise NotImplementedError


class Cthulhu(OldGod):
    text = 'The world is plunged into an age of madness, chaos, and destruction. You have lost'

    def activate(self, board):
        board.effects.append(self.name)


def get_old_gods():
    def is_god(klass):
        return inspect.isclass(klass) and issubclass(klass, OldGod) and klass is not OldGod

    gods = [god[1]() for god in inspect.getmembers(sys.modules[__name__], is_god)]
    shuffle(gods)
    return gods[:5] + [Cthulhu()]


town_deck = []
