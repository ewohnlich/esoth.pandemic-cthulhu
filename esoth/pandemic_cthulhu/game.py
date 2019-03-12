import sys
from collections import deque
from random import shuffle, choice

from .decks import get_old_gods, get_player_relic_decks, get_summon_deck, EvilStirs, RoleManager
from .player import Player
from .printer import print_elder_map
from .utils import PandemicObject, get_input, SKIP_SUMMON, SKIP_SANITY_CHECKS, SEAL_GATE_BASE_COST, \
    REDUCE_SEAL_COST, INCREASE_SEAL_COST, DETECTIVE, MAGICIAN, confirm


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
    _effect_tracker = None  # depreciate by 1 each turn. Allows effect to persist across turns
    players = None
    locations = None
    towns = None
    current_player = None
    stream = sys.stdout

    def __init__(self, num_players=False, stream=None, auto=False):
        self.player_deck = []
        self.player_discards = []
        self.summon_deck = deque([])
        self.summon_discards = []
        self.relic_deck = []
        self.old_gods = []
        self.effects = []
        self.effect_tracker = {}
        self.players = []
        self.locations = {}
        self.towns = []
        self.old_gods = get_old_gods(self)
        self.num_players = num_players
        self.auto = auto

        if stream:
            self.stream = stream

        if not num_players:
            num_players = input('Number of players [2/3/4]: ')
            while num_players not in ['2', '3', '4']:
                num_players = input('Invalid number. Number of players [2/3/4]:')
            num_players = int(num_players)
        self.num_players = num_players

    def announce(self, msg):
        """ The game is only text based now so it just prints to stdout

        :param msg: message to print
        :return:
        """
        if self.stream:
            print(msg, file=self.stream)

    def show_board(self):
        print_elder_map(self)

    def _setup_locations(self):
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
            Location('Pawn Shop', town=innsmouth, bus_stop=False, gate=False),
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
        add_conn('Farmstead', 'Swamp', 'Church', 'Historic Inn')
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
        add_conn('Factory', 'Hospital', 'Boardwalk')
        add_conn('Hospital', 'Factory', 'Pawn Shop')
        add_conn('Pawn Shop', 'Junkyard', 'Hospital')
        add_conn('Junkyard', 'Diner', 'Pawn Shop')

    def _setup_cultists(self):
        cultize = [3, 3, 2, 2, 1, 1]
        for count in cultize:
            draw = self.summon_deck.pop()
            self.summon_discards.append(draw)
            self.locations[draw.name].cultists += count
            self.announce('Placed {} cultist(s) at {}'.format(count, draw.name))
            self.cultist_reserve -= count
        shog = self.summon_deck.pop()
        self.summon_discards.append(shog)
        self.locations[shog.name].shoggoth = 1
        self.shoggoth_reserve -= 1
        self.announce('Placed a shoggoth at {}'.format(shog.name))

    def _deal_players(self):
        for player in self.players:
            start = 4
            while start:
                player.deal()
                start -= 1
            if player.role == MAGICIAN:
                self.draw_relic_card(player)

    def _initialize_evil(self):
        """ Divide the decks into 4 after players have each been dealt their cards
            Add 1 EvilStirs to each subset
            Shuffle each subset
            Concatenate subsets
        """
        decks = [[], [], [], []]
        curr_deck = 0
        while self.player_deck:
            draw = self.player_deck.pop()
            decks[curr_deck % 4].append(draw)
            curr_deck += 1
        while decks:
            deck = decks.pop()
            deck.append(EvilStirs(self))
            shuffle(deck)
            self.player_deck += deck

    def _setup(self):
        rm = RoleManager()
        while self.num_players:
            player = Player(self)
            rm.assign_role(player, self.auto)
            self.players.append(player)
            self.num_players -= 1
        self.current_player = self.players[0]
        self.player_deck, self.relic_deck = get_player_relic_decks(self, self.num_players)
        self.summon_deck = get_summon_deck()
        self._setup_locations()
        self._setup_cultists()
        self._deal_players()
        self._initialize_evil()

    def seal_cost(self):
        cost = sum([
            SEAL_GATE_BASE_COST,
            -1 * int(REDUCE_SEAL_COST in self.effects),
        ])
        if self.current_player.role == DETECTIVE:
            cost -= 1
        return cost

    def seal_gate(self, town):
        town.sealed = True
        for loc in town.locations:
            if loc.cultists:
                loc.cultists -= 1
                self.cultist_reserve += 1
        if REDUCE_SEAL_COST in self.effects:
            self.effects.remove(REDUCE_SEAL_COST)
        self.announce(
            'The gate in {} has been sealed! Cultists in this town reduced by 1 in each location'.format(town.name))
        self.show_board()

    def draw_relic_card(self, player):
        if self.relic_deck:
            relic = self.relic_deck.pop()
            self.announce('{} draws a relic card. {}: {}'.format(player.name(), relic.name, relic.text))
            player.hand.append(relic)
            player.limit_hand()

    def draw_player_card(self):
        if self.player_deck:
            return self.player_deck.pop()

    def add_cultist(self, location, respect_elder=True):
        town = self.locations[location].town
        if town.elder_sign and respect_elder:
            self.announce('An elder sign prevents a cultist from being added to {}'.format(location))
        elif self.locations[location].cultists == 3:
            # awaken ritual
            self.announce('{} is at cultist capacity - an awakening ritual occurs!'.format(location))
            self.awakening_ritual()
        else:
            self.locations[location].cultists += 1

    def sanity_roll(self, player=None):
        if SKIP_SANITY_CHECKS in self.effects:
            self.announce('Active effect precludes the need for a sanity check')
            return
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
            self.announce('** {} loses {} sanity **'.format(player.name(), sanity))
            player.sanity = max(0, player.sanity - sanity)
        elif cultists:
            self.announce('** {} summons 2 cultists to {} **'.format(player.name(), player.location))
            self.add_cultist(player.location)
            self.add_cultist(player.location)
        else:
            self.announce('** {} maintains a grip on reality. No effect. **'.format(player.name()))

    def awakening_ritual(self):
        for god in self.old_gods:
            if not god.revealed:
                god.revealed = True
                god.activate()
                confirm()
                break

    def reset_states(self):
        if SKIP_SUMMON in self.effects:
            self.effects.remove(SKIP_SUMMON)
        if SKIP_SANITY_CHECKS in self.effects:
            self.effect_tracker[SKIP_SANITY_CHECKS] -= 1
            if self.effect_tracker[SKIP_SANITY_CHECKS] <= 0:
                self.effects.remove(SKIP_SANITY_CHECKS)

    def summoning_rate(self):
        if len([god for god in self.old_gods if god.revealed]) > 3:
            return 3
        return 2

    def play(self):
        self._setup()

        self.show_board()
        turn = 0
        while not self.game_over():
            self.current_player = self.players[turn % len(self.players)]
            self.announce('It is now {}\'s turn (turn {})'.format(self.current_player.name(), turn + 1))
            self.current_player.do_turn()
            self.reset_states()
            self.show_board()
            turn += 1

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
        self.summon_discards.append(summon)
        self.announce('Summon deck draw: {}'.format(summon.name))
        self.add_cultist(summon.name)
        self.cultist_reserve -= 1
        if summon.shoggoths:
            self.move_shoggoths()

    def gate_distance(self, loc, visited=None):
        if not visited:
            visited = []
        if [_conn for _conn in loc.connections if _conn.gate and not _conn.town.sealed]:
            return 1
        visited.append(loc)
        paths = [self.gate_distance(_conn, visited) for _conn in loc.connections if _conn not in visited]
        paths = [path for path in paths if path]  # dead end path is 0
        if paths:
            distance = 1 + min(paths)
            return distance
        return 999  # deadend

    def move_shoggoths(self, automate=False):
        """ Shoggoths move to the closest gate

            Special cases: 1. If two or more options are equidistant from a gate, player chooses
                            2. If shoggoth is on a gate, trigger an awakening ritual
        """

        awaken = 0  # delay until current shoggoths move, in case one activates Hastor
        for location in self.get_shoggoth_sites():
            if location.shoggoth:
                location.shoggoth -= 1
                if location.gate and not location.town.sealed:
                    self.announce(
                        'The Shoggoth at {} enters the gate, triggering an awakening ritual'.format(location.name))
                    awaken += 1
                    self.shoggoth_reserve += 1
                else:
                    opts = {}
                    for conn in location.connections:
                        if conn.gate and not conn.town.sealed:
                            opts[0] = [conn]
                        else:
                            dist = self.gate_distance(conn)
                            opts.setdefault(dist, [])
                            opts[dist].append(conn)

                    opts = opts[min(opts.keys())]
                    if len(opts) == 1:
                        opts[0].shoggoth += 1
                        self.announce('Shoggoth moves from {} to {}'.format(location.name, opts[0].name))
                        for player in self.players:
                            if player.location == opts[0].name:
                                self.announce('Shoggoth enters the location of {}, performing a sanity roll'.format(
                                    player.name()))
                                self.sanity_roll(player)
                    else:
                        if automate:
                            destination = opts[0]
                        else:
                            destination = get_input(opts, 'name', 'Shoggoth move options at {} are equidistant. '
                                                                  'Current player chooses'.format(location.name))
                        destination.shoggoth += 1
                        for player in self.players:
                            if player.location == destination.name:
                                self.announce('Shoggoth enters the location of {}, performing a sanity roll'.format(
                                    player.name()))
                                self.sanity_roll(player)
                        self.announce('Shoggoth moves from {} to {}'.format(location.name, destination.name))
        for i in range(awaken):
            self.awakening_ritual()

    def move_player(self, location):
        """ Moves player to a location and checks for Shoggoth

        :return: None
        """
        player = self.current_player
        player.location = location
        self.announce('{} moves to {}'.format(player.name(), location))
        if self.locations[player.location].shoggoth:
            self.announce('You\'ve entered a location with a shoggoth. Performing a sanity roll...')
            self.sanity_roll()
        self.show_board()

    def get_shoggoth_sites(self):
        locs = []
        for location in self.locations.values():
            if location.shoggoth:
                locs.append(location)
        return locs

    def summon_shoggoth(self):
        summon = self.summon_deck.popleft()
        town = self.locations[summon.name].town
        if town.elder_sign:
            self.announce('An elder sign prevents a shoggoth from being summoned to {}'.format(summon.name))
        else:
            self.announce('A Shoggoth has been summoned at {}'.format(summon.name))
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

    def game_over(self):
        sealed = [town for town in self.towns if town.sealed]
        if len(sealed) == 4:
            self.announce('The game is over. You have won!')
            return True

        loss_condition = None
        if self.cultist_reserve < 0:
            loss_condition = 'Not enough cultists in reserve.'
        if self.shoggoth_reserve < 0:
            loss_condition = 'Not enough shoggoths in reserve.'
        if self.old_gods[-1].revealed:
            loss_condition = self.old_gods[-1].text
        if not any([player.sanity for player in self.players if player.sanity > 0]):
            loss_condition = 'All players are insane.'
        if not self.player_deck:
            loss_condition = 'Player deck has been depleted.'

        if loss_condition:
            self.announce('You have lost: {}'.format(loss_condition))
            return True


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
