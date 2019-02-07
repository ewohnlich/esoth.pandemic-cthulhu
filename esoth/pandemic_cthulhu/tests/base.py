from io import StringIO
from unittest import TestCase

from esoth.pandemic_cthulhu.game import GameBoard


class PandemicCthulhuTestCase(TestCase):
    def setUp(self):
        self.game = GameBoard(num_players=2, stream=StringIO())
        self.player = self.game.players[0]

    def clear_board(self):
        for location in self.game.locations.values():
            location.cultists = 0
            location.shoggoth = 0
