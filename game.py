from decks import get_old_gods, get_player_relic_decks, get_summon_deck, EvilStirs
from utils import PandemicObject
from collections import deque
from random import shuffle


class GameBoard(object):
    id = 0
    cultist_reserve = 0
    shoggoth_reserve = 0
    player_deck = []
    player_discards = []
    summon_deck = deque([])
    summon_discards = []
    relic_deck = []
    old_gods = []
    effects = []
    players = []
    locations = {}

    def turn(self):
        pass
        # 4 actions
        # clear active relics on players

    def initialize(self):
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
        # use names in summon deck
        for location in self.summon_deck:
            self.locations[location.name] = Location(name=location.name)

    def setup_cultists(self):
        cultize = [3, 3, 2, 2, 1, 1]
        for count in cultize:
            draw = self.summon_deck.pop()
            self.summon_discards.append(draw)
            self.locations[draw.name].cultists += count
        shog = self.summon_deck.pop()
        self.summon_discards.append(shog)
        self.locations[shog.name].shoggoth = True

    def deal_players(self):
        for player in self.players:
            start = 4
            while start:
                draw = self.player_deck.pop()
                player.hand.append(draw)
                start -= 1

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

    def check_end(self):
        if self.cultist_reserve <= 0:
            return True
        if self.shoggoth_reserve <= 0:
            return True
        if 'Cthulhu' in self.effects:
            return True


class Player(PandemicObject):
    hand = None
    effects = None
    sanity = 4
    role = None

    def __init__(self, name=''):
        super(Player, self).__init__(name=name)
        self.hand = []
        self.effects = []


# Town
# connections
# elder_sign
# locations

class Location(PandemicObject):
    bus_stop = False
    cultists = 0
    connections = []
    gate = False
    shoggoth = False
# Location
# bus_stop
# connections
# cultists
# gate
# shoggoth

# Player
# deck
# location
# sanity
