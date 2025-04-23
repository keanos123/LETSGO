from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, cors_allowed_origins="*")

CLIENTS = set()

@app.route('/')
def index():
    return render_template('index.html')

# Static HLS files (served by nginx normally, but fallback)
@app.route('/hls/<path:filename>')
def hls_files(filename):
    hls_dir = '/var/www/hls'
    return send_from_directory(hls_dir, filename)

@socketio.on('connect')
def handle_connect():
    # Distinguish control panel vs streamer by query param role
    role = flask.request.args.get('role')
    if role == 'client':
        CLIENTS.add(request.sid)
        print('Streamer connected')
    emit('status', {'msg': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    CLIENTS.discard(request.sid)

@socketio.on('command')
def handle_command(data):
    # Relay command to all client streamers
    print('Command received', data)
    for cid in CLIENTS:
        emit('command', data, room=cid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
