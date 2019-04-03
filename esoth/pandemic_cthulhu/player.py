import random

from .actions import build_actions, PlayRelic, Walk
from .decks import Relic, EvilStirs
from .utils import PandemicObject, get_input, SANITY_BASE, ACTIONS_BASE, SKIP_SUMMON, MAGICIAN, DOCTOR


class Player(PandemicObject):
    hand = None
    effects = None
    sanity = SANITY_BASE
    role = None
    number = 0
    location = 'Train Station'
    game = None

    # once per turn/event trackers
    defeated_cultist_this_space = False
    defeated_shoggoth_this_turn = False
    played_relic_this_turn = False
    insane_hunter_paranoia = False
    extra_move_available = False

    def __init__(self, game):
        super(Player, self).__init__()
        self.game = game
        self.number = len(game.players) + 1
        self.hand = []
        self.effects = []

    def name(self):
        return '{}({})'.format(self.role, self.number)

    def sanity_name(self):
        return '{} [{}]'.format(self.role, self.sanity)

    def deal(self, count=1):
        """ Don't check hand limit until all cards have been dealt """
        for i in range(count):
            card = self.game.draw_player_card()
            if hasattr(card, 'name'):
                if hasattr(card, 'text'):
                    self.game.announce('{} drew a card: {}: {}'.format(self.role, card.name, card.text))
                else:
                    self.game.announce('{} drew a card: {}'.format(self.role, card.name))
            else:
                self.game.announce('{} drew a card: {}'.format(self.role, card))
            if isinstance(card, EvilStirs):
                card.activate(self)
                if card.name == 'Cthulhu':
                    return
            else:
                self.hand.append(card)
                self.hand = sorted(self.hand)

        self.limit_hand()

    def hand_limit(self):
        """ max cards player can have """
        if self.role == MAGICIAN and self.sanity:
            return 8
        return 7

    def limit_hand(self):
        """ reduce hand size to the hand_limit """
        while len(self.hand) > self.hand_limit():
            discard = get_input(self.hand, None,
                                '{} is over the hand limit. Enter a number to discard'.format(self.name()))
            self.hand.remove(discard)
            self.game.discard(discard)
            if isinstance(discard, Relic):
                if discard.playable():
                    discard.play(self)

    def do_turn(self):
        # TODO sanity state may change mid turn, which effects turn limit
        self.defeated_shoggoth_this_turn = False
        self.played_relic_this_turn = False
        num_actions = ACTIONS_BASE
        if self.role == DOCTOR:
            num_actions += 1
        if not self.sanity:
            num_actions -= 1
        last_location = self.location
        while num_actions > 0:
            available = [action for action in build_actions(self.game, self) if action.available(num_actions)]
            action = get_input(available, 'name', 'You have {} action(s) remaining.'.format(num_actions),
                               force=True)
            cost = action.run()
            if not isinstance(action, Walk):
                self.extra_move_available = False
            num_actions -= cost or 0
            if self.location != last_location:
                self.defeated_cultist_this_space = False  # reset Ithaqua effect
            last_location = self.location
            if self.game.game_over():
                return
        if self.role == MAGICIAN and self.relics and not self.sanity and not self.played_relic_this_turn:
            self.game.announce('As the magician with a relic and no sanity, you must play a relic')
            PlayRelic(self.game, self).run()
        self.game.announce('{} actions over, now drawing cards...\n'.format(self.role))
        self.deal(count=2)
        if self.game.game_over():  # Evil Stirs could have ended the game
            return
        if SKIP_SUMMON not in self.game.effects:
            for i in range(self.game.summoning_rate()):
                self.game.draw_summon()

    @property
    def relics(self):
        return [card for card in self.hand if isinstance(card, Relic)]

    def insane_hunter_roll(self):
        """ special roll for insane hunter, the first time each turn they enter a location with no cultists """
        if random.choice((0, 1)):
            self.game.add_cultist(self.location)
