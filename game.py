from cthulhu.decks import get_old_gods

class GameBoard(object):
    id = 0
    cultist_reserve = 0
    shoggoth_reserve = 0
    player_cards = []
    player_discards = []
    summon_cards = []
    summon_discards = []
    old_gods = []
    effects = []

    def initialize(self):
        self.old_gods = get_old_gods()

    def check_end(self):
        if self.cultist_reserve <= 0:
            return True
        if self.shoggoth_reserve <= 0:
            return True
        if 'Cthulhu' in self.effects:
            return True

