import socket
import threading

nickname = input("Choose your nickname: ")
host = '3.138.180.119'
port = 17249

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')

            if message == "Password":
                password = input("Enter password: ")
                client.send(password.encode('ascii'))

            if message == "Nickname":
                client.send(nickname.encode('ascii'))
                write_thread.start()

            if message == "Entry denied":
                print("Password incorrect")
                break

            elif len(message) != 0 and message != "Password" and message != "Nickname":
                print(message)

        except:
            print("An error occurred")
            client.close()
            break

def write():
    while True:
        message = input("")
        client.send(message.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
