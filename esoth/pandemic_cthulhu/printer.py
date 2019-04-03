def print_player_hands(game):
    for player in game.players:
        print('{}: {} sanity -- {} cards: {}'.format(player.name(), player.sanity, len(player.hand),
                                                     ', '.join(sorted(map(str, player.hand), ))), file=game.stream)


def print_shoggoth_locations(game):
    locs = []
    for loc in game.locations:
        if game.locations[loc].shoggoth:
            locs.append(loc)
    print('Shoggoths located at: {}'.format(', '.join(locs)), file=game.stream)


ELDER_MAP = """
Old Gods: {}
Player cards: {} (discard: {})  Relic cards: {}  Summon discards: {}     Cultist reserve: {}  Shoggoth reserve: {}
                      ARKHAM                                                       INNSMOUTH
Train Station<b> - University ----- Police Station    Diner<b> ------- Junkyard     Hospital(G)  Boardwalk
| s[ ]c[ ]       | s[ ]c[ ]      / | s[ ]c[ ]       _/ s[ ]c[ ]        | s[ ]c[ ]  /|s[ ]c[ ]   /| s[ ]c[ ] 
|                |        ______/  |             __/                   |          / |          / |
|                Park(G) /-------- Secret Lodge /                      Pawn Shop / Factory<b> /  Docks
|                  s[ ]c[ ]         s[ ]c[ ]                            s[ ]c[ ]     s[ ]c[ ]   / s[ ]c[ ] 
|                 DUNWICH                                      ________________________________/
Cafe ----------- Church ------- Historic Inn<b>         Woods /------ Market<b> ---- Wharf
  s[ ]c[ ]     /| s[ ]c[ ]    /  s[ ]c[ ]              | s[ ]c[ ]   / | s[ ]c[ ]    | s[ ]c[ ] 
              / |           _/                         |           /  |             |                 KINGSPORT
 Old Mill(G) /   Farmstead /---- Swamp --------------- Great Hall /   Theater       Graveyard(G)
   s[ ]c[ ]      s[ ]c[ ]        s[ ]c[ ]               s[ ]c[ ]       s[ ]c[ ]      s[ ]c[ ] 

Effects: {}
 $=shoggoth *=cultist <b>=bus stop ( )=open gate (X)=sealed gate (E)=Elder Sign gate
"""

ELDER_MAP_HTML = """
Old Gods: {}
Player cards: {} (discard: {})  Relic cards: {}  Summon discards: {}     Cultist reserve: {}  Shoggoth reserve: {}
                      ARKHAM                                                       INNSMOUTH
Train Station<i class="icon-bus"/> - University ----- Police Station    Diner<i class="icon-bus"/> ------- Junkyard     Hospital(G)  Boardwalk
| s[ ]c[ ]       | s[ ]c[ ]      / | s[ ]c[ ]       _/ s[ ]c[ ]        | s[ ]c[ ]  /|s[ ]c[ ]   /| s[ ]c[ ] 
|                |        ______/  |             __/                   |          / |          / |
|                Park(G) /-------- Secret Lodge /                      Pawn Shop / Factory<i class="icon-bus"/> /  Docks
|                  s[ ]c[ ]         s[ ]c[ ]                            s[ ]c[ ]     s[ ]c[ ]   / s[ ]c[ ] 
|                 DUNWICH                                      ________________________________/
Cafe ----------- Church ------- Historic Inn<i class="icon-bus"/>         Woods /------ Market<i class="icon-bus"/> ---- Wharf
  s[ ]c[ ]     /| s[ ]c[ ]    /  s[ ]c[ ]              | s[ ]c[ ]   / | s[ ]c[ ]    | s[ ]c[ ] 
              / |           _/                         |           /  |             |                 KINGSPORT
 Old Mill(G) /   Farmstead /---- Swamp --------------- Great Hall /   Theater       Graveyard(G)
   s[ ]c[ ]      s[ ]c[ ]        s[ ]c[ ]               s[ ]c[ ]       s[ ]c[ ]      s[ ]c[ ] 

Effects: {}
 $=shoggoth *=cultist ( )=open gate (X)=sealed gate (E)=Elder Sign gate
"""


def get_elder_map(game, html=False):
    if html:
        emap = ELDER_MAP_HTML
    else:
        emap = ELDER_MAP
    elder_map = emap.replace('s[ ]c[ ] ', '{}')
    gods = ' '.join([god.revealed and god.name or '*' for god in game.old_gods])
    order = ['Train Station', 'University', 'Police Station', 'Diner', 'Junkyard', 'Hospital', 'Boardwalk',
             'Park', 'Secret Lodge', 'Pawn Shop', 'Factory', 'Docks', 'Cafe', 'Church', 'Historic Inn', 'Woods',
             'Market', 'Wharf', 'Old Mill', 'Farmstead', 'Swamp', 'Great Hall', 'Theater', 'Graveyard']
    details = []
    for loc in order:
        players = ''.join([str(player.number) for player in game.players if player.location == loc])
        if html:
            monsters = '{: <5}'.format('<i class="icon-shogg"/>' * game.locations[loc].shoggoth + '*' * game.locations[loc].cultists)
        else:
            monsters = '{: <5}'.format('$' * game.locations[loc].shoggoth + '*' * game.locations[loc].cultists)
        details.append(monsters + '{: <4}'.format(players))

    elder_map = elder_map.format(gods, len(game.player_deck), len(game.player_discards), len(game.relic_deck),
                                 len(game.summon_discards), game.cultist_reserve, game.shoggoth_reserve, *details,
                                 ', '.join(game.effects))
    elder_map = elder_map.replace('(G)', '({})')
    town_order = ('Innsmouth', 'Arkham', 'Dunwich', 'Kingsport')
    towns = sorted(game.towns, key=lambda x: town_order.index(x.name))  # when printing map, Innsmouth comes first
    elder_map = elder_map.format(*[town.elder_sign and 'E' or town.sealed and 'X' or ' ' for town in towns])
    return elder_map


def print_elder_map(game):
    print(get_elder_map(game), file=game.stream)
    print_player_hands(game)


RULES = """ Win condition: seal all four gates
Loss condition: No cultists left in reserves when needed, no shoggoth left in reserves when needed, player draw deck is
empty when needed, all players are insane, or Cthulhu has been summoned.

Player turn:
1. Perform actions (4 is default, but changes based on sanity and some roles)
2. Draw two cards which are either Town Clue cards, a Relic (special bonuses), or Evil Stirs (bad things!)
3. Draw summon cards at the current summoning rate (2 for first half of old gods, 3 for second half)

Actions:
* Walk to a location
* Take the bus - at bus stops, discard current town card to go anywhere. Or another town card to go somewhere in that town
* Use gate - use gate to go to another gate
* Trade town clue cards or relic cards with a player in the same location. For clue cards, must be the current town
* Seal gate - default requirement of 5 of the current town clue cards
* Use relic
* Defeat cultist
* Defeat shoggoth (requires 3 actions)

Sanity Roll:
On a sanity roll you might lose 1 sanity, 2 sanity, or summon 2 cultists. This action is performed when entering a
location with a shoggoth or a shoggoth enters your location, when using a Relic card, during an Evil Stirs draw, or
some other special events
"""


def print_rules():
    print(RULES)
