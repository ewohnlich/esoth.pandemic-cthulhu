from decks import get_old_gods, get_player_relic_decks, get_summon_deck, EvilStirs, PandemicCard
from utils import PandemicObject
from collections import deque
from random import shuffle, choice

PLAYERS = 1


class GameBoard(object):
    id = 0
    cultist_reserve = 20
    shoggoth_reserve = 3
    player_deck = []
    player_discards = []
    summon_deck = deque([])
    summon_discards = []
    relic_deck = []
    old_gods = []
    effects = []
    players = []
    locations = {}
    towns = []
    current_player = None

    def __init__(self):
        self.old_gods = get_old_gods()
        players = input('Number of players [2/3/4]: ')
        while players not in ['2', '3', '4']:
            players = input('Invalid number. Number of players [2/3/4]:')
        players = int(players)

        while players:
            self.players.append(Player())
            players -= 1
        self.player_deck, self.relic_deck = get_player_relic_decks(players)
        self.summon_deck = get_summon_deck()
        self.setup_locations()
        self.setup_cultists()
        self.deal_players()
        self.initialize_evil()

    def setup_locations(self):
        kingsport = Town('Kingsport')
        innsmouth = Town('Innsmouth')
        dunwich = Town('Dunwich')
        arkham = Town('Arkham')
        kingsport.connections = [innsmouth, dunwich]
        innsmouth.connections = [arkham, kingsport]
        dunwich.connections = [arkham, kingsport]
        arkham.connections = [innsmouth, dunwich]
        self.towns = [kingsport, innsmouth, dunwich, arkham]

        locations = [
            Location('Train Station', town=arkham, bus_stop=True, gate=False)
        ]

        for location in locations:
            self.locations[location.name] = location

    def setup_cultists(self):
        cultize = [3, 3, 2, 2, 1, 1]
        for count in cultize:
            draw = self.summon_deck.pop()
            self.summon_discards.append(draw)
            self.locations[draw.name].cultists += count
            self.cultist_reserve -= count
        shog = self.summon_deck.pop()
        self.summon_discards.append(shog)
        self.locations[shog.name].shoggoth = True
        self.shoggoth_reserve -= 1

    def deal_players(self):
        for player in self.players:
            start = 4
            while start:
                player.deal(self)
                start -= 1

    def draw_player_card(self):
        if self.player_deck:
            return self.player_deck.pop()

    def initialize_evil(self):
        """ Divide the decks into 4 after players have each been dealt their cards
            Add 1 EvilStirs to each subset
            Shuffle each subset
            Concatenate subsets
        """
        decks = [[] for d in range(4)]
        curr_deck = 0
        while self.player_deck:
            draw = self.player_deck.pop()
            decks[curr_deck % 4].append(draw)
            curr_deck += 1
        while decks:
            deck = decks.pop()
            deck.append(EvilStirs())
            shuffle(deck)
            self.player_deck += deck

    def add_cultist(self, location):
        if self.locations[location].cultists == 3:
            # awaken ritual
            print('{} is at cultist capacity - an awakening ritual occurs!'.format(location))
            raise NotImplementedError
        else:
            self.locations[location].cultists += 1
            print('{} now has {} cultist(s)'.format(location, self.locations[location].cultists))

    def sanity_roll(self, player=None):
        if not player:
            player = self.current_player
        choices = [(0, 0),  # sanity, cultists
                   (0, 0),
                   (1, 0),
                   (1, 0),
                   (2, 0),
                   (0, 2), ]
        sanity, cultists = choice(choices)
        if sanity:
            print('** {} loses {} sanity **'.format(player.name, sanity))
            player.sanity = max(0, player.sanity - sanity)
        elif cultists:
            self.add_cultist(player.location)
            self.add_cultist(player.location)
        else:
            print('** {} maintains a grip on reality. No effect. **'.format(player.role))

    def awakening_ritual(self):
        for god in self.old_gods:
            if not god.revealed:
                god.revealed = True
                god.activate(self)
                break

    def play(self):
        turn = 0
        while not self.have_lost() and not self.have_won():
            self.current_player = self.players[turn % len(self.players)]
            self.current_player.do_turn(self)
            turn += 1
        condition = self.have_lost()
        if condition:
            condition = 'You have lost: {}'.format(condition)
        else:
            condition = 'You have won!'
        print('The game is over. {}'.format(condition))

    def discard(self, card):
        self.player_discards.append(card)

    def draw_summon(self):
        # rebuild deck if empty. This is not a loss condition
        if not self.summon_deck:
            discards = self.summon_discards
            shuffle(discards)
            self.summon_deck = deque(discards)
            self.summon_discards = []
        summon = self.summon_deck.pop()
        if summon.shoggoths:
            self.move_shoggoths()

    def move_shoggoths(self):
        for location in self.locations:
            if location.shoggoth:
                if location.gate:
                    self.awakening_ritual()
                    location.shoggoth -= 1
                else:
                    raise NotImplementedError

    def summon_shoggoth(self):
        summon = self.summon_deck.popleft()
        self.shoggoth_reserve -= 1
        if self.shoggoth_reserve < 0:
            return  # stop here
        self.summon_discards.append(summon)
        self.locations[summon.name].shoggoth += 1
        for player in self.players:
            if player.location == summon.name:
                self.sanity_roll(player)
        return summon.name

    def regroup_cultists(self):
        discards = self.summon_discards
        shuffle(discards)
        self.summon_deck += discards
        self.summon_discards = []

    def have_won(self):
        sealed = [loc for loc in self.locations if loc.sealed]
        return len(sealed) == 4

    def have_lost(self):
        if self.cultist_reserve < 0:
            return 'Not enough cultists in reserve.'
        if self.shoggoth_reserve < 0:
            return 'Not enough shoggoths in reserve.'
        if 'Cthulhu' in self.effects:
            return self.old_gods[-1].text
        if not any([player.sanity for player in self.players]):
            return 'All players are insane.'
        if not self.player_deck:
            return 'Player deck has been depleted.'


