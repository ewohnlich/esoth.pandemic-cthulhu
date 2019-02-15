import sys

from .game import GameBoard


def main():
    game = GameBoard()
    game.play()


if __name__ == "__main__":
    sys.exit(main())
