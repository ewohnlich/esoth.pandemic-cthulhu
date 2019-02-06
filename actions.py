from decks import Relic
from utils import get_input, MOVEMENT_RESTRICTION, DEFEAT_SHOGGOTH_COST, SEAL_GATE_BASE_COST, ACTIVE_PLAYER_ONLY


class Action(object):
    name = 'Action'

    def available(self, game, remaining_actions):
        return False

    def run(self, game):
        """ execute the action

        :param game:
        :return: action cost. For example move is 1, defeat shoggo is 3. We have to do this on run because some
        actions (relics) might increase/decrease cost. A relic that adds moves is expressed here as a negative cost
        """
        return 0

    @staticmethod
    def can_move(game):
        player = game.current_player
        if game.locations[player.location].cultists >= 2 and MOVEMENT_RESTRICTION in game.effects:
            return player.defeated_cultist_this_turn
        return True

    @staticmethod
    def player(game):
        return game.current_player

    def curr_loc(self, game):
        return game.locations[self.player(game).location]


class Walk(Action):
    name = 'Walk to a location'

    def available(self, game, remaining_actions):
        return self.can_move(game)

    def run(self, game, double=False):
        """ Walk to a location

        :param game: the master game
        :param double: the driver can move twice, and MUST if insane
        :return: action cost
        """
        player = game.current_player
        # get a location and move there. Sanity if shoggo
        conns = game.locations[player.location].connections
        new_loc = None
        if len(conns) == 1:
            new_loc = conns[0]
        if not new_loc:
            new_loc = get_input(conns, 'name', 'Where would you like to move?')
        game.move_player(new_loc.name)

        if not double:
            if player.role.move_modifier:
                second_move = True
                if player.sanity:
                    second_move = get_input(['Yes', 'No'], None, 'Do you want to move again for free?')
                if second_move == 'Yes':
                    self.run(game, double=True)

        return 1


class Bus(Action):
    name = 'Take the bus'

    def available(self, game, remaining_actions):
        player = game.current_player
        curr_loc = game.locations[player.location]
        has_clue = [card for card in player.hand if not isinstance(card, Relic)]
        return curr_loc.bus_stop and has_clue and self.can_move(game)

    def run(self, game):
        player = game.current_player
        discard = get_input([i for i in player.hand if isinstance(i, str)], None, 'Select a card to discard')
        player.hand.remove(discard)
        game.discard(discard)
        if discard == game.locations[player.location].town.name:
            town = get_input(game.towns, 'name', 'By discarding a card from your current town, you can move '
                                                 'anywhere. First select a town')
            destination = get_input([l for l in town.locations], 'name',
                                    'Select a location within {}'.format(town.name))
        else:
            town = [t for t in game.towns if t.name == discard][0]
            destination = get_input(town.locations, 'name', 'Travel to a town in {}'.format(discard))
        game.move_player(destination.name)
        return 1


class DefeatCultist(Action):
    name = 'Defeat cultist'

    def available(self, game, remaining_actions):
        return self.curr_loc(game).cultists

    def run(self, game):
        player = self.player(game)
        if player.role.clear_all_cultists:
            game.cultist_reserve += self.curr_loc(game).cultists
            self.curr_loc(game).cultists = 0
            game.announce('{} removes all cultists'.format(player.name()))
        else:
            self.curr_loc(game).cultists -= 1
            game.announce('{} removes 1 cultist'.format(player.name()))
        player.defeated_cultist_this_turn = True
        game.show_board()
        return 1


class DefeatShoggoth(Action):
    name = 'Defeat Shoggoth'

    def available(self, game, remaining_actions):
        return self.curr_loc(game).shoggoth and remaining_actions >= DEFEAT_SHOGGOTH_COST

    def run(self, game):
        self.curr_loc(game).shoggoth -= 1
        game.shoggoth_reserve += 1
        game.draw_relic_card(self)
        return 3


class SealGate(Action):
    name = 'Seal gate'

    def available(self, game, remaining_actions):
        player = self.player(game)
        return player.hand.count(self.curr_loc(game).town.name) + player.role.seal_modifier >= SEAL_GATE_BASE_COST

    def run(self, game):
        curr_loc = self.curr_loc(game)
        town = curr_loc.town
        seal_cost = game.seal_cost(self.player(game).role.seal_modifier)
        for i in range(seal_cost):
            self.player(game).hand.remove(town.name)
            game.discard(town.name)
        game.seal_gate(town)
        return 1


class GiveClueCard(Action):
    name = 'Give clue card for current town'

    def available(self, game, remaining_actions=None):
        shared = []
        curr_player = self.player(game)
        if self.curr_loc(game).town.name in curr_player.hand:
            for player in game.players:
                if player is not self and player.location == curr_player.location:
                    shared.append(player)
        return shared

    def run(self, game):
        curr_loc = self.curr_loc(game)
        player = self.player(game)
        transfer = curr_loc.town.name
        recipients = self.available(game)
        if len(recipients) == 1:
            recipient = recipients[0]
        else:
            recipient = get_input(recipients, 'name', 'Who do you want to give a card to?')
        player.hand.remove(transfer)
        recipient.hand.append(transfer)
        game.announce('{} gives {} to {}'.format(player.name(), transfer, recipient.name()))
        recipient.limit_hand(game)
        return 1