class Player(PandemicObject):
    hand = None
    effects = None
    sanity = 4
    role = None
    location = 'Train Station'

    def __init__(self, name=''):
        super(Player, self).__init__(name=name)
        if not self.name:
            global PLAYERS
            self.name = 'player{}'.format(PLAYERS)
            PLAYERS += 1
        self.hand = []
        self.effects = []

    def deal(self, board):
        card = board.draw_player_card()
        if isinstance(card, PandemicCard) and card.name == 'Evil Stirs':
            card.activate(board, self)
        else:
            self.hand.append(card)
            while len(self.hand) > 7:
                opts = ['{}. {}'.format(idx + 1, card) for idx, card in enumerate(self.hand)]
                discard = input('You are over the hand limit. Enter a number to discard. {}'.format(', '.join(opts)))
                try:
                    discard_idx = int(discard) - 1
                    discard = self.hand[discard_idx]
                    del self.hand[discard_idx]
                    board.discard(discard)
                except ValueError:
                    print('Option must be an integer')
                except IndexError:
                    print('Not a valid option')
            self.hand = sorted(self.hand)

    def do_turn(self, board):
        actions = 4  # one role has more
        while actions:
            cost = self.do_action(board, actions)
            actions -= cost
        self.deal(board.draw_player_card())
        self.deal(board.draw_player_card())
        board.draw_summon()
        board.draw_summon()

    def do_action(self, board, remaining_actions):
        raise NotImplementedError
        # move
        # bus
        # trade
        # clear cultist
        # clear shoggoth
        # seal gate
        # play relic
        # alien carving should return -3


class Town(PandemicObject):
    connections = []
    sealed = False
    elder_sign = False
    locations = []


class Location(PandemicObject):
    bus_stop = False
    cultists = 0
    connections = []
    gate = False
    sealed = False
    town = False
    shoggoth = 0  # could technically have multiple

    def __init__(self, name, town, bus_stop=False, gate=False):
        super(Location, self).__init__(name)
        self.bus_stop = bus_stop
        self.gate = gate

# Player
# deck
# location
# sanity
