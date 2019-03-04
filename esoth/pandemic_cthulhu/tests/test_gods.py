from .base import PandemicCthulhuTestCase
from ..actions import Walk, DefeatCultist, PlayRelic, SealGate, UseGate
from ..decks import Ithaqua, Azathoth, AtlatchNacha, ShudMell, YogSothoth, Hastor, Yigg, Dagon, \
    Tsathaggua, Nyarlothep, ShubNiggurath, ElderSign
from ..utils import REDUCED_CULTIST_RESERVE, ACTIVE_PLAYER_ONLY, DISALLOW_GATE


class GodCase(PandemicCthulhuTestCase):
    def test_ithaqua(self):
        self.game.locations[self.player.location].cultists = 2
        Ithaqua(self.game).activate()
        action = Walk(self.game, self.player)
        self.assertFalse(action.available())
        action = DefeatCultist(self.game, self.player)
        action.run()
        action = Walk(self.game, self.player)
        self.assertTrue(action.available())

    def test_azathoth(self):
        self.assertEqual(self.game.cultist_reserve, 8)
        Azathoth(self.game).activate()
        self.assertEqual(self.game.cultist_reserve, 5)
        self.assertIn(REDUCED_CULTIST_RESERVE, self.game.effects)

    def test_atlatchnacha(self):
        self.dummy_gods()
        for player in self.game.players:
            self.assertEqual(player.sanity, 4)
        AtlatchNacha(self.game).activate()
        for player in self.game.players:
            self.assertEqual(player.sanity, 3)

    def test_shudmell(self):
        self.assertEqual(self.player.sanity, 4)
        ShudMell(self.game).activate()
        self.assertEqual(self.player.sanity, 1)

    def test_yogsothoth(self):
        self.game.towns[0].sealed = True
        for player in self.game.players:  # clear their hands
            player.hand = []
        self.game.players[1].hand.append(ElderSign(self.game))
        action = PlayRelic(self.game, self.player)
        self.assertEqual(action.available(4), True)
        YogSothoth(self.game).activate()
        self.assertIn(ACTIVE_PLAYER_ONLY, self.game.effects)
        self.assertEqual(action.available(4), False)

    def test_hastor(self):
        # clear the board except for Wharf, Hastor can start a chain reaction
        self.clear_board()
        self.game.locations['Wharf'].shoggoth = 1
        # load the summon deck
        self.game.summon_deck[0].name = 'Train Station'
        self.game.summon_deck[0].shoggoths = False
        self.assertEqual(self.game.locations['Train Station'].shoggoth, 0)
        Hastor(self.game).activate()

        # pre-move
        self.assertEqual(self.game.locations['Train Station'].shoggoth, 0)
        self.assertEqual(self.game.locations['Wharf'].shoggoth, 0)
        # post-move
        self.assertEqual(self.game.locations['University'].shoggoth, 1)
        self.assertEqual(self.game.locations['Graveyard'].shoggoth, 1)

    def test_yigg(self):
        self.clear_board()
        self.player.hand = ['Arkham'] * 5
        self.player.location = 'Park'
        action = SealGate(self.game, self.player)
        self.assertTrue(action.available())
        Yigg(self.game).activate()
        self.assertFalse(action.available())
        self.player.hand.append('Kingsmouth')
        self.assertFalse(action.available())
        self.player.hand.append('Dunwich')
        self.assertTrue(action.available())
        action.run()
        self.assertEqual(len(self.player.hand), 1)

    def test_dagon(self):
        self.clear_board()
        Dagon(self.game).activate()
        self.assertEqual(sum([location.cultists for location in self.game.locations.values()]), 4)
        self.assertEqual(self.game.locations['Hospital'].cultists, 1)
        self.assertEqual(self.game.locations['Park'].cultists, 1)
        self.assertEqual(self.game.locations['Old Mill'].cultists, 1)
        self.assertEqual(self.game.locations['Graveyard'].cultists, 1)

    def test_tsathaggua(self):
        self.player.hand = ['Arkham'] * 4
        Tsathaggua(self.game).activate()
        self.assertEqual(len(self.player.hand), 2)

    def test_nyarlothep(self):
        self.player.location = 'Park'
        action = UseGate(self.game, self.player)
        self.assertTrue(action.available())
        Nyarlothep(self.game).activate()
        self.assertIn(DISALLOW_GATE, self.game.effects)
        self.assertFalse(action.available())

    def test_shubniggurath(self):
        summons = len(self.game.summon_discards)
        num_cultists = sum([loc.cultists for loc in self.game.locations.values()])
        # load the deck summons can't happen and trigger awakening rituals
        for card in self.game.summon_deck:
            card.shoggoths = False
        ShubNiggurath(self.game).activate()
        self.assertEqual(len(self.game.summon_discards) - summons, 4)
        self.assertEqual(sum([loc.cultists for loc in self.game.locations.values()]) - num_cultists, 4)
