import base64
import smtplib
import threading
from email.message import EmailMessage
from imap_tools import MailBox, AND

client_dict = {}
server_gmail = "server@gmail.com"
server_password = "serverpassword"
server_security = "chatroompassword"


class ClientManager:
    def __init__(self, client):
        self.client = client
        self.gmail = client_dict[client]

    def left(self):
        broadcast(f'{self.client} left!', f'{self.client} left!', self.gmail)
        client_dict.pop(self.client)

    def kick(self):
        broadcast(f'{self.client} was kicked!', f'{self.client} was kicked!', self.gmail)
        send("You were kicked from the chatroom", "", self.gmail, "Kicked")
        client_dict.pop(self.client)


def encoder(string):
    ascii_bytes = string.encode('ascii')
    base64_bytes = base64.b64encode(ascii_bytes)
    base64_string = base64_bytes.decode('ascii')

    return base64_string


def decoder(string):
    base64_bytes = string.encode('ascii')
    ascii_bytes = base64.b64decode(base64_bytes)
    ascii_string = ascii_bytes.decode('ascii')

    return ascii_string


def send(message, print_message, client, subject):
    print(print_message)
    print(print_message, file=open("logs.txt", 'a'))
    mail = EmailMessage()
    mail["from"] = server_gmail
    mail["to"] = client
    mail["subject"] = encoder(subject)

    mail.set_content(encoder(message))

    with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(server_gmail, server_password)
        smtp.send_message(mail)


def broadcast(message, print_message, sender):
    print(print_message)
    print(print_message, file=open("logs.txt", 'a'))
    try:
        mail = EmailMessage()
        mail["from"] = server_gmail
        mail["to"] = ",".join(str(client) for client in client_dict.values() if client != sender)
        mail["subject"] = encoder("Chatroom server")

        mail.set_content(encoder(message))

        with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(server_gmail, server_password)
            smtp.send_message(mail)

    except:
        pass


def server_commands():
    while True:
        value = input("")
        if value[0:5] == "kick ":
            kicked_client = value[5:]
            if kicked_client in client_dict.keys():
                ClientManager(kicked_client).kick()
            else:
                print(f"There is no member named {kicked_client} in the chatroom")

        if value[0:6] == "Image ":
            image_client = value[6:]
            if image_client in client_dict.keys():
                send("", "", client_dict[image_client], "Image")
            else:
                print(f"There is no member named {image_client} in the chatroom")

        if value == "members":
            current_members = " ".join(client for client in client_dict.keys())
            print(current_members)

        if value[0:10] == "@everyone ":
            message = value[10:]
            broadcast("Server: " + message, "Server: " + message, "")

        if value[0:1] == "@" and value[0:10] != "@everyone ":
            receiver = str(value.split()[0][1:])
            if receiver in client_dict.keys():
                message = "Server(dm): " + " ".join(word for word in value.split()[1:])
                print_message = f"Server({value.split()[0]}): " + " ".join(word for word in value.split()[1:])
                send(message, print_message, client_dict[receiver], "Server dm")
            else:
                print(f"There is no member named {receiver} in the chatroom")

        else:
            print("Please enter a valid command")


def server_main():
    while True:
        try:
            sender_gmail = ""
            sender = ""
            text = ""
            sub = ""
            with MailBox('imap.gmail.com').login(server_gmail, server_password, 'INBOX') as mailbox:
                for msg in mailbox.fetch(AND(seen=False)):
                    sender_gmail = msg.from_

                    for k, v in client_dict.items():
                        if v == sender_gmail:
                            sender = k

                    text = decoder(msg.text)
                    sub = decoder(msg.subject)

            if sub == "Join request":
                if sender_gmail in client_dict.values():
                    send("Someone has already entered the room with this gmail",
                         f"Connection declined to {sender_gmail}", sender_gmail, "Chatroom denied entry")
                elif text in client_dict.keys():
                    send("Someone already has the same username", f"Connection declined to {sender_gmail}",
                         sender_gmail, "Chatroom denied entry")
                else:
                    send("Enter password", f"Connection requested by {sender_gmail} as {text}", sender_gmail,
                         "Chatroom Security")

            if sub == "Join password":
                text_words = text.split(" @")
                sender_name = text_words[1]
                if text_words[0] == server_security:
                    current_members = " ".join(client for client in client_dict.keys())
                    broadcast("\n{} joined\n".format(sender_name), "", sender_gmail)
                    send(f"\nSuccessfully joined as {sender_name} \nCurrent members: {current_members}\n",
                         f"{sender_gmail} joined as {sender_name}", sender_gmail, "Chatroom join")
                    client_dict[sender_name] = sender_gmail

                else:
                    send("Incorrect password", f"{sender_gmail} failed to join as {sender_name}",
                         sender_gmail, "Chatroom denied entry")

            if sub == "Chatroom group":
                final_message = "{0}: {1}".format(sender, text)
                broadcast(final_message, final_message, sender_gmail)

            if sub == "Chatroom dm":
                dm_words = text.split()
                dm_receiver = dm_words[0]
                dm_text = ' '.join(words for words in dm_words[1:])
                dm_message = "{0} (dm): {1}".format(sender, dm_text)
                send(dm_message, dm_message, client_dict[dm_receiver], "Member dm")

            if sub == "Chatroom leave":
                ClientManager(sender).left()

        except ValueError:
            pass


threading.Thread(target=server_main).start()
threading.Thread(target=server_commands).start()
