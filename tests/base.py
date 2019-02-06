from unittest import TestCase
from game import GameBoard


class PandemicCthulhuTestCase(TestCase):
    def setUp(self):
        self.game = GameBoard(2)
