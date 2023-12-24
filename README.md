# Chatroom
A simple client server model to host a chatroom for multiple people. Use the server file to host a room on which people can join by using the client file. There is no limit on the number of clients.

## Sockets chatroom
A chatroom hosted for clients connected on the same local network. It uses the sockets module to make a connection.

## Email chatroom
A chatroom which can be used to connect people all across the globe. It uses gmail to send and receive messages, so a gmail account is required for the server and every client.

To join the chatroom, a password is required which can be set by the server. The server can be used to send a message to all members and kick a member from the chatroom.
The email chatroom also allows the users to send private messages to another member in the chatroom.
