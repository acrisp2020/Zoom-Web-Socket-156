from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize SocketIO with gevent
socketio = SocketIO(app, async_mode='gevent')

# In-memory storage for users and messages
active_users = []
messages = []

#----------------Routes----------------------------------------------------------
# Index file route
@app.route('/')
def index():
    return render_template('index.html')

# Route to display all users
@app.route('/users')
def display_users():
    return jsonify(active_users)

# Route to display all messages
@app.route('/messages')
def display_messages():
    return jsonify(messages)
#----------------Routes----------------------------------------------------------


#------------------Websocket Events----------------------------------------------
# WebSocket event for new users
@socketio.on('new_connection')
def handle_new_connection(data):
    username = data.get('username')
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

    # Save messages in transient memory
    messages.append({'username': username, 'message': message_content})
    emit('receive_message', {'message': message_content, 'username': username}, broadcast=True)

# WebSocket event for user disconnect
@socketio.on('disconnect')
def handle_disconnect():
    # No username passed, simulate disconnection for transient memory
    global active_users
    active_users = [u for u in active_users if u not in active_users]
    emit('update_user_list', active_users, broadcast=True)
#------------------Websocket Events----------------------------------------------

# Run the Flask-SocketIO server
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
