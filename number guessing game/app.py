from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import eventlet
eventlet.monkey_patch()

import random

app = Flask(__name__)
socketio = SocketIO(app)

number_to_guess = random.randint(1, 100)
guesses = {}
game_over = False

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('guess')
def handle_guess(data):
    global game_over
    if game_over:
        emit('result', {'message': 'Game over! Click restart to play again.'})
        return

    name = data.get('name')
    guess = int(data.get('number'))

    guesses[name] = guesses.get(name, 0) + 1

    if guess < number_to_guess:
        emit('result', {'message': f'{name} guessed {guess} — Too low!'})
    elif guess > number_to_guess:
        emit('result', {'message': f'{name} guessed {guess} — Too high!'})
    else:
        game_over = True
        emit('result', {
            'message': f'🎉 {name} guessed it right! The number was {guess} 🎉',
            'scoreboard': guesses,
            'gameover': True
        }, broadcast=True)

@socketio.on('restart')
def handle_restart():
    global number_to_guess, guesses, game_over
    number_to_guess = random.randint(1, 100)
    guesses = {}
    game_over = False
    emit('result', {'message': '🔄 Game restarted! Start guessing again.', 'scoreboard': {}}, broadcast=True)

@socketio.on('chat')
def handle_chat(data):
    emit('chat', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)


