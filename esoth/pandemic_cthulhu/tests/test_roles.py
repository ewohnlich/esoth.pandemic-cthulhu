from .base import PandemicCthulhuTestCase
from ..actions import MoveCultist, SealGate, GiveClueCard
from ..utils import DETECTIVE, OCCULTIST


class ActionsCase(PandemicCthulhuTestCase):
    def test_detective(self):
        self.clear_board()
        self.player.role = DETECTIVE
        action = SealGate(self.game, self.player)
        self.player.location = 'Park'
        self.assertFalse(action.available())
        self.player.hand = ['Arkham'] * 4
        self.assertTrue(action.available())

    def test_insane_detective(self):
        self.player1.role = DETECTIVE
        self.player1.sanity = 0
        self.player1.hand = ['Arkham']
        self.player2.hand = []
        action = GiveClueCard(self.game, self.player1)
        cost = action.run()
        self.assertEqual(self.player1.hand, [])
        self.assertEqual(self.player2.hand, ['Arkham'])
        self.assertEqual(cost, 2)

    def test_occultist(self):
        self.clear_board()
        self.player.role = OCCULTIST
        self.game.locations['Graveyard'].cultists = 1
        action = MoveCultist(self.game, self.player)
        self.assertTrue(action.available())
        cost = action.run()
        self.assertEqual(self.game.locations['Graveyard'].cultists, 0)
        self.assertEqual(self.game.locations['Market'].cultists, 1)
        self.assertEqual(cost, 1)


