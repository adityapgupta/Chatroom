import socket
import threading

host = '127.0.0.1'
port = 4455

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print(f'Listening for connections on {host}:{port}...\n')
print(f'Listening for connections on {host}:{port}...\n', file=open("logs.txt", 'a'))
client_dict = {}
server_password = "password"

class ClientManager:
    def __init__(self, client):
        self.client = client
        self.nickname = client_dict[client]

    def exit_client(self):
        client_dict.pop(self.client)
        self.client.close()

    def left(self):
        ClientManager(self.client).exit_client()
        broadcast('\n{} left!\n'.format(self.nickname), None)

    def kick(self):
        ClientManager(self.client).exit_client()
        broadcast('\n{} was kicked!\n'.format(self.nickname), None)


def broadcast(message, sender):
    print(message)
    print(message, file=open("logs.txt", 'a'))
    for client in client_dict.keys():
        if client == sender:
            continue
        client.send(message.encode('ascii'))


def dm_send(message, receiver):
    print(message)
    print(message, file=open("logs.txt", 'a'))
    for client in client_dict.keys():
        if client_dict[client] == receiver:
            client.send(message.encode('ascii'))


# noinspection PyBroadException
def server_commands():
    while True:
        value = input("")

        if value[0:5] == "kick ":
            kicked = value[5:]
            kicking = False

            for client in client_dict.keys():
                if client_dict[client] == kicked:
                    ClientManager(client).kick()
                    kicking = True

            if not kicking:
                print(f"There is no member named {kicked} in the chatroom\n")

        if value == "members":
            if len(client_dict) > 0:
                current_members = " ".join(client for client in client_dict.values())
                print(current_members,"\n")
            else:
                print("The chatroom is empty")

        if value[0:10] == "@everyone ":
            message = value[10:]
            broadcast("\nServer: " + message + "\n", None)

        if value[0:1] == "@" and value[0:10] != "@everyone ":
            receiver = str(value.split()[0][1:])

            if receiver in client_dict.values():
                message = f"\nServer({receiver}): " + " ".join(word for word in value.split()[1:]) + "\n"
                dm_send(message, receiver)
            else:
                print(f"There is no member named {receiver} in the chatroom\n")


def handle(client):
    while True:
        # noinspection PyBroadException
        try:
            message = client.recv(1024)
            decoded_message = message.decode('ascii')
            if not message:
                break

            if client not in client_dict:
                break

            final_message = "{}: {}".format(client_dict[client], decoded_message)
            print(final_message, file=open("logs.txt", 'a'))
            broadcast(final_message, client)

        except:
            break

    if client in client_dict:
        ClientManager(client).left()

    # if list(client_dict.keys()).index(client) == 0:
    #     if decoded_message[:6] == "!kick ":
    #         kicked_nickname = decoded_message[6:]
    #         kicked_index = list(client_dict.values()).index(kicked_nickname)
    #         kicked_client = list(client_dict.keys())[kicked_index]
    #         Remove(kicked_client).kick()
    #         break

    # if keyboard.is_pressed('enter'):
    #     server_input = input("")
    #     if server_input[:6] == "@kick":
    #         kicked_nickname = server_input[6:]
    #         try:
    #             kicked_index = nicknames.index(kicked_nickname)
    #             kicked_client = clients[kicked_index]
    #             Remove(kicked_client).kick()
    #             break
    #         except kicked_nickname not in nicknames:
    #             print("No user named {} is in the server".format(kicked_nickname))


def receive():
    while True:
        client, address = server.accept()
        print("Connection requested by {}".format(str(address)))
        print("Connection requested by {}".format(str(address)), file=open("logs.txt", 'a'))

        client.send("Password".encode('ascii'))
        password = client.recv(1024).decode('ascii')

        if password == server_password:
            client.send("Nickname".encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            client_dict[client] = nickname

            client.send('Connected to server!\n'.encode('ascii'))
            broadcast("\n{} joined!\n".format(client_dict[client]), client)

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        else:
            client.send("Entry denied".encode('ascii'))
            break


threading.Thread(target=receive).start()
threading.Thread(target=server_commands).start()
