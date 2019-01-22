from cthulhu.decks import get_old_gods, get_relics, get_town_deck


class GameBoard(object):
    id = 0
    cultist_reserve = 0
    shoggoth_reserve = 0
    player_deck = []
    player_discards = []
    summon_deck = []
    summon_discards = []
    relic_deck = []
    old_gods = []
    effects = []
    players = []

    def turn(self):
        pass
        # 4 actions
        # clear active relics on players

    def initialize(self):
        self.old_gods = get_old_gods()
        self.relic_deck = get_relics()
        town_deck = get_town_deck()
        print(town_deck)
        players = input('Number of players: ')
        print(players)

    def check_end(self):
        if self.cultist_reserve <= 0:
            return True
        if self.shoggoth_reserve <= 0:
            return True
        if 'Cthulhu' in self.effects:
            return True

# Town
# connections
# elder_sign
# locations

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
