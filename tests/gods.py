from .base import PandemicCthulhuTestCase
from decks import Ithaqua


class GodCase(PandemicCthulhuTestCase):
    def test_tthaqua(self):
        game = self.game
        game.locations['Train Station'].cultists = 2
        game.old_gods[0] = Ithaqua()
        game.awakening_ritual()
        game.locations['Train Station'].cultists = 2
        assert False  # todo