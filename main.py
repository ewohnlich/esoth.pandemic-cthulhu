from game import GameBoard
from decks import *
from printer import print_elder_map


def test_shubmell(game):
    game.old_gods[0] = ShudMell()
    game.awakening_ritual()


def test_ithaqua(game):
    game.locations['Train Station'].cultists = 2
    game.old_gods[0] = Ithaqua()
    game.awakening_ritual()


def test_sealgate(game):
    game.players[0].hand += ['Arkham'] * 4


def test_xaosmirror(game):
    game.players[0].hand.append(XaosMirror())


def test_atlatcnacha(game):
    AtlatchNacha().activate(game)


def test_tsathaggua(game):
    Tsathaggua().activate(game)


def test_eldersign(game):
    game.towns[0].sealed = True
    game.players[0].hand.append(ElderSign())


def test_last_hourglass(game):
    game.players[0].hand.append(LastHourglass())


if __name__ == '__main__':
    game = GameBoard()
    test_ithaqua(game)
    game.play()
    # import code
    # variables = globals().copy()
    # variables.update(locals())
    # shell = code.InteractiveConsole(variables)
    # shell.interact()
    # game.move_shoggoths()
    # game.move_shoggoths()
