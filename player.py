from decks import PandemicCard, Relic
from utils import PandemicObject, get_input, SEAL_GATE_BASE_COST, SANITY_BASE, DEFEAT_SHOGGOTH_COST, ACTIONS_BASE, \
    SKIP_SUMMON, ACTIVE_PLAYER_ONLY, MOVEMENT_RESTRICTION

PLAYERS = 1


class Player(PandemicObject):
    hand = None
    effects = None
    sanity = SANITY_BASE
    role = None
    number = 0
    location = 'Train Station'
    seal_modifier = 0
    defeated_cultist_this_turn = False

    def __init__(self):
        global PLAYERS
        self.number = PLAYERS
        PLAYERS += 1
        self.hand = []
        self.effects = []

    def name(self):
        return '{}({})'.format(self.role.name, self.number)

    def deal(self, game, count=1):
        """ Don't check hand limit until all cards have been dealt """
        for i in range(count):
            card = game.draw_player_card()
            game.announce('{} drew a card: {}'.format(self.role.name, hasattr(card, 'name') and card.name or card))
            if isinstance(card, PandemicCard) and card.name == 'Evil Stirs':
                card.activate(game, self)
            else:
                self.hand.append(card)
                self.hand = sorted(self.hand)

        self.limit_hand(game)

    def limit_hand(self, game):
        while len(self.hand) > 7:
            discard = get_input(self.hand, None,
                                '{} is over the hand limit. Enter a number to discard'.format(self.name()))
            self.hand.remove(discard)
            game.discard(discard)

    def do_turn(self, game):
        self.defeated_cultist_this_turn = False  # reset
        actions = ACTIONS_BASE + self.role.action_modifier
        if not self.sanity:
            actions -= 1
        while actions > 0:
            cost = self.do_action(game, actions)
            actions -= cost or 0
        game.announce('{} actions over, now drawing cards...\n'.format(self.role.name))
        self.deal(game, count=2)
        if SKIP_SUMMON not in game.effects:
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
        self.defeated_cultist_this_turn = True
        game.show_board()
        return 1

    def action_defeat_shoggoth(self, game):
        game.locations[self.location].shoggoth -= 1
        game.shoggoth_reserve += 1
        game.draw_relic_card(self)
        return 3

    def action_walk(self, game, double=False):
        """ Walk

        :param game: the master game
        :param double: the driver can move twice, and MUST if insane
        :return:
        """
        # get a location and move there. Sanity if shoggo
        conns = game.locations[self.location].connections
        new_loc = None
        if len(conns) == 1:
            new_loc = conns[0]
        if not new_loc:
            new_loc = get_input(conns, 'name', 'Where would you like to move?')
        game.move_player(new_loc.name)

        if not double:
            if self.role.move_modifier:
                second_move = True
                if self.sanity:
                    second_move = get_input(['Yes', 'No'], None, 'Do you want to move again for free?')
                if second_move == 'Yes':
                    self.action_walk(game, double=True)

        return 1

    def action_bus(self, game):
        discard = get_input([i for i in self.hand if isinstance(i, str)], None, 'Select a card to discard')
        self.hand.remove(discard)
        game.discard(discard)
        if discard == game.locations[self.location].town.name:
            town = get_input(game.towns, 'name', 'By discarding a card from your current town, you can move '
                                                 'anywhere. First select a town')
            destination = get_input([l for l in town.locations], 'name',
                                    'Select a location within {}'.format(town.name))
        else:
            town = [t for t in game.towns if t.name == discard][0]
            destination = get_input(town.locations, 'name', 'Travel to a town in {}'.format(discard))
        game.move_player(destination.name)
        return 1

    def action_seal_gate(self, game):
        town = game.locations[self.location].town
        seal_cost = game.seal_cost(self.role.seal_modifier)
        for i in range(seal_cost):
            self.hand.remove(town.name)
            game.discard(town.name)
        game.seal_gate(town)
        return 1

    def ppass(self, game):
        """ Player passes """
        return 1

    def can_gateway(self, game):
        if MOVEMENT_RESTRICTION in game.effects:
            return False
        curr_loc = game.locations[self.location]
        if curr_loc.gate and not curr_loc.town.sealed:
            destinations = [loc for loc in game.locations.values() if
                            loc is not curr_loc and loc.gate and not loc.town.sealed]
            return destinations

    def action_gateway(self, game):
        destinations = self.can_gateway(game)
        if len(destinations) == 1:
            destination = destinations[0]
        else:
            destination = get_input(destinations, 'name', 'Where would you like to go?')
        game.announce('{} takes the gate from {} to {}. This requires a sanity roll.'.format(self.name(), self.location,
                                                                                             destination.name))
        game.sanity_roll()
        self.location = destination.name

    @property
    def relics(self):
        return [card for card in self.hand if isinstance(card, Relic)]

    def give_town_card_recipients(self, game):
        shared = []
        if game.locations[self.location].town.name in self.hand:
            for player in game.players:
                if player is not self and player.location == self.location:
                    shared.append(player)
        return shared

    def give_relic_recipients(self, game):
        shared = []
        if self.relics:
            for player in game.players:
                if player is not self and player.location == self.location:
                    shared.append(player)
        return shared

    def take_town_card_candidates(self, game):
        shared = []
        town = game.locations[self.location].town.name
        for player in game.players:
            if player is not self and player.location == self.location and town in player.hand:
                shared.append(player)
        return shared

    def take_relic_candidates(self, game):
        shared = []
        for player in game.players:
            if player is not self and player.location == self.location and player.relics:
                shared.append(player)
        return shared

    def action_give_town_card(self, game):
        transfer = game.locations[self.location].town.name
        recipients = self.give_town_card_recipients(game)
        if len(recipients) == 1:
            recipient = recipients[0]
        else:
            recipient = get_input(recipients, 'name', 'Who do you want to give a card to?')
        self.hand.remove(transfer)
        recipient.hand.append(transfer)
        game.announce('{} gives {} to {}'.format(self.name(), transfer, recipient.name()))
        recipient.limit_hand(game)
        return 1

    def action_give_relic(self, game):
        if len(self.relics) == 1:
            transfer = self.relics[0]
        else:
            transfer = get_input(self.relics, None, 'Which relic do you want to give?')
        recipients = self.give_relic_recipients(game)
        if len(recipients) == 1:
            recipient = recipients[0]
        else:
            recipient = get_input(recipients, 'name', 'Who do you want to give the relic to?')
        self.hand.remove(transfer)
        recipient.hand.append(transfer)
        game.announce('{} gives {} to {}'.format(self.name(), transfer, recipient.name()))
        recipient.limit_hand(game)
        return 1

    def action_take_town_card(self, game):
        transfer = game.locations[self.location].town.name
        candidates = self.take_town_card_candidates(game)
        if len(candidates) == 1:
            candidate = candidates[0]
        else:
            candidate = get_input(candidates, 'name', 'Who do you want to take a card from?')
        candidate.hand.remove(transfer)
        self.hand.append(transfer)
        game.announce('{} takes {} from {}'.format(self.name(), transfer, candidate.name()))
        self.limit_hand(game)
        return 1

    def action_take_relic(self, game):
        candidates = self.take_relic_candidates(game)
        if len(candidates) == 1:
            candidate = candidates[0]
        else:
            candidate = get_input(candidates, 'name', 'Who do you want to take a relic from?')
        if len(candidate.relics) == 1:
            transfer = candidate.relics[0]
        else:
            transfer = get_input(candidate.relics, None, 'Which relic do you want to take?')
        candidate.hand.remove(transfer)
        self.hand.append(transfer)
        game.announce('{} takes {} from {}'.format(self.name(), transfer, candidate.name()))
        self.limit_hand(game)
        return 1

    def can_playrelic(self, game):
        if ACTIVE_PLAYER_ONLY in game.effects:
            return bool([card for card in self.relics if card.playable(game)])
        else:
            for player in game.players:
                relics = [card for card in player.relics if card.playable(game)]
                if relics:
                    return True

    def action_play_relic(self, game):
        all_relics = []
        if ACTIVE_PLAYER_ONLY in game.effects:
            all_relics = self.relics
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

    def do_action(self, game, remaining_actions):
        """ TODO: convert these into Action subclasses? """
        available = []
        can_move = True
        if game.locations[self.location].cultists >= 2 and MOVEMENT_RESTRICTION in game.effects:
            can_move = self.defeated_cultist_this_turn

        if can_move:
            available.append({'title': 'Walk to a location', 'action': self.action_walk, })
        curr_loc = game.locations[self.location]
        if curr_loc.bus_stop and self.hand and can_move:
            available.append({'title': 'Take the bus', 'action': self.action_bus})
        if curr_loc.cultists:
            available.append({'title': 'Defeat cultist', 'action': self.action_defeat_cultist})
        if curr_loc.shoggoth and remaining_actions >= DEFEAT_SHOGGOTH_COST:
            available.append({'title': 'Defeat shoggoth', 'action': self.action_defeat_shoggoth})
        if curr_loc.gate and not curr_loc.town.sealed:
            if self.hand.count(curr_loc.town.name) + self.role.seal_modifier >= SEAL_GATE_BASE_COST:
                available.append({'title': 'Seal gate', 'action': self.action_seal_gate})
        if self.give_town_card_recipients(game):
            available.append({'title': 'Give current town card', 'action': self.action_give_town_card})
        if self.take_town_card_candidates(game):
            available.append({'title': 'Take current town card', 'action': self.action_take_town_card})
        if self.give_relic_recipients(game):
            available.append({'title': 'Give relic', 'action': self.action_give_relic})
        if self.take_relic_candidates(game):
            available.append({'title': 'Take relic', 'action': self.action_take_relic})
        if self.can_gateway(game):
            available.append({'title': 'Use gateway', 'action': self.action_gateway})
        if self.can_playrelic(game):
            available.append({'title': 'Play relic', 'action': self.action_play_relic})

        available.append({'title': 'Pass', 'action': self.ppass})
        opt = get_input(available, 'title', 'You have {} action(s) remaining.'.format(remaining_actions))

        return opt['action'](game)
