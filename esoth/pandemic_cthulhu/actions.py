from .decks import Relic
from .utils import get_input, MOVEMENT_RESTRICTION, DEFEAT_SHOGGOTH_COST, DISALLOW_GATE, ACTIVE_PLAYER_ONLY, \
    DETECTIVE, MAGICIAN, DRIVER, OCCULTIST, HUNTER, REPORTER, INCREASE_SEAL_COST
from .printer import print_rules


class Action(object):
    """ An action defines its availability and its execution, for a given game state and player """
    name = 'Action'
    game = None
    player = None

    def __init__(self, game, player):
        """ Create an action with bound game state and player

        :param game: Game state
        :param player: Player
        """
        self.game = game
        self.player = player

    def available(self, remaining_actions):
        return False

    def run(self):
        """ execute the action

        :return: action cost. For example move is 1, defeat shoggo is 3. We have to do this on run because some
        actions (relics) might increase/decrease cost. A relic that adds moves is expressed here as a negative cost
        """
        return 0

    def curr_loc(self):
        """ :returns game.Location object, not location name """
        return self.game.locations[self.player.location]

    def give_take_relic_cost(self, giver, taker):
        if giver.sanity and giver.role == MAGICIAN:
            return 0
        elif taker.sanity and taker.role == MAGICIAN:
            return 0
        return 1

    def give_take_clue_cost(self, giver, taker):
        if not giver.sanity and giver.role == DETECTIVE:
            return 2
        return 1

    def defeat_shoggoth_cost(self):
        if self.player.role == HUNTER and not self.player.defeated_shoggoth_this_turn:
            return 1
        return DEFEAT_SHOGGOTH_COST


class Walk(Action):
    name = 'Walk to a location'

    def available(self, remaining_actions=None):
        if self.player.role == DRIVER:
            return True
        elif self.game.locations[self.player.location].cultists >= 2 and MOVEMENT_RESTRICTION in self.game.effects:
            return self.player.defeated_cultist_this_space
        return True

    def run(self, double=False):
        """ Walk to a location

        :param double: the driver can move twice, and MUST if insane
        :return: action cost
        """
        # get a location and move there. Sanity if shoggo
        conns = self.game.locations[self.player.location].connections
        new_loc = None
        if len(conns) == 1:
            new_loc = conns[0]
        if not new_loc:
            new_loc = get_input(conns, 'name', 'Where would you like to move?')
        self.game.move_player(new_loc.name)

        if self.player.role == HUNTER and not self.player.sanity and not self.player.insane_hunter_paranoia and new_loc.cultists:
            self.player.insane_hunter_roll()
            self.player.insane_hunter_paranoia = True

        if not double:
            if self.player.role == DRIVER:
                second_move = True
                if self.player.sanity:
                    second_move = get_input(['Yes', 'No'], None, 'Do you want to move again for free?')
                if second_move == 'Yes':
                    self.run(double=True)

        return 1


class Bus(Action):
    name = 'Take the bus'

    def available(self, remaining_actions=None):
        if self.player.role == REPORTER and not self.player.sanity:
            return False
        has_clue = [card for card in self.player.hand if not isinstance(card, Relic)]
        curr_loc = self.game.locations[self.player.location]
        return curr_loc.bus_stop and has_clue

    def run(self):
        discard = get_input([i for i in self.player.hand if isinstance(i, str)], None, 'Select a card to discard')
        self.player.hand.remove(discard)
        self.game.discard(discard)
        if discard == self.game.locations[self.player.location].town.name or (
                self.player.role == REPORTER and self.player.sanity):
            town = get_input(self.game.towns, 'name', 'You can move anywhere. First select a town')
            destination = get_input([l for l in town.locations], 'name',
                                    'Select a location within {}'.format(town.name))
        else:
            town = [t for t in self.game.towns if t.name == discard][0]
            destination = get_input(town.locations, 'name', 'Travel to a town in {}'.format(discard))

        self.game.move_player(destination.name)
        return 1


class DefeatCultist(Action):
    name = 'Defeat cultist'

    def available(self, remaining_actions=None):
        return self.curr_loc().cultists

    def run(self):
        if self.player.role == HUNTER:
            self.game.cultist_reserve += self.curr_loc().cultists
            self.curr_loc().cultists = 0
            self.game.announce('{} removes all cultists'.format(self.player.name()))
        else:
            self.curr_loc().cultists -= 1
            self.game.cultist_reserve += 1
            self.game.announce('{} removes 1 cultist'.format(self.player.name()))
        self.player.defeated_cultist_this_space = True
        self.game.show_board()
        return 1


class DefeatShoggoth(Action):
    name = 'Defeat Shoggoth'

    def available(self, remaining_actions):
        return self.curr_loc().shoggoth and remaining_actions >= self.defeat_shoggoth_cost()

    def run(self):
        cost = self.defeat_shoggoth_cost()
        self.curr_loc().shoggoth -= 1
        self.game.shoggoth_reserve += 1
        self.game.draw_relic_card(self.player)
        self.player.defeated_shoggoth_this_turn = True
        return cost


