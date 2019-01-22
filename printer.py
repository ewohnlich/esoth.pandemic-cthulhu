def print_player_hands(game):
    for player in game.players:
        print('{}: {}'.format(player.name, sorted(player.hand)))
