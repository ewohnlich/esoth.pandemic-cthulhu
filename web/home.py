#!/usr/bin/env python
from threading import Lock
from io import StringIO
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from esoth.pandemic_cthulhu.game import GameBoard, Player
from esoth.pandemic_cthulhu.printer import get_elder_map

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()



def background_thread():
    """Example of how to send server generated events to clients."""
    return
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='')


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('join', namespace='')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    if message['room'] not in session['games']:
        game = GameBoard(2, stream=StringIO())
        session['games'][message['room']] = game
        game._setup()
    game_map = get_elder_map(session['games'][message['room']], html=True)
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'map': game_map,
          'count': session['receive_count']})


@socketio.on('leave', namespace='')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room', namespace='')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('get_roles', namespace='')
def get_roles(message):
    if message.get('room') and message['room'] in games:
        game = session['games'][message['room']]
        roles = game.rm.active_roles
        emit('my_response', {'data': 'Roles available: ' + ', '.join(roles),
                             'count': session['receive_count']},
             room=message['room'])


@socketio.on('assign_role', namespace='')
def assign_role(message):
    game = session['games'][message['room']]
    role = message['data']
    player = Player(game)
    game.rm.assign_role(player, role)


@socketio.on('my_room_event', namespace='')
def send_room_message(message):
    if message['room']:
        game = session['games'][message['room']]
        game.send_message(message['room'])
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('disconnect_request', namespace='')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
