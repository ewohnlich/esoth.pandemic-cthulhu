from decks import Relic
from utils import get_input, MOVEMENT_RESTRICTION, DEFEAT_SHOGGOTH_COST, SEAL_GATE_BASE_COST, ACTIVE_PLAYER_ONLY


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

    def can_move(self):
        player = self.game.current_player
        if self.game.locations[player.location].cultists >= 2 and MOVEMENT_RESTRICTION in self.game.effects:
            return player.defeated_cultist_this_turn
        return True

    def curr_loc(self):
        """ :returns game.Location object, not location name """
        return self.game.locations[self.player.location]


class Walk(Action):
    name = 'Walk to a location'

    def available(self, remaining_actions):
        return self.can_move()

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

        if not double:
            if self.player.role.move_modifier:
                second_move = True
                if self.player.sanity:
                    second_move = get_input(['Yes', 'No'], None, 'Do you want to move again for free?')
                if second_move == 'Yes':
                    self.run(double=True)

        return 1


class Bus(Action):
    name = 'Take the bus'

    def available(self, remaining_actions):
        curr_loc = self.game.locations[self.player.location]
        has_clue = [card for card in self.player.hand if not isinstance(card, Relic)]
        return curr_loc.bus_stop and has_clue and self.can_move()

    def run(self):
        discard = get_input([i for i in self.player.hand if isinstance(i, str)], None, 'Select a card to discard')
        self.player.hand.remove(discard)
        self.game.discard(discard)
        if discard == self.game.locations[self.player.location].town.name:
            town = get_input(self.game.towns, 'name', 'By discarding a card from your current town, you can move '
                                                      'anywhere. First select a town')
            destination = get_input([l for l in town.locations], 'name',
                                    'Select a location within {}'.format(town.name))
        else:
            town = [t for t in self.game.towns if t.name == discard][0]
            destination = get_input(town.locations, 'name', 'Travel to a town in {}'.format(discard))

        self.game.move_player(destination.name)
        return 1


class DefeatCultist(Action):
    name = 'Defeat cultist'

    def available(self, remaining_actions):
        return self.curr_loc().cultists

    def run(self):
        if self.player.role.clear_all_cultists:
            self.game.cultist_reserve += self.curr_loc().cultists
            self.curr_loc().cultists = 0
            self.game.announce('{} removes all cultists'.format(self.player.name()))
        else:
            self.curr_loc().cultists -= 1
            self.game.announce('{} removes 1 cultist'.format(self.player.name()))
        self.player.defeated_cultist_this_turn = True
        self.game.show_board()
        return 1


class DefeatShoggoth(Action):
    name = 'Defeat Shoggoth'

    def available(self, remaining_actions):
        return self.curr_loc().shoggoth and remaining_actions >= DEFEAT_SHOGGOTH_COST

    def run(self):
        self.curr_loc().shoggoth -= 1
        self.game.shoggoth_reserve += 1
        self.game.draw_relic_card(self)
        return 3


class SealGate(Action):
    name = 'Seal gate'

    def available(self, remaining_actions):
        return self.player.hand.count(self.curr_loc().town.name) + self.player.role.seal_modifier >= SEAL_GATE_BASE_COST

    def run(self):
        curr_loc = self.curr_loc()
        town = curr_loc.town
        seal_cost = self.game.seal_cost(self.player.role.seal_modifier)
        for i in range(seal_cost):
            self.player(self.game).hand.remove(town.name)
            self.game.discard(town.name)
            self.game.seal_gate(town)
        return 1


class GiveClueCard(Action):
    name = 'Give clue card for current town'

    def available(self, remaining_actions=None):
        shared = []
        if self.curr_loc().town.name in self.player.hand:
            for player in self.game.players:
                if player is not self.player and player.location == self.player.location:
                    shared.append(player)
        return shared

    def run(self):
        curr_loc = self.curr_loc()
        transfer = curr_loc.town.name
        recipients = self.available()
        if len(recipients) == 1:
            recipient = recipients[0]
        else:
            recipient = get_input(recipients, 'name', 'Who do you want to give a card to?')
        self.player.hand.remove(transfer)
        recipient.hand.append(transfer)
        self.game.announce('{} gives {} to {}'.format(self.player.name(), transfer, recipient.name()))
        recipient.limit_hand(self.game)
        return 1


class TakeClueCard(Action):
    name = 'Take clue card for current town'

    def available(self, remaining_actions=None):
        curr_loc = self.curr_loc()
        shared = []
        town = curr_loc.town.name
        for player in self.game.players:
            if player is not self.player and player.location == curr_loc.name and town in player.hand:
                shared.append(player)
        return shared

    def run(self):
        curr_loc = self.curr_loc()
        transfer = curr_loc.town.name
        candidates = self.available()
        if len(candidates) == 1:
            candidate = candidates[0]
        else:
            candidate = get_input(candidates, 'name', 'Who do you want to take a card from?')
        candidate.hand.remove(transfer)
        self.player.hand.append(transfer)
        self.game.announce('{} takes {} from {}'.format(self.player.name(), transfer, candidate.name()))
        self.player.limit_hand(self.game)
        return 1


class GiveRelic(Action):
    name = "Give relic"

    def available(self, remaining_actions=None):
        shared = []
        if self.player.relics:
            for player in self.game.players:
                if player is not self and player.location == self.player.location:
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
        recipient.limit_hand(self.game)
        return 1


class TakeRelic(Action):
    name = 'Take relic'

    def available(self, remaining_actions=None):
        shared = []
        for player in self.game.players:
            if player is not self and player.location == self.player.location and player.relics:
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
        self.player.limit_hand(self.game)
        return 1


class PlayRelic(Action):
    name = 'Play relic'

    def available(self, remaining_actions=None):
        if ACTIVE_PLAYER_ONLY in self.game.effects:
            return bool([card for card in self.player.relics if card.playable(self.game)])
        else:
            for player in self.game.players:
                relics = [card for card in player.relics if card.playable(self.game)]
                if relics:
                    return True

    def run(self):
        all_relics = []
        if ACTIVE_PLAYER_ONLY in self.game.effects:
            all_relics = self.player.relics
        else:
            for player in self.game.players:
                all_relics.extend([card for card in player.relics if card.playable(self.game)])
        relic = get_input(all_relics, None, 'Choose a relic to play', force=True)
        cost = 0
        for player in self.game.players:
            if relic in player.hand:
                cost = relic.play(self.game, player)
                player.hand.remove(relic)
        return cost or 0


class UseGateway(Action):
    name = 'Use gateway'

    def available(self, remaining_actions=None):
        if MOVEMENT_RESTRICTION in self.game.effects:
            return False
        if self.curr_loc().gate and not self.curr_loc().town.sealed:
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
        self.game.sanity_roll()
        self.player.location = destination.name


class Pass(Action):
    name = 'Pass'

    def available(self, remaining_actions):
        return True

    def run(self):
        return 1


def build_actions(game, player):
    # can't use inspect because it does not keep order
    return [
        Walk(game, player),
        Bus(game, player),
        UseGateway(game, player),
        DefeatCultist(game, player),
        DefeatShoggoth(game, player),
        SealGate(game, player),
        GiveClueCard(game, player),
        TakeClueCard(game, player),
        GiveRelic(game, player),
        TakeRelic(game, player),
        PlayRelic(game, player),
        Pass(game, player),
    ]
