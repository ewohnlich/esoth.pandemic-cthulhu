from game import GameBoard
from printer import print_player_hands, print_old_gods

if __name__ == '__main__':
    game = GameBoard()
    print_player_hands(game)
    print_old_gods(game)
    import code
    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.interact()