class TakeClueCard(Action):
    name = 'Take clue card for current town'

    def available(self, game, remaining_actions=None):
        curr_loc = self.curr_loc(game)
        shared = []
        town = curr_loc.town.name
        for player in game.players:
            if player is not self and player.location == curr_loc.name and town in player.hand:
                shared.append(player)
        return shared

    def run(self, game):
        curr_loc = self.curr_loc(game)
        player = self.player(game)
        transfer = curr_loc.town.name
        candidates = self.available(game)
        if len(candidates) == 1:
            candidate = candidates[0]
        else:
            candidate = get_input(candidates, 'name', 'Who do you want to take a card from?')
        candidate.hand.remove(transfer)
        player.hand.append(transfer)
        game.announce('{} takes {} from {}'.format(player.name(), transfer, candidate.name()))
        player.limit_hand(game)
        return 1


class GiveRelic(Action):
    name = "Give relic"

    def available(self, game, remaining_actions=None):
        shared = []
        if self.player(game).relics:
            for player in game.players:
                if player is not self and player.location == self.player(game).location:
                    shared.append(player)
        return shared

    def run(self, game):
        player = self.player(game)
        if len(player.relics) == 1:
            transfer = player.relics[0]
        else:
            transfer = get_input(player.relics, None, 'Which relic do you want to give?')
        recipients = self.available(game)
        if len(recipients) == 1:
            recipient = recipients[0]
        else:
            recipient = get_input(recipients, 'name', 'Who do you want to give the relic to?')
        player.hand.remove(transfer)
        recipient.hand.append(transfer)
        game.announce('{} gives {} to {}'.format(player.name(), transfer, recipient.name()))
        recipient.limit_hand(game)
        return 1


class TakeRelic(Action):
    name = 'Take relic'

    def available(self, game, remaining_actions=None):
        shared = []
        for player in game.players:
            if player is not self and player.location == self.player(game).location and player.relics:
                shared.append(player)
        return shared

    def run(self, game):
        player = self.player(game)
        candidates = self.available(game)
        if len(candidates) == 1:
            candidate = candidates[0]
        else:
            candidate = get_input(candidates, 'name', 'Who do you want to take a relic from?')
        if len(candidate.relics) == 1:
            transfer = candidate.relics[0]
        else:
            transfer = get_input(candidate.relics, None, 'Which relic do you want to take?')
        candidate.hand.remove(transfer)
        player.hand.append(transfer)
        game.announce('{} takes {} from {}'.format(player.name(), transfer, candidate.name()))
        player.limit_hand(game)
        return 1


class PlayRelic(Action):
    name = 'Play relic'

    def available(self, game, remaining_actions=None):
        if ACTIVE_PLAYER_ONLY in game.effects:
            return bool([card for card in self.player(game).relics if card.playable(game)])
        else:
            for player in game.players:
                relics = [card for card in player.relics if card.playable(game)]
                if relics:
                    return True

    def run(self, game):
        all_relics = []
        if ACTIVE_PLAYER_ONLY in game.effects:
            all_relics = self.player(game).relics
        else:
            for player in game.players:
                all_relics.extend([card for card in player.relics if card.playable(game)])
        relic = get_input(all_relics, None, 'Choose a relic to play', force=True)
        cost = 0
        for player in game.players:
            if relic in player.hand:
                cost = relic.play(game, player)
                player.hand.remove(relic)
        return cost or 0


class UseGateway(Action):
    name = 'Use gateway'

    def available(self, game, remaining_actions=None):
        if MOVEMENT_RESTRICTION in game.effects:
            return False
        curr_loc = game.locations[self.player(game).location]
        if curr_loc.gate and not curr_loc.town.sealed:
            destinations = [loc for loc in game.locations.values() if
                            loc is not curr_loc and loc.gate and not loc.town.sealed]
            return destinations

    def run(self, game):
        player = self.player(game)
        destinations = self.available(game)
        if len(destinations) == 1:
            destination = destinations[0]
        else:
            destination = get_input(destinations, 'name', 'Where would you like to go?')
        game.announce(
            '{} takes the gate from {} to {}. This requires a sanity roll.'.format(player.name(), player.location,
                                                                                   destination.name))
        game.sanity_roll()
        player.location = destination.name


class Pass(Action):
    name = 'Pass'

    def available(self, game, remaining_actions):
        return True

    def run(self, game):
        return 1


def get_actions():
    # can't use inspect because it does not keep order
    return [
        Walk(),
        Bus(),
        UseGateway(),
        DefeatCultist(),
        DefeatShoggoth(),
        SealGate(),
        GiveClueCard(),
        TakeClueCard(),
        GiveRelic(),
        TakeRelic(),
        PlayRelic(),
        Pass(),
    ]
