from .base import PandemicCthulhuTestCase


class GameCase(PandemicCthulhuTestCase):

    def test_shogmove(self):
        self.clear_board()
        self.game.locations['University'].shoggoth = 1
        self.game.move_shoggoths()
        self.assertEqual(self.game.locations['Park'].shoggoth, 1)
        self.assertEqual(self.game.locations['University'].shoggoth, 0)
