def print_player_hands(game):
    for player in game.players:
        print('Hand for {}: -- {} cards -- {}'.format(player.name(), len(player.hand),
                                              ', '.join(sorted(map(str, player.hand), ))))


def print_shoggoth_locations(game):
    locs = []
    for loc in game.locations:
        if game.locations[loc].shoggoth:
            locs.append(loc)
    print('Shoggoths located at: {}'.format(', '.join(locs)))


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
 $=shoggoth *=cultist <b>=bus stop ( )=open gate (X)=sealed gate (E)=Elder Sign gate
"""


def print_elder_map(game):
    elder_map = ELDER_MAP.replace('s[ ]c[ ] ', '{}')
    gods = ' '.join([god.revealed and god.name or '*' for god in game.old_gods])
    order = ['Train Station', 'University', 'Police Station', 'Diner', 'Junkyard', 'Hospital', 'Boardwalk',
             'Park', 'Secret Lodge', 'Pawn Shop', 'Factory', 'Docks', 'Cafe', 'Church', 'Historic Inn', 'Woods',
             'Market', 'Wharf', 'Old Mill', 'Farmstead', 'Swamp', 'Great Hall', 'Theater', 'Graveyard']
    details = []
    for loc in order:
        players = ''.join([str(player.number) for player in game.players if player.location == loc])
        monsters = '{: <5}'.format('$' * game.locations[loc].shoggoth + '*' * game.locations[loc].cultists)
        details.append(monsters + '{: <4}'.format(players))

    elder_map = elder_map.format(gods, len(game.player_deck), len(game.player_discards), len(game.relic_deck),
                                 len(game.summon_discards), game.cultist_reserve, game.shoggoth_reserve, *details)
    elder_map = elder_map.replace('(G)', '({})')
    elder_map = elder_map.format(*[town.elder_sign and 'E' or town.sealed and 'X' or ' ' for town in game.towns])
    print(elder_map)
