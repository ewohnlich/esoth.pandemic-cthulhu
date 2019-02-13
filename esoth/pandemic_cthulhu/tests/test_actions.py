from .base import PandemicCthulhuTestCase
from ..actions import Walk, Bus, DefeatCultist, DefeatShoggoth, GiveClueCard, GiveRelic, TakeRelic, TakeClueCard, \
    Pass, SealGate, UseGate
from ..decks import Relic


class ActionsCase(PandemicCthulhuTestCase):
    def test_walk(self):
        self.clear_board()
        action = Walk(self.game, self.player)
        self.assertTrue(action.available())
        self.assertEqual(self.player.location, 'Train Station')
        cost = action.run()
        self.assertEqual(self.player.location, 'Cafe')
        self.assertEqual(cost, 1)

    def test_bus(self):
        self.clear_board()
        action = Bus(self.game, self.player)
        self.assertEqual(self.player.location, 'Train Station')
        self.player.hand = ['Innsmouth', 'Innsmouth']
        self.assertTrue(action.available())
        cost = action.run()
        self.assertEqual(self.player.location, 'Junkyard')
        self.assertEqual(cost, 1)
        action.run()
        self.assertEqual(self.player.location, 'Train Station')
        self.assertFalse(action.available())

    def test_defeatcultist(self):
        self.clear_board()
        self.game.add_cultist(self.player.location)
        action = DefeatCultist(self.game, self.player)
        self.assertTrue(action.available())
        cost = action.run()
        self.assertEqual(cost, 1)
        self.assertFalse(action.available())

    def test_defeatshoggoth(self):
        self.clear_board()
        self.game.locations['Train Station'].shoggoth = 1
        action = DefeatShoggoth(self.game, self.player)
        self.assertFalse(action.available(1))
        self.assertTrue(action.available(4))
        cost = action.run()
        self.assertEqual(cost, 3)
        self.assertFalse(action.available(4))

    def test_sealgate(self):
        self.clear_board(True)
        action = SealGate(self.game, self.player)
        self.assertFalse(action.available())
        self.player.hand = ['Arkham'] * 5
        self.assertTrue(action.available())
        cost = action.run()
        self.assertEqual(cost, 1)
        self.assertFalse(action.available())

    def test_givecluecard(self):
        self.clear_board(True)
        action = GiveClueCard(self.game, self.player)
        self.assertFalse(action.available(remaining_actions=1))
        self.player.hand = ['Dunwich']
        self.assertFalse(action.available(remaining_actions=1))
        self.player.hand = ['Arkham']
        self.assertTrue(action.available(remaining_actions=1))
        action.run()
        self.assertEqual(self.player1.hand, [])
        self.assertEqual(self.player2.hand, ['Arkham'])

    def test_takecluecard(self):
        self.clear_board(True)
        action = TakeClueCard(self.game, self.player)
        self.assertFalse(action.available(remaining_actions=1))
        self.player2.hand = ['Dunwich']
        self.assertFalse(action.available(remaining_actions=1))
        self.player2.hand = ['Arkham']
        self.assertTrue(action.available(remaining_actions=1))
        cost = action.run()
        self.assertEqual(cost, 1)
        self.assertEqual(self.player1.hand, ['Arkham'])
        self.assertEqual(self.player2.hand, [])

    def test_giverelic(self):
        self.clear_board(True)
        action = GiveRelic(self.game, self.player)
        self.assertFalse(action.available())
        self.game.draw_relic_card(self.player)
        self.assertTrue(action.available())
        cost = action.run()
        self.assertEqual(cost, 1)
        self.assertFalse(action.available())
        self.assertEqual(len(self.player.hand), 0)
        self.assertEqual(len(self.player2.hand), 1)
        self.assertTrue(isinstance(self.player2.hand[0], Relic))

    def test_takerelic(self):
        self.clear_board(True)
        action = TakeRelic(self.game, self.player)
        self.assertFalse(action.available())
        self.game.draw_relic_card(self.player2)
        self.assertTrue(action.available())
        cost = action.run()
        self.assertEqual(cost, 1)
        self.assertFalse(action.available())
        self.assertEqual(len(self.player2.hand), 0)
        self.assertEqual(len(self.player.hand), 1)
        self.assertTrue(isinstance(self.player.hand[0], Relic))

    def test_usegateway(self):
        self.clear_board(True)
        action = UseGate(self.game, self.player)
        self.assertFalse(action.available())
        self.player.location = 'Park'
        self.assertTrue(action.available())
        cost = action.run()
        self.assertEqual(cost, 1)
        self.assertEqual(self.player.location, 'Old Mill')

    def test_pass(self):
        action = Pass(self.game, self.player)
        self.assertTrue(action.available())
        cost = action.run()
        self.assertEqual(cost, 1)
