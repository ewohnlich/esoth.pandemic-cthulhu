from .decks import PandemicCard, Relic
from .utils import PandemicObject, get_input, SANITY_BASE, ACTIONS_BASE, SKIP_SUMMON
from .actions import build_actions

PLAYERS = 1


class Player(PandemicObject):
    hand = None
    effects = None
    sanity = SANITY_BASE
    role = None
    number = 0
    location = 'Train Station'
    seal_modifier = 0
    defeated_cultist_this_turn = False

    def __init__(self):
        super(Player, self).__init__()
        global PLAYERS
        self.number = PLAYERS
        PLAYERS += 1
        self.hand = []
        self.effects = []

    def name(self):
        return '{}({})'.format(self.role.name, self.number)

    def deal(self, game, count=1):
        """ Don't check hand limit until all cards have been dealt """
        for i in range(count):
            card = game.draw_player_card()
            game.announce('{} drew a card: {}'.format(self.role.name, hasattr(card, 'name') and card.name or card))
            if isinstance(card, PandemicCard) and card.name == 'Evil Stirs':
                card.activate(game, self)
            else:
                self.hand.append(card)
                self.hand = sorted(self.hand)

        self.limit_hand(game)

    def limit_hand(self, game):
        while len(self.hand) > 7:
            discard = get_input(self.hand, None,
                                '{} is over the hand limit. Enter a number to discard'.format(self.name()))
            self.hand.remove(discard)
            game.discard(discard)

    def do_turn(self, game):
        self.defeated_cultist_this_turn = False  # reset
        num_actions = ACTIONS_BASE + self.role.action_modifier
        if not self.sanity:
            num_actions -= 1
        while num_actions > 0:
            available = [action for action in build_actions(game, self) if action.available(num_actions)]
            action = get_input(available, 'name', 'You have {} action(s) remaining.'.format(num_actions),
                               force=True)
            cost = action.run()
            num_actions -= cost or 0
        game.announce('{} actions over, now drawing cards...\n'.format(self.role.name))
        self.deal(game, count=2)
        if SKIP_SUMMON not in game.effects:
            game.draw_summon()
            game.draw_summon()

    @property
    def relics(self):
        return [card for card in self.hand if isinstance(card, Relic)]
