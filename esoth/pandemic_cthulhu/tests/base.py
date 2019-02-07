from unittest import TestCase
from esoth.pandemic_cthulhu.game import GameBoard


class PandemicCthulhuTestCase(TestCase):
    def setUp(self):
        self.game = GameBoard(2)
