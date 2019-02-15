from .base import PandemicCthulhuTestCase


class GameCase(PandemicCthulhuTestCase):

    def test_shogmove(self):
        self.clear_board()
        self.game.locations['University'].shoggoth = 1
        self.game.move_shoggoths()
        self.assertEqual(self.game.locations['Park'].shoggoth, 1)
        self.assertEqual(self.game.locations['University'].shoggoth, 0)

    def test_lose_condition_sanity(self):
        for player in self.game.players:
            player.sanity = -1
        self.assertTrue(self.game.game_over())
        self.game.play()
        self.assertIn('You have lost', self.game.stream.getvalue())
        self.assertIn('All players are insane', self.game.stream.getvalue())