class SealGate(Action):
    name = 'Seal gate'

    def available(self, remaining_actions=None):
        seal_cost = self.game.seal_cost()
        base_cost = self.player.hand.count(self.curr_loc().town.name) >= seal_cost and self.curr_loc().gate
        if INCREASE_SEAL_COST in self.game.effects and base_cost:
            connected_towns = [town.name for town in self.curr_loc().town.connections]
            for c_town in connected_towns:
                if c_town in self.player.hand:
                    return True
        else:
            return base_cost

    def run(self):
        curr_loc = self.curr_loc()
        town = curr_loc.town
        seal_cost = self.game.seal_cost()
        for i in range(seal_cost):
            self.player.hand.remove(town.name)
            self.game.discard(town.name)
        if INCREASE_SEAL_COST in self.game.effects:
            connected_towns = self.curr_loc().town.connections
            connected_cards = []
            for ctown in connected_towns:
                if ctown.name in self.player.hand:
                    connected_cards.append(ctown)
            c_town = get_input([ctown for ctown in connected_towns if ctown.name in self.player.hand], 'name',
                               'Active effect requires a card from a connected town')
            self.player.hand.remove(c_town.name)
        self.game.seal_gate(town)
        if not self.player.sanity:
            self.player.sanity = 4
            locs = ['Hospital', 'Church']
            new_loc = get_input(locs, None, 'You regain your sanity and move to one of these locations')
            self.player.location = new_loc
        return 1


class GiveClueCard(Action):
    name = 'Give clue card for current town'

    def available(self, remaining_actions):
        shared = []
        if self.curr_loc().town.name in self.player.hand:
            for player in self.game.players:
                if player is not self.player and player.location == self.player.location:
                    shared.append(player)

        if shared:
            costs = []
            for player in shared:
                costs.append(self.give_take_clue_cost(self.player, player))
            if min(costs) <= remaining_actions:
                return shared
        return shared

    def run(self):
        curr_loc = self.curr_loc()
        transfer = curr_loc.town.name
        recipients = self.available(remaining_actions=2)  # assume available() already checked
        if len(recipients) == 1:
            recipient = recipients[0]
        else:
            recipient = get_input(recipients, 'name', 'Who do you want to give a card to?')
        self.player.hand.remove(transfer)
        recipient.hand.append(transfer)
        self.game.announce('{} gives {} to {}'.format(self.player.name(), transfer, recipient.name()))
        recipient.limit_hand()
        return self.give_take_clue_cost(self.player, recipient)


class TakeClueCard(Action):
    name = 'Take clue card for current town'

    def available(self, remaining_actions):
        curr_loc = self.curr_loc()
        shared = []
        town = curr_loc.town.name
        for player in self.game.players:
            if player is not self.player and player.location == curr_loc.name and town in player.hand:
                shared.append(player)

        costs = []
        if shared:
            for player in shared:
                costs.append(self.give_take_clue_cost(self.player, player))
            if min(costs) <= remaining_actions:
                return shared
        return shared

    def run(self):
        curr_loc = self.curr_loc()
        transfer = curr_loc.town.name
        candidates = self.available(remaining_actions=2)
        if len(candidates) == 1:
            candidate = candidates[0]
        else:
            candidate = get_input(candidates, 'name', 'Who do you want to take a card from?')
        candidate.hand.remove(transfer)
        self.player.hand.append(transfer)
        self.game.announce('{} takes {} from {}'.format(self.player.name(), transfer, candidate.name()))
        self.player.limit_hand()
        return self.give_take_clue_cost(self.player, candidate)


class GiveRelic(Action):
    name = "Give relic"

    def available(self, remaining_actions=None):
        if self.player.role == MAGICIAN and not self.player.sanity:
            return False
        shared = []
        if self.player.relics:
            for player in self.game.players:
                if player is not self.player and player.location == self.player.location:
                    shared.append(player)
        return shared

    def run(self, ):
        if len(self.player.relics) == 1:
            transfer = self.player.relics[0]
        else:
            transfer = get_input(self.player.relics, None, 'Which relic do you want to give?')
        recipients = self.available()
        if len(recipients) == 1:
            recipient = recipients[0]
        else:
            recipient = get_input(recipients, 'name', 'Who do you want to give the relic to?')
        self.player.hand.remove(transfer)
        recipient.hand.append(transfer)
        self.game.announce('{} gives {} to {}'.format(self.player.name(), transfer, recipient.name()))
        recipient.limit_hand()
        return self.give_take_relic_cost(self.player, recipient)


