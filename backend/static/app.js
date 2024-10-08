const socket = io.connect('http://172.16.129.41:5000');

//prompts user for a username
let username = prompt("Enter Username:");

//notifies server of new connection
socket.emit('new_connection', {username:username});

//function to send messages
function sendMessage() {
    const inputElement = document.getElementById('message-input');
    const message = inputElement.value;

    if (message) {
        socket.emit('send_message', { message: message, username:username });
        inputElement.value = '';  // Clear the input field
    }
}

//handle 'user_connected' events
socket.on('user_connected', function(data){
    const chatBox = document.getElementById('chat-box');
    const userElement = document.createElement('p');

    userElement.innerText = `${data.username} has entered the chat.`;

    chatBox.appendChild(userElement);
});

//listen for messages from the server
socket.on('receive_message', function(data) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('p');

    messageElement.innerText = `${data.username}: ${data.message}`;

    // Append the message to the chat box
    chatBox.appendChild(messageElement);
});

//username taken event
socket.on('username_taken', function(data){
    alert(data.error);
    username = prompt("Username Taken, try again");
    socket.emit('new_connection',{username:username});
});

//handle 'update_user_list'
socket.on('update_user_list', function(users){
    const userList = document.getElementById('user-list');
    userList.innerHTML = '<h2>Users</h2>';

    users.forEach(function(user){
        const userElement = document.createElement('p');
        userElement.innerText = user;
        userList.appendChild(userElement);
    });
});





