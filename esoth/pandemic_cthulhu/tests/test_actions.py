from ..actions import Walk, Bus, UseGate, DefeatCultist, DefeatShoggoth, GiveClueCard, GiveRelic, TakeClueCard, TakeRelic, Pass, PlayRelic, SealGate
from ..decks import Ithaqua, Azathoth, AtlatchNacha, ShudMell, YogSothoth, Hastor, Yigg, Dagon, \
    Tsathaggua, Nyarlothep, ShubNiggurath, ElderSign
from ..utils import REDUCED_CULTIST_RESERVE, ACTIVE_PLAYER_ONLY, MOVEMENT_RESTRICTION

from .base import PandemicCthulhuTestCase


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
        pass

    def test_sealgate(self):
        pass

    def test_givecluecard(self):
        pass

    def test_takecluecard(self):
        pass

    def test_giverelic(self):
        pass

    def test_takerelic(self):
        pass

    def test_usegateway(self):
        pass

    def test_pass(self):
        pass