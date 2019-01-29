from game import GameBoard
from decks import *
from printer import print_elder_map


def test_shubmell(game):
    game.old_gods[0].action = shudmell_action
    game.awakening_ritual()


def test_sealgate(game):
    game.players[0].hand += ['Arkham']*4


if __name__ == '__main__':
    game = GameBoard()
    game.play()
    # import code
    # variables = globals().copy()
    # variables.update(locals())
    # shell = code.InteractiveConsole(variables)
    # shell.interact()
    # game.move_shoggoths()
    # game.move_shoggoths()
