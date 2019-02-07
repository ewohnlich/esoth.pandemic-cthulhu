from esoth.pandemic_cthulhu.actions import Walk
from esoth.pandemic_cthulhu.decks import Ithaqua

from .base import PandemicCthulhuTestCase


class GodCase(PandemicCthulhuTestCase):
    def test_tthaqua(self):
        game = self.game
        game.locations['Train Station'].cultists = 2
        game.old_gods[0] = Ithaqua()
        game.awakening_ritual()
        game.locations['Train Station'].cultists = 2
        action = Walk(game, game.players[0])
        self.assertFalse(action.available())
