from game import GameBoard
from decks import *


def test_shubmell(game):
    game.old_gods[0].action = shudmell_action
    game.awakening_ritual()


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
