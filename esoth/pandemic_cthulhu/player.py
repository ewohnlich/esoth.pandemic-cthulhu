from .actions import build_actions
from .decks import Relic, EvilStirs
from .utils import PandemicObject, get_input, SANITY_BASE, ACTIONS_BASE, SKIP_SUMMON


class Player(PandemicObject):
    hand = None
    effects = None
    sanity = SANITY_BASE
    role = None
    number = 0
    location = 'Train Station'
    seal_modifier = 0
    defeated_cultist_this_turn = False
    game = None

    def __init__(self, game):
        super(Player, self).__init__()
        self.game = game
        self.number = len(game.players) + 1
        self.hand = []
        self.effects = []

    def name(self):
        return '{}({})'.format(self.role.name, self.number)

    def sanity_name(self):
        return '{} [{}]'.format(self.role.name, self.sanity)

    def deal(self, count=1):
        """ Don't check hand limit until all cards have been dealt """
        for i in range(count):
            card = self.game.draw_player_card()
            self.game.announce('{} drew a card: {}'.format(self.role.name, hasattr(card, 'name') and card.name or card))
            if isinstance(card, EvilStirs):
                card.activate(self)
            else:
                self.hand.append(card)
                self.hand = sorted(self.hand)

        self.limit_hand()

    def limit_hand(self):
        while len(self.hand) > 7:
            discard = get_input(self.hand, None,
                                '{} is over the hand limit. Enter a number to discard'.format(self.name()))
            self.hand.remove(discard)
            self.game.discard(discard)

    def do_turn(self):
        self.defeated_cultist_this_turn = False  # reset
        num_actions = ACTIONS_BASE + self.role.action_modifier
        if not self.sanity:
            num_actions -= 1
        while num_actions > 0:
            available = [action for action in build_actions(self.game, self) if action.available(num_actions)]
            action = get_input(available, 'name', 'You have {} action(s) remaining.'.format(num_actions),
                               force=True)
            cost = action.run()
            num_actions -= cost or 0
        self.game.announce('{} actions over, now drawing cards...\n'.format(self.role.name))
        self.deal(count=2)
        if SKIP_SUMMON not in self.game.effects:
            self.game.draw_summon()
            self.game.draw_summon()

    @property
    def relics(self):
        return [card for card in self.hand if isinstance(card, Relic)]
