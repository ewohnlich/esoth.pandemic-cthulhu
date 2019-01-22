from game import GameBoard
from printer import print_player_hands

if __name__ == '__main__':
    game = GameBoard()
    game.initialize()
    print(print_player_hands(game))
