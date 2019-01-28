from decks import PandemicCard
from utils import PandemicObject, get_input

PLAYERS = 1


class Player(PandemicObject):
    hand = None
    effects = None
    sanity = 4
    role = None
    number = 0
    location = 'Train Station'

    def __init__(self):
        global PLAYERS
        self.number = PLAYERS
        PLAYERS += 1
        self.hand = []
        self.effects = []

    def name(self):
        return '{}({})'.format(self.role.name, self.number)

    def deal(self, game):
        card = game.draw_player_card()
        game.announce('{} drew a card: {}'.format(self.role.name, hasattr(card, 'name') and card.name or card))
        if isinstance(card, PandemicCard) and card.name == 'Evil Stirs':
            card.activate(game, self)
        else:
            self.hand.append(card)
            while len(self.hand) > 7:
                discard = get_input(self.hand, None, 'You are over th e hand limit. Enter a number to discard')
                self.hand.remove(discard)
                game.discard(discard)
            self.hand = sorted(self.hand)

    def do_turn(self, game):
        actions = 4 + self.role.action_modifier
        if not self.sanity:
            actions -= 1
        while actions:
            cost = self.do_action(game, actions)
            actions -= cost
        game.announce('{} actions over, now drawing cards...\n'.format(self.role.name))
        self.deal(game)
        self.deal(game)
        game.draw_summon()
        game.draw_summon()

    def action_defeat_cultist(self, game):
        location = self.location
        if self.role.clear_all_cultists:
            game.cultist_reserve += game.locations[location].cultists
            game.locations[location].cultists = 0
            game.announce('{} removes all cultists'.format(self.name()))
        else:
            game.locations[location].cultists -= 1
            game.announce('{} removes 1 cultist'.format(self.name()))
        game.show_board()
        return 1

    def action_defeat_shoggoth(self, game):
        game.locations[self.location].shoggoth -= 1
        game.shoggoth_reserve += 1
        return 3

    def action_move(self, game):
        # get a location and move there. Sanity if shoggo
        conns = game.locations[self.location].connections
        new_loc = None
        if len(conns) == 1:
            new_loc = conns[0].name
        if not new_loc:
            new_loc = get_input(conns, 'name', 'Where would you like to move?')
        self.location = new_loc.name
        if game.locations[self.location].shoggoth:
            game.announce('You\'ve entered a location with a shoggoth. Performing a sanity roll...')
            game.sanity_roll()
        return 1

    def action_bus(self, game):
        discard = get_input([i for i in self.hand if isinstance(i, str)], None, 'Select a card to discard')
        self.hand.remove(discard)
        game.discard(discard)
        if discard == game.locations[self.location].town.name:
            destination = get_input([l for l in game.locations], None, 'Where to?')
        else:
            town = [t for t in game.towns if t.name == discard][0]
            destination = get_input(town.locations, 'name', 'Travel to a town in {}'.format(discard))
        self.location = destination.name
        game.announce('{} charters a bus to {}'.format(self.name(), destination.name))
        return 1

    def do_action(self, game, remaining_actions):
        available = [
            {'title': 'Move one location', 'action': self.action_move, }
        ]
        curr_loc = game.locations[self.location]
        if curr_loc.bus_stop and self.hand:
            available.append({'title': 'Take the bus', 'action': self.action_bus})
        if curr_loc.cultists:
            available.append({'title': 'Defeat cultist', 'action': self.action_defeat_cultist})
        if curr_loc.shoggoth and remaining_actions >= 3:
            available.append({'title': 'Defeat shoggoth', 'action':self.action_defeat_shoggoth})

        opt = get_input(available, 'title', 'You have {} action(s) remaining.'.format(remaining_actions))

        return opt['action'](game)
        # move
        # bus
        # trade
        # clear cultist
        # clear shoggoth
        # seal gate
        # play relic
        # alien carving should return -3
