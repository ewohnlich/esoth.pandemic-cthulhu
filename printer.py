def print_player_hands(game):
    for player in game.players:
        print('{}: {}'.format(player.name, sorted(player.hand)))


def print_old_gods(game):
    for god in game.old_gods:
        if god.revealed:
            print(god.name)
        else:
            print('***')
