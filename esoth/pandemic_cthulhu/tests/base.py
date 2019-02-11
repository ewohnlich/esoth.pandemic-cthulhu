from io import StringIO
from unittest import TestCase
import os

from esoth.pandemic_cthulhu.game import GameBoard
from esoth.pandemic_cthulhu.decks import OldGod
from esoth.pandemic_cthulhu.utils import AUTOMATE_INPUT


class PandemicCthulhuTestCase(TestCase):
    def setUp(self):
        os.environ[AUTOMATE_INPUT] = 'true'
        self.game = GameBoard(num_players=2, stream=StringIO())
        self.player = self.game.players[0]
        self.player1 = self.player
        self.player2 = self.game.players[1]
        for player in self.game.players:
            player.role = 'Dummy'
        self.dummy_gods()

    def clear_board(self, hands=False):
        for location in self.game.locations.values():
            location.cultists = 0
            location.shoggoth = 0

        if hands:
            for player in self.game.players:
                player.hand = []

    def dummy_gods(self):
        """ some events can chain, and we want to ignore any events that spawn more gods and need a prompt """
        self.game.old_gods = []
        for i in range(6):
            self.game.old_gods.append(OldGod(self.game))
