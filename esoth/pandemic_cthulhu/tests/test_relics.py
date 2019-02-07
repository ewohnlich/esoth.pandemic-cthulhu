from esoth.pandemic_cthulhu.decks import XaosMirror, ElderSign, LastHourglass

from .base import PandemicCthulhuTestCase


class RelicCase(PandemicCthulhuTestCase):
    def test_xaosmirror(self):
        relic = XaosMirror(self.game)
        player1 = self.player
        player2 = self.game.players[1]
        trade_card_p1 = player1.hand[0]
        trade_card_p2 = player2.hand[1]
        relic.play(player1, trade_card_p1, trade_card_p2)
        # players swap their first cards, which goes to the end of their hand
        self.assertEqual(player1.hand[-1], trade_card_p2)
        self.assertEqual(player2.hand[-1], trade_card_p1)

    def test_eldersign(self):
        relic = ElderSign(self.game)
        town = self.game.towns[0]
        town.sealed = True
        town.locations[0].cultists = 0  # make sure we start 0
        self.game.add_cultist(town.locations[0].name)
        self.assertEqual(town.locations[0].cultists, 1)  # pre-seal this should add a cultist
        self.assertEqual(town.elder_sign, False)

        relic.play(self.player)
        self.assertEqual(town.elder_sign, True)
        self.game.add_cultist(town.locations[0].name)
        self.assertEqual(town.locations[0].cultists, 1)  # pre-seal no new cultist

    def test_last_hourglass(self):
        relic = LastHourglass(self.game)
        self.game.player_discards.append('Arkham')
        clue = self.game.player_discards[0]
        self.assertEqual(len(self.player.hand), 4)
        relic.play(self.player, automate=clue)
        self.assertEqual(self.player.hand[-1], 'Arkham')
        self.assertEqual(len(self.player.hand), 5)
        self.assertRaises(ValueError, relic.play, self.player, automate=clue)
