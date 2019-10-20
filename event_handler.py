from app import app, db, UserModel
from flask_login import current_user
from flask_socketio import SocketIO

socket = SocketIO(app)

@socket.on('message')
def handle_message(message):
    print('received message: ' + message)

@socket.on('connect')
def on_connect():
    if current_user.is_authenticated:
        user = db.session.query(UserModel).filter_by(id=current_user.id).first()
        user.is_online = True
        db.session.commit()
    #print('my response', {'data': 'Connected'})

@socket.on('disconnect')
def on_disconnect():
    if current_user.is_authenticated:
        user = db.session.query(UserModel).filter_by(id=current_user.id).first()
        user.is_online = False
        db.session.commit()
    #print('my response', {'data': 'Disconnected'})