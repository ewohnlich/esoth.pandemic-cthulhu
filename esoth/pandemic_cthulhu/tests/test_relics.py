from ..decks import AlienCarving, BizarreStatue, MiGoEye, XaosMirror, SilverKey, SongOfKadath, \
    ElderSign, LastHourglass, WardedBox, get_relics, Nyarlothep, BookOfShadow, SealOfLeng, AlhazredsFlame
from ..actions import PlayRelic, SealGate
from ..utils import SKIP_SUMMON, SKIP_SANITY_CHECKS, MAGICIAN

from .base import PandemicCthulhuTestCase


class RelicCase(PandemicCthulhuTestCase):
    def test_sanityroll(self):
        self.game.towns[0].sealed = True
        self.game.old_gods[0] = Nyarlothep(self.game)
        self.game.old_gods[0].activate()

        for relic in get_relics(self.game):
            self.clear_board()
            self.game.player_discards = ['Arkham', 'Innsmouth'] * 6
            self.game.players[0].hand = ['Arkham', 'Dunwich']
            self.game.players[1].hand = ['Innsmouth', 'Kingsport']
            if 'No sanity roll required' not in relic.text:
                relic.play(self.player)
                self.assertIn('**', self.game.stream.getvalue())
                self.game.stream.truncate(0)
                self.game.stream.seek(0)

    def test_aliencarving(self):
        self.clear_board(True)
        relic = AlienCarving(self.game)
        self.player.hand = [relic]
        self.clear_board()
        action = PlayRelic(self.game, self.player)
        self.assertEqual(action.run(), -3)

    def test_bizarrestatue(self):
        self.clear_board(True)
        relic = BizarreStatue(self.game)
        relic.play(self.player)
        discards = len(self.game.summon_discards)
        self.game.player_deck = ['Arkham'] * 4  # no evil stirs please!
        self.player.do_turn()
        self.assertEqual(len(self.game.summon_discards) - discards, 0)
        self.game.reset_states()  # this action is handled by the game, not the player
        self.assertNotIn(SKIP_SUMMON, self.game.effects)
        self.clear_board(hands=True)
        self.player.do_turn()
        self.assertEqual(len(self.game.summon_discards) - discards, 2)

    def test_migoeye(self):
        self.clear_board(True)
        self.player.hand = ['Arkham'] * 4
        self.player.location = 'Park'
        action = SealGate(self.game, self.player)
        self.assertFalse(action.available())
        relic = MiGoEye(self.game)
        relic.play(self.player)
        self.assertTrue(action.available())

    def test_wardedbox(self):
        self.game.shoggoth_reserve = 999

        def next_turn():
            self.game.stream.truncate(0)
            self.game.stream.seek(0)
            self.game.reset_states()
            self.clear_board()
            for player in self.game.players:
                player.sanity = 4

        self.dummy_gods()

        # pre-relic
        next_turn()
        self.game.summon_deck[0].name = self.player.location
        self.game.summon_shoggoth()
        self.assertNotIn('Active effect precludes the need for a sanity check', self.game.stream.getvalue())
        next_turn()

        # player1, play relic and summon
        relic = WardedBox(self.game)
        relic.play(self.player)
        self.game.summon_deck[0].name = self.player.location
        self.game.summon_shoggoth()
        self.assertIn('Active effect precludes the need for a sanity check', self.game.stream.getvalue())
        next_turn()

        # player 2, still active
        self.game.summon_deck[0].name = self.player.location
        self.game.summon_shoggoth()
        self.assertIn('Active effect precludes the need for a sanity check', self.game.stream.getvalue())
        next_turn()

        # player 1, still active but ends here
        self.game.summon_deck[0].name = self.player.location
        self.game.summon_shoggoth()
        self.assertIn('Active effect precludes the need for a sanity check', self.game.stream.getvalue())
        next_turn()

        # player 2, effect has now ended
        self.game.summon_deck[0].name = self.player.location
        self.game.summon_shoggoth()
        self.assertNotIn('Active effect precludes the need for a sanity check', self.game.stream.getvalue())
        next_turn()

    def test_xaosmirror(self):
        relic = XaosMirror(self.game)
        trade_card_p1 = self.player1.hand[0]
        trade_card_p2 = self.player2.hand[0]
        relic.play(self.player1)
        # players swap their first cards, which goes to the end of their hand
        self.assertEqual(self.player1.hand[-1], trade_card_p2)
        self.assertEqual(self.player2.hand[-1], trade_card_p1)

    def test_silverkey(self):
        self.clear_board()
        relic = SilverKey(self.game)
        # train station will be first choice, so move them off first
        self.player.location = 'Boardwalk'
        relic.play(self.player)
        self.assertEqual(self.player.location, 'Train Station')

    def test_songofkadath(self):
        for player in self.game.players:
            player.sanity -= 1
            self.assertEqual(player.sanity, 3)
        relic = SongOfKadath(self.game)
        relic.play(self.player)
        for player in self.game.players:
            self.assertEqual(player.sanity, 4)

    def test_eldersign(self):
        self.clear_board(True)
        relic = ElderSign(self.game)
        town = [town for town in self.game.towns if town.name == 'Arkham'][0]
        town.sealed = True
        loc = self.game.locations['University']
        self.game.add_cultist(loc.name)
        self.assertEqual(loc.cultists, 1)  # pre-seal this should add a cultist
        self.assertEqual(town.elder_sign, False)

        relic.play(self.player)
        self.assertEqual(town.elder_sign, True)
        self.game.add_cultist(loc.name)
        self.assertEqual(loc.cultists, 1)  # pre-seal no new cultist

    def test_bookofshadow(self):
        self.clear_board(True)
        new_towns = ['Arkham', 'Innsmouth', 'Kingsport', 'Dunwich']
        self.game.player_deck.extend(new_towns)
        relic = BookOfShadow(self.game)
        relic.play(self.player)  # with no input it just reverses
        new_towns.reverse()
        self.assertEqual(self.game.player_deck[-4:], new_towns)

    def test_last_hourglass(self):
        self.clear_board(True)
        relic = LastHourglass(self.game)
        self.game.player_discards.append('Arkham')
        self.assertEqual(len(self.player.hand), 0)
        relic.play(self.player)
        self.assertEqual(self.player.hand[-1], 'Arkham')
        self.assertEqual(len(self.player.hand), 1)
        self.assertRaises(IndexError, relic.play, self.player)

    def test_sealofleng(self):
        nyarlothep = Nyarlothep(self.game)
        self.game.old_gods[0] = nyarlothep
        self.game.old_gods[0].activate()
        relic = SealOfLeng(self.game)
        relic.play(self.player)
        self.assertNotIn(nyarlothep.effect, self.game.effects)
        self.assertEqual(self.game.old_gods[0].name, 'SEAL OF LENG')

    def test_alhazredsflame(self):
        self.clear_board(True)
        relic = AlhazredsFlame(self.game)

        # clear shoggoth
        self.game.locations['Wharf'].shoggoth = 1
        # otherwise using a relic could add cultists, and the relic would then remove them!
        self.game.effects.append(SKIP_SANITY_CHECKS)
        relic.play(self.player)
        self.assertEqual(self.game.locations['Wharf'].shoggoth, 0)

        # clear cultists
        self.clear_board()  # sanity roll could have added cultists
        self.game.locations['Wharf'].cultists = 3
        self.game.locations['Police Station'].cultists = 1
        self.assertEqual(sum([loc.cultists for loc in self.game.locations.values()]), 4)
        relic.play(self.player)
        self.assertEqual(self.game.locations['Wharf'].cultists, 0)
        self.assertEqual(self.game.locations['Police Station'].cultists, 0)
