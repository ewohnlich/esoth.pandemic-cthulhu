from collections import deque
from random import shuffle, choice

from utils import PandemicObject, get_input
from decks import get_old_gods, get_player_relic_decks, get_summon_deck, EvilStirs, PandemicCard, RoleManager
from printer import print_player_hands, print_elder_map

PLAYERS = 1
AUTO_ASSIGNMENT = True  # automatically set roles if true, easier for testing


class GameBoard(object):
    id = 0
    cultist_reserve = 20
    shoggoth_reserve = 3
    player_deck = None
    player_discards = None
    summon_deck = None
    summon_discards = None
    relic_deck = None
    old_gods = None
    effects = None
    players = None
    locations = None
    towns = None
    current_player = None

    def __init__(self):
        self.player_deck = []
        self.player_discards = []
        self.summon_deck = deque([])
        self.summon_discards = []
        self.relic_deck = []
        self.old_gods = []
        self.effects = []
        self.players = []
        self.locations = {}
        self.towns = []
        self.old_gods = get_old_gods()

        players = input('Number of players [2/3/4]: ')
        while players not in ['2', '3', '4']:
            players = input('Invalid number. Number of players [2/3/4]:')
        players = int(players)

        rm = RoleManager()
        while players:
            player = Player()
            rm.assign_role(player, AUTO_ASSIGNMENT)
            self.players.append(player)
            players -= 1
        self.current_player = self.players[0]
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
        self.towns = [arkham, innsmouth, dunwich, kingsport]

        locations = [
            Location('Train Station', town=arkham, bus_stop=True, gate=False),
            Location('University', town=arkham, bus_stop=False, gate=False),
            Location('Park', town=arkham, bus_stop=False, gate=True),
            Location('Secret Lodge', town=arkham, bus_stop=False, gate=False),
            Location('Police Station', town=arkham, bus_stop=False, gate=False),
            Location('Diner', town=arkham, bus_stop=True, gate=False),
            Location('Cafe', town=dunwich, bus_stop=False, gate=False),
            Location('Old Mill', town=dunwich, bus_stop=False, gate=True),
            Location('Church', town=dunwich, bus_stop=False, gate=False),
            Location('Farmstead', town=dunwich, bus_stop=False, gate=False),
            Location('Swamp', town=dunwich, bus_stop=False, gate=False),
            Location('Historic Inn', town=dunwich, bus_stop=True, gate=False),
            Location('Great Hall', town=kingsport, bus_stop=False, gate=False),
            Location('Woods', town=kingsport, bus_stop=False, gate=False),
            Location('Market', town=kingsport, bus_stop=True, gate=False),
            Location('Theater', town=kingsport, bus_stop=False, gate=False),
            Location('Wharf', town=kingsport, bus_stop=False, gate=False),
            Location('Graveyard', town=kingsport, bus_stop=False, gate=True),
            Location('Junkyard', town=innsmouth, bus_stop=False, gate=False),
            Location('Pawn Shop', town=innsmouth, bus_stop=False, gate=True),
            Location('Hospital', town=innsmouth, bus_stop=False, gate=True),
            Location('Factory', town=innsmouth, bus_stop=True, gate=False),
            Location('Docks', town=innsmouth, bus_stop=False, gate=False),
            Location('Boardwalk', town=innsmouth, bus_stop=False, gate=False),
        ]
        self.locations = {location.name: location for location in locations}

        def add_conn(*args):
            start = args[0]
            conns = args[1:]
            if isinstance(conns, str):
                conns = [conns]
            self.locations[start].connections = [self.locations[conn] for conn in conns]

        add_conn('Train Station', 'Cafe', 'University')
        add_conn('University', 'Train Station', 'Park', 'Police Station')
        add_conn('Park', 'University', 'Police Station', 'Secret Lodge')
        add_conn('Police Station', 'University', 'Park', 'Secret Lodge')
        add_conn('Secret Lodge', 'Park', 'Police Station', 'Diner')
        add_conn('Diner', 'Secret Lodge', 'Junkyard')
        add_conn('Cafe', 'Train Station', 'Church')
        add_conn('Old Mill', 'Church')
        add_conn('Church', 'Old Mill', 'Farmstead', 'Cafe', 'Historic Inn')
        add_conn('Farmstead', 'Swamp', 'Church')
        add_conn('Swamp', 'Farmstead', 'Great Hall')
        add_conn('Historic Inn', 'Church', 'Farmstead')
        add_conn('Great Hall', 'Swamp', 'Woods', 'Market')
        add_conn('Woods', 'Great Hall', 'Market', 'Docks')
        add_conn('Market', 'Woods', 'Great Hall', 'Theater', 'Wharf')
        add_conn('Theater', 'Market')
        add_conn('Wharf', 'Market', 'Graveyard')
        add_conn('Graveyard', 'Wharf')
        add_conn('Docks', 'Woods', 'Boardwalk')
        add_conn('Boardwalk', 'Docks', 'Factory')
        add_conn('Factory', 'Hospital', 'Pawn Shop', 'Boardwalk')
        add_conn('Hospital', 'Factory', 'Pawn Shop')
        add_conn('Pawn Shop', 'Junkyard')
        add_conn('Junkyard', 'Diner', 'Pawn Shop')

    def setup_cultists(self):
        cultize = [3, 3, 2, 2, 1, 1]
        for count in cultize:
            draw = self.summon_deck.pop()
            self.summon_discards.append(draw)
            self.locations[draw.name].cultists += count
            print('Placed {} cultist(s) at {}'.format(count, draw.name))
            self.cultist_reserve -= count
        shog = self.summon_deck.pop()
        self.summon_discards.append(shog)
        self.locations[shog.name].shoggoth = True
        print('Placed a shoggoth at {}'.format(shog.name))
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
            self.awakening_ritual()
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
            print('** {} loses {} sanity **'.format(player.role.name, sanity))
            player.sanity = max(0, player.sanity - sanity)
        elif cultists:
            print('** {} summons 2 cultists to {} **'.format(player.role.name, player.location))
            self.add_cultist(player.location)
            self.add_cultist(player.location)
        else:
            print('** {} maintains a grip on reality. No effect. **'.format(player.role.name))

    def awakening_ritual(self):
        for god in self.old_gods:
            if not god.revealed:
                god.revealed = True
                god.activate(self)
                break

    def play(self):
        print_elder_map(self)
        turn = 0
        while not self.have_lost() and not self.have_won():
            self.current_player = self.players[turn % len(self.players)]
            print_player_hands(self)
            print('It is now {}\'s turn (turn {})'.format(self.current_player.role.name, turn+1))
            self.current_player.do_turn(self)
            print_elder_map(self)
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
        print('Summon deck draw: {}'.format(summon.name))
        self.add_cultist(summon.name)
        if summon.shoggoths:
            self.move_shoggoths()

    def move_shoggoths(self):
        """ Shoggoths move to the closest gate

            Special casees: 1. If two or more options are equidistant from a gate, player chooses
                            2. If shoggoth is on a gate, trigger an awakening ritual
        """

        def gate_distance(loc, visited=None):
            if not visited:
                visited = []
            if [conn for conn in loc.connections if conn.gate]:
                return 1
            visited.append(loc)
            paths = [gate_distance(conn, visited) for conn in loc.connections if conn not in visited]
            paths = [path for path in paths if path]  # dead end path is 0
            if paths:
                distance = 1 + min(paths)
                return distance
            return 0  # deadend

        awaken = 0  # delay until current shoggoths move, in case one activates Hastor
        for location in self.get_shoggoth_sites():
            if location.shoggoth:
                location.shoggoth -= 1
                if location.gate:
                    print('The Shoggoth at {} enters the gate, triggering an awakening ritual'.format(location.name))
                    awaken += 1
                else:
                    opts = {}
                    for conn in location.connections:
                        if conn.gate:
                            opts[1] = [conn]
                        else:
                            dist = gate_distance(conn)
                            opts.setdefault(dist, [])
                            opts[dist].append(conn)

                    opts = opts[min(opts.keys())]
                    if len(opts) == 1:
                        opts[0].shoggoth += 1
                        print('Shoggoth moves from {} to {}'.format(location.name, opts[0].name))
                    else:
                        choice = get_input(opts, 'name', 'Shoggoth move options at {} are equidistant. '
                                                         'Current player chooses'.format(location.name))
                        choice.shoggoth += 1
                        print('Shoggoth moves from {} to {}'.format(location.name, choice.name))
        for i in range(awaken):
            self.awakening_ritual()

    def get_shoggoth_sites(self):
        locs = []
        for location in self.locations.values():
            if location.shoggoth:
                locs.append(location)
        return locs

    def summon_shoggoth(self):
        summon = self.summon_deck.popleft()
        print('A Shoggoth has been summoned at {}'.format(summon.name))
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
        sealed = [loc for loc in self.locations.values() if loc.sealed]
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
        print('{} drew a card: {}'.format(self.role.name, hasattr(card, 'name') and card.name or card))
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
        actions = 4 + self.role.action_modifier
        if not self.sanity:
            actions -= 1
        while actions:
            cost = self.do_action(board, actions)
            actions -= cost
        print('{} actions over, now drawing cards...\n'.format(self.role.name))
        self.deal(board)
        self.deal(board)
        board.draw_summon()
        board.draw_summon()

    def clear_cultist(self, board, location):
        if self.role.clear_all_cultists:
            board.locations[location].cultists = 0
        else:
            board.locations[location].cultists -= 1

    def action_move(self, board):
        # get a location and move there. Sanity if shoggo
        conns = board.locations[self.location].connections
        new_loc = None
        if len(conns) == 1:
            new_loc = conns[0].name
        if not new_loc:
            new_loc = get_input(conns, 'name', 'Where would you like to move?')
        self.location = new_loc.name
        if board.locations[self.location].shoggoth:
            print('You\'ve entered a location with a shoggoth. Performing a sanity roll...')
            board.sanity_roll()
        return 1

    def action_bus(self, board):
        raise NotImplementedError

    def do_action(self, board, remaining_actions):
        available = [
            {'title': 'Move one location', 'action': self.action_move, }
        ]
        if board.locations[self.location].bus_stop:
            available.append({'title': 'Take the bus', 'action': self.action_bus})

        opt = get_input(available, 'title', 'You have {} action(s) remaining.'.format(remaining_actions))

        return opt['action'](board)
        # move
        # bus
        # trade
        # clear cultist
        # clear shoggoth
        # seal gate
        # play relic
        # alien carving should return -3


class Town(PandemicObject):
    connections = None
    sealed = False
    elder_sign = False
    locations = None

    def __init__(self, name):
        super(Town, self).__init__(name)
        self.connections = []
        self.locations = []


class Location(PandemicObject):
    bus_stop = False
    cultists = 0
    connections = None
    gate = False
    sealed = False
    town = None
    shoggoth = 0  # could technically have multiple

    def __init__(self, name, town, bus_stop=False, gate=False):
        super(Location, self).__init__(name)
        self.town = town
        self.connections = []
        if self not in town.locations:
            town.locations.append(self)
        self.bus_stop = bus_stop
        self.gate = gate

# Player
# deck
# location
# sanity