class TakeRelic(Action):
    name = 'Take relic'

    def available(self, remaining_actions=None):
        shared = []
        for player in self.game.players:
            if player is not self.player and player.location == self.player.location and player.relics:
                shared.append(player)
        return shared

    def run(self):
        candidates = self.available()
        if len(candidates) == 1:
            candidate = candidates[0]
        else:
            candidate = get_input(candidates, 'name', 'Who do you want to take a relic from?')
        if len(candidate.relics) == 1:
            transfer = candidate.relics[0]
        else:
            transfer = get_input(candidate.relics, None, 'Which relic do you want to take?')
        candidate.hand.remove(transfer)
        self.player.hand.append(transfer)
        self.game.announce('{} takes {} from {}'.format(self.player.name(), transfer, candidate.name()))
        self.player.limit_hand()
        return self.give_take_relic_cost(self.player, candidate)


class PlayRelic(Action):
    name = 'Play relic'

    def available(self, remaining_actions=None):
        if ACTIVE_PLAYER_ONLY in self.game.effects:
            return bool([card for card in self.player.relics if card.playable()])
        else:
            for player in self.game.players:
                relics = [card for card in player.relics if card.playable()]
                if relics:
                    return True

    def run(self, automate=False):
        all_relics = []
        if ACTIVE_PLAYER_ONLY in self.game.effects:
            all_relics = self.player.relics
        else:
            for player in self.game.players:
                all_relics.extend([card for card in player.relics if card.playable()])
        if automate:
            relic = automate
        else:
            relic = get_input(all_relics, None, 'Choose a relic to play', force=True)
        cost = 0
        for player in self.game.players:
            if relic in player.hand:
                cost = relic.play(player)
                player.hand.remove(relic)
        self.player.played_relic_this_turn = True
        return cost or 0


class UseGate(Action):
    name = 'Use a gate'

    def available(self, remaining_actions=None):
        if self.curr_loc().gate and not self.curr_loc().town.sealed and DISALLOW_GATE not in self.game.effects:
            destinations = [loc for loc in self.game.locations.values() if
                            loc is not self.curr_loc() and loc.gate and not loc.town.sealed]
            return destinations

    def run(self):
        destinations = self.available()
        if len(destinations) == 1:
            destination = destinations[0]
        else:
            destination = get_input(destinations, 'name', 'Where would you like to go?')
        self.game.announce(
            '{} takes the gate from {} to {}. This requires a sanity roll.'.format(self.player.name(),
                                                                                   self.player.location,
                                                                                   destination.name))
        self.player.location = destination.name
        self.game.sanity_roll()
        return 1


class MoveCultist(Action):
    name = 'Move cultist'

    def available(self, remaining_actions=None):
        cultist_locations = [loc for loc in self.game.locations.values() if loc.cultists]
        if self.player.role == OCCULTIST:
            return cultist_locations

    def run(self):
        locs = self.available()
        start = get_input(locs, 'name', 'Where do you want to move a cultist from?')
        dest = get_input(start.connections, 'name', 'Where do you want to move it to?')
        start.cultists -= 1
        self.game.add_cultist(dest.name)

        if self.player.sanity:
            second_move = get_input(['Yes', 'No'], None, 'Do you want to move this cultist again for free?')
            if second_move == 'Yes':
                dest2 = get_input(dest.connections, 'name', 'Where do you want to move it to?')
                dest.cultists -= 1
                self.game.add_cultist(dest2.name)
        else:
            second_move = get_input(['Yes', 'No'], None, 'Do you want to move another cultist?')
            if second_move == 'Yes':
                start = get_input(locs, 'name', 'Where do you want to move a cultist from?')
                dest = get_input(start.connections, 'name', 'Where do you want to move it to?')
                start.cultists -= 1
                self.game.add_cultist(dest.name)
        return 1


class MoveShoggoth(Action):
    name = 'Move shoggoth'

    def available(self, remaining_actions):
        shoggo = [loc for loc in self.game.locations.values() if loc.shoggoth]
        if self.player.role == OCCULTIST and self.player.sanity and remaining_actions >= 2:
            return shoggo

    def run(self):
        start = get_input(self.available(2), 'name', 'Where do you want to move a shoggoth from?')
        dest = get_input(start.connections, 'name', 'Where do you want to move it to?')
        start.shoggoth -= 1
        dest.shoggoth += 1

        for player in self.game.players:
            if player.location == dest.name:
                self.game.announce('Shoggoth enters the location of {}, performing a sanity roll'.format(
                    player.name()))
                self.game.sanity_roll(player)

        return 2


class Pass(Action):
    name = 'Pass'

    def available(self, remaining_actions=None):
        return True

    def run(self):
        return 1


class PrintRules(Action):
    name = 'Print Rules'

    def available(self, remaining_actions=None):
        return True

    def run(self):
        print_rules()
        return 0


def build_actions(game, player):
    # can't use inspect because it does not keep order
    return [
        Walk(game, player),
        Bus(game, player),
        UseGate(game, player),
        DefeatCultist(game, player),
        DefeatShoggoth(game, player),
        SealGate(game, player),
        GiveClueCard(game, player),
        TakeClueCard(game, player),
        GiveRelic(game, player),
        TakeRelic(game, player),
        PlayRelic(game, player),
        MoveCultist(game, player),
        MoveShoggoth(game, player),
        Pass(game, player),
        PrintRules(game, player)
    ]
