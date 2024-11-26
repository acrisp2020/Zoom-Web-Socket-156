from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'your_secret_key'

# SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SocketIO with gevent
socketio = SocketIO(app, async_mode='gevent')
db = SQLAlchemy(app)

# Model for storing users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

# Model for storing messages
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('user.username'), nullable=False)

#----------------Routes----------------------------------------------------------
# Index file route
@app.route('/')
def index():
    return render_template('index.html')

# Route to display all users
@app.route('/users')
def display_users():
    users = User.query.all()
    return jsonify([user.username for user in users])

# Route to display all messages
@app.route('/messages')
def display_messages():
    messages = Message.query.all()
    return jsonify([{'username': message.username, 'content': message.content} for message in messages])
#----------------Routes----------------------------------------------------------


#------------------Websocket Events----------------------------------------------
# WebSocket event for new users
active_users = []
@socketio.on('new_connection')
def handle_new_connection(data):
    username = data.get('username')

    user = User.query.filter_by(username=username).first()
    if not user:
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()

    if username in active_users:
        emit('username_taken', {'error': 'Username taken'})
    
    else:
        active_users.append(username)
        emit('user_connected', {'username': username}, broadcast=True)
        emit('update_user_list', active_users, broadcast=True)

# WebSocket event for message broadcasting
@socketio.on('send_message')
def handle_send_message(data):
    message_content = data.get('message')
    username = data.get('username')
    
    # Save messages in the database
    new_message = Message(content=message_content, username=username)
    db.session.add(new_message)
    db.session.commit()
    emit('receive_message', {'message': message_content, 'username': username}, broadcast=True)

#Websocket event for user disconnect
@socketio.on('disconnect')
def handle_disconnect():
    username = None
    if username in active_users:
        active_users.remove(username)
        emit('update_user_list', active_users, broadcast=True)
#------------------Websocket Events----------------------------------------------

# Run the Flask-SocketIO server
if __name__ == '__main__':
    with app.app_context(): 
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
