from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from flask_socketio import SocketIO, emit, send
import uuid

from esoth.pandemic_cthulhu.game import GameBoard

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

games = {}


@app.route("/")
def runner():
    return render_template('home.html')


@socketio.on('get_game')
def get_game(data):
    if data.get('gameid') in games:
        game = games[data['gameid']]
        print('existing game: ' + str(game.id))
    else:
        game = GameBoard(num_players=data.get('num_players'))
        game.id = uuid.uuid4().hex
        print('new game: ' + str(game.id))
    games[game.id] = game
    emit('game id: {}'.format(game.id), broadcast=True)
