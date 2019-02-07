from esoth.pandemic_cthulhu.game import GameBoard
from esoth.pandemic_cthulhu.decks import *
from esoth.pandemic_cthulhu.printer import print_elder_map


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
    game.play()
